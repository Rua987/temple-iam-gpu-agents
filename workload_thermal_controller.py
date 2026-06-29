"""Coordonne Afterburner et le cap pilote nvidia-smi selon le workload."""

from __future__ import annotations

import logging
from typing import Dict, Optional

from afterburner_profile_controller import AfterburnerProfileController
from gpu_real_controller import GPUControlCapability, GPURealController


class WorkloadThermalController:
    """Applique heavy_cool (Profile2 + cap 900 MHz) ou relache au repos."""

    def __init__(
        self,
        afterburner: Optional[AfterburnerProfileController] = None,
        gpu_controller: Optional[GPURealController] = None,
        dry_run: bool = False,
        gpu_index: int = 0,
    ):
        # dry_run: propage la simulation aux deux actuateurs (clocks + Afterburner).
        # gpu_index: carte ciblee (multi-GPU), passe au controleur clocks.
        self.dry_run = dry_run
        self.afterburner = afterburner or AfterburnerProfileController(dry_run=dry_run)
        self.gpu_controller = gpu_controller or GPURealController(dry_run=dry_run, gpu_index=gpu_index)
        self.current_mode: Optional[str] = None
        self.current_ai_profile: Optional[str] = None
        # Override thermique pilote par le scorer (emergency_throttle/thermal_focus).
        # Quand actif, il prime sur le mode workload et n'est PAS relache par les
        # bascules de process principal (Edge/Ollama qui clignotent).
        self.emergency_active = False
        self.emergency_profile: Optional[str] = None
        # Controle fin (sweet spot): cap clock continu en regime normal, distinct
        # du frein d'urgence. None = pas de controle fin actif.
        self.fine_control_clock: Optional[int] = None

    AI_PROFILES = frozenset({"ai_soft", "ai_throttle", "ai_brake"})

    # Strategie du scorer -> profil de frein reel a appliquer.
    STRATEGY_CAPS = {
        "emergency_throttle": "heavy_cool",  # 900 MHz - frein dur
        "thermal_focus": "critical",         # 1200 MHz - refroidissement
    }

    def apply_thermal_strategy(self, strategy: str, temp_c: float, target_temp: float) -> Optional[str]:
        """Relie la decision du scorer a une action GPU concrete.

        - emergency_throttle / thermal_focus (ou temp >> cible) -> applique un cap
          de frein immediat, quel que soit le workload courant.
        - temp revenue nettement sous la cible -> relache l'override.
        Retourne le profil applique, 'released', ou None si rien a faire.
        """
        if self.gpu_controller.capabilities == GPUControlCapability.READ_ONLY:
            return None

        wanted = self.STRATEGY_CAPS.get(strategy)
        # Filet de securite: meme si le scorer dit 'balanced', une temp trop haute
        # au-dessus de la cible force le frein dur.
        if wanted is None and temp_c >= target_temp + 5:
            wanted = "heavy_cool"

        if wanted:
            if self.gpu_controller.current_profile != wanted:
                self.gpu_controller.apply_profile(wanted)
                logging.warning(
                    "URGENCE thermique %sC (cible %sC, %s) -> cap %s force",
                    int(temp_c), int(target_temp), strategy, wanted,
                )
            self.emergency_active = True
            self.emergency_profile = wanted
            self.fine_control_clock = None  # l'urgence prime sur le controle fin
            return wanted

        # Plus de demande de frein: relache si la temp est bien retombee.
        if self.emergency_active and temp_c <= target_temp - 3:
            self.emergency_active = False
            self.emergency_profile = None
            self.gpu_controller.reset_gpu_clocks()
            # Re-applique le mode workload normal (ex: heavy_cool gaming).
            self.current_mode = None
            logging.info("Fin urgence thermique (%sC <= cible %sC)", int(temp_c), int(target_temp))
            return "released"
        return None

    def apply_target_clock(self, max_clock: int, reason: str = "") -> bool:
        """Controle FIN (sweet spot): verrouille le clock max a une cible continue.

        Distinct du frein d'urgence: sert a converger vers le clock optimal
        perf/qualite en regime normal (pas de surchauffe). Ne fait rien si une
        urgence thermique est active (elle prime).
        """
        if self.emergency_active:
            return False
        if self.gpu_controller.capabilities == GPUControlCapability.READ_ONLY:
            return False
        max_clock = int(max_clock)
        if self.fine_control_clock == max_clock and self.gpu_controller.is_clock_locked:
            return True  # deja a la cible, rien a faire
        ok = self.gpu_controller.lock_gpu_clocks(300, max_clock)
        if ok:
            self.fine_control_clock = max_clock
            logging.info("Controle fin (sweet spot): cap %d MHz%s",
                         max_clock, f" - {reason}" if reason else "")
        return ok

    def resolve_mode(self, optimization_profile: Optional[Dict]) -> str:
        if not optimization_profile:
            return "stock"

        category = optimization_profile.get("category", "gaming")
        mode = optimization_profile.get("optimization_mode", "active")

        if category == "browser_webview" or mode == "observe_only":
            return "stock"
        if category in {"gaming", "unknown_gpu_app"}:
            return "heavy_cool"
        if category == "local_ai":
            return "efficient_only"
        return "stock"

    def adjust_for_temperature(self, temp_c: float, optimization_profile: Optional[Dict]) -> Optional[str]:
        """Echelle ai_soft/ai_throttle/ai_brake pour local_ai au-dessus de target_temp."""
        if self.current_mode != "efficient_only":
            return None
        if self.gpu_controller.capabilities == GPUControlCapability.READ_ONLY:
            return None

        temp = int(temp_c)
        target = int((optimization_profile or {}).get("target_temp", 70))

        if temp >= target + 18:
            profile = "ai_brake"
        elif temp >= target + 8:
            profile = "ai_throttle"
        elif temp >= target + 2:
            profile = "ai_soft"
        else:
            if self.gpu_controller.current_profile in self.AI_PROFILES:
                self.gpu_controller.reset_gpu_clocks()
            self.current_ai_profile = None
            return "none"

        if self.gpu_controller.current_profile != profile:
            self.gpu_controller.apply_profile(profile)
            logging.info(
                "local_ai thermique: %sC (cible %sC) -> %s",
                temp,
                target,
                profile,
            )
        self.current_ai_profile = profile
        return profile

    def apply_for_workload(self, optimization_profile: Optional[Dict]) -> bool:
        target_mode = self.resolve_mode(optimization_profile)
        # Pendant une urgence thermique, on ne relache PAS le frein meme si un
        # process "stock" (Edge/Ollama) devient brievement principal.
        if self.emergency_active and target_mode == "stock":
            return True
        if target_mode == self.current_mode:
            return True

        if target_mode == "stock":
            ok = self._release()
        elif target_mode == "heavy_cool":
            ok = self._apply_heavy_cool()
        else:
            ok = self._apply_efficient_only()

        if ok:
            self.current_mode = target_mode
        return ok

    def release(self) -> bool:
        ok = self._release()
        if ok:
            self.current_mode = "stock"
            self.current_ai_profile = None
        return ok

    def _apply_heavy_cool(self) -> bool:
        afterburner_ok = self.afterburner.apply_profile("efficient")
        clock_ok = self._apply_driver_cap()
        if afterburner_ok or clock_ok:
            logging.info("Profil heavy_cool actif: Afterburner efficient + cap 900 MHz")
            return True
        logging.warning("heavy_cool non applique (Afterburner et cap pilote indisponibles)")
        return False

    def _apply_efficient_only(self) -> bool:
        self._reset_driver_cap()
        afterburner_ok = self.afterburner.apply_profile("efficient")
        if afterburner_ok:
            logging.info("Profil efficient_only actif: Afterburner efficient, pas de cap 900 MHz")
            return True
        logging.warning("efficient_only non applique")
        return False

    def _release(self) -> bool:
        self.fine_control_clock = None  # plus de controle fin au repos
        afterburner_ok = self.afterburner.apply_profile("stock")
        clock_ok = self._reset_driver_cap()
        if afterburner_ok or clock_ok:
            logging.info("Profil thermique relache: stock + reset clocks")
            return True
        return False

    def _apply_driver_cap(self) -> bool:
        if self.gpu_controller.capabilities == GPUControlCapability.READ_ONLY:
            return False
        return self.gpu_controller.apply_profile("heavy_cool")

    def _reset_driver_cap(self) -> bool:
        if not self.gpu_controller.is_clock_locked:
            return True
        if self.gpu_controller.capabilities == GPUControlCapability.READ_ONLY:
            return False
        return self.gpu_controller.reset_gpu_clocks()

    def get_display_status(self) -> Dict[str, str]:
        """Resume lisible pour le dashboard du monitor."""
        mode = self.current_mode or "stock"
        mode_labels = {
            "stock": "Stock (repos)",
            "heavy_cool": "Heavy cool — Afterburner P2 + cap 900 MHz",
            "efficient_only": "Efficient — Afterburner P2, echelle IA si chaud",
        }
        ai_labels = {
            "ai_soft": "ai_soft — cap 750 MHz",
            "ai_throttle": "ai_throttle — cap 600 MHz",
            "ai_brake": "ai_brake — cap 450 MHz",
            "none": "Aucun cap pilote (temp OK)",
        }

        afterburner = self.afterburner.current_profile or "non applique"
        driver_cap = "non verrouille"
        if self.gpu_controller.is_clock_locked and self.gpu_controller.current_profile:
            driver_cap = self.gpu_controller.current_profile
        elif self.fine_control_clock and self.gpu_controller.is_clock_locked:
            driver_cap = f"{self.fine_control_clock} MHz (fin)"

        ai_step = self.current_ai_profile or "none"
        if self.emergency_active:
            active = f"🚨 URGENCE thermique — frein {self.emergency_profile} force"
        elif self.fine_control_clock:
            active = f"🎚️ Controle fin (sweet spot) — cap {self.fine_control_clock} MHz"
        elif mode == "heavy_cool":
            active = mode_labels["heavy_cool"]
        elif mode == "efficient_only" and ai_step in self.AI_PROFILES:
            active = ai_labels.get(ai_step, ai_step)
        elif mode == "efficient_only":
            active = mode_labels["efficient_only"]
        else:
            active = mode_labels["stock"]

        return {
            "workload_mode": mode_labels.get(mode, mode),
            "active_action": active,
            "afterburner_profile": afterburner,
            "driver_cap": driver_cap,
            "ai_ladder": ai_labels.get(ai_step, ai_step),
            "clock_locked": "oui" if self.gpu_controller.is_clock_locked else "non",
        }
