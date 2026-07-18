"""Etage CPU du pilote thermique - meme philosophie que l'etage GPU.

Sur laptop, CPU et GPU partagent la meme dissipation: freiner un CPU qui cuit
libere du budget thermique pour le GPU. Le levier est natif Windows (powercfg,
"max processor state"), reversible, sans driver:

    100% = stock  ·  99% = coupe le Turbo Boost (gros gain thermique, perte
    de perf modeste)  ·  80% / 60% = freins progressifs.

Lecture de temperature: zone thermique ACPI via WMI (MSAcpi_ThermalZoneTemperature).
C'est la source native Windows; certains OEM ne l'exposent pas -> dans ce cas
l'etage CPU se declare indisponible et ne fait RIEN (pas de frein a l'aveugle).
La lecture (~400 ms) tourne dans un thread d'arriere-plan pour ne jamais
bloquer la boucle du monitor.

Securite:
- dry_run: tout est simule (aucun powercfg execute).
- release() restaure 100% ; le monitor l'appelle a l'arret. powercfg persiste
  apres la mort du process, donc la restauration est indispensable.
"""

from __future__ import annotations

import logging
import subprocess
import threading
import time
from typing import Optional


class CPUThermalController:
    """Frein thermique CPU par paliers de 'max processor state' (powercfg)."""

    # Paliers analogues aux profils GPU (heavy_cool/critical).
    LEVELS = {
        "stock": 100,      # comportement d'usine
        "no_turbo": 99,    # coupe le Turbo Boost - premier frein, quasi indolore
        "brake": 80,       # frein moyen
        "hard": 60,        # frein d'urgence
    }

    def __init__(self, dry_run: bool = False, target_temp: float = 85.0):
        self.dry_run = dry_run
        # 8750H et similaires: throttle constructeur ~95C. Cible par defaut 85C.
        self.target_temp = float(target_temp)
        self.current_level: str = "stock"
        self.available: Optional[bool] = None  # None = pas encore teste
        self._temp: Optional[float] = None
        self._temp_ts: float = 0.0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._temp_loop, daemon=True)
        self._thread.start()

    # ---------- lecture temperature (thread de fond) ----------
    def _read_temp_once(self) -> Optional[float]:
        """Zone thermique ACPI (decikelvin). ~400 ms -> jamais dans la boucle."""
        try:
            out = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command",
                 "(Get-CimInstance -Namespace root/wmi -ClassName "
                 "MSAcpi_ThermalZoneTemperature).CurrentTemperature"],
                capture_output=True, text=True, timeout=6,
            )
            values = [float(v) for v in out.stdout.split() if v.strip().replace('.', '').isdigit()]
            if not values:
                return None
            # Plusieurs zones possibles: on prend la plus chaude.
            return round(max(values) / 10.0 - 273.15, 1)
        except Exception:
            return None

    def _temp_loop(self):
        while not self._stop.is_set():
            t = self._read_temp_once()
            if t is not None and 5.0 < t < 120.0:  # filtre les lectures absurdes
                self._temp = t
                self._temp_ts = time.time()
                if self.available is None:
                    self.available = True
                    logging.info("CPU thermal: zone ACPI disponible (%.1fC)", t)
            elif self.available is None:
                self.available = False
                logging.warning("CPU thermal: temperature indisponible (OEM sans zone ACPI) - etage CPU passif")
                return  # inutile de re-essayer en boucle
            self._stop.wait(2.0)

    @property
    def temperature(self) -> Optional[float]:
        """Derniere temp lue (None si indisponible ou perimee > 15 s)."""
        if self._temp is None or (time.time() - self._temp_ts) > 15:
            return None
        return self._temp

    # ---------- actuation powercfg ----------
    def _set_max_state(self, pct: int) -> bool:
        if self.dry_run:
            logging.info("[DRY-RUN] CPU max state -> %d%%", pct)
            return True
        try:
            for flag in ("/setacvalueindex", "/setdcvalueindex"):
                subprocess.run(
                    ["powercfg", flag, "SCHEME_CURRENT", "SUB_PROCESSOR",
                     "PROCTHROTTLEMAX", str(pct)],
                    capture_output=True, text=True, timeout=6,
                )
            # Re-applique le schema pour prise d'effet immediate.
            subprocess.run(["powercfg", "/setactive", "SCHEME_CURRENT"],
                           capture_output=True, text=True, timeout=6)
            return True
        except Exception as e:
            logging.error("powercfg max state %d%%: %s", pct, e)
            return False

    def _apply_level(self, level: str, reason: str) -> None:
        if level == self.current_level:
            return
        if self._set_max_state(self.LEVELS[level]):
            logging.warning("CPU frein: %s (%d%%) - %s", level, self.LEVELS[level], reason)
            self.current_level = level

    # ---------- decision (appelee chaque tick par le monitor) ----------
    def update(self) -> str:
        """Choisit le palier selon la temp CPU, avec hysteresis anti-oscillation.

        Escalade: cible+8 -> hard ; cible+3 -> brake ; cible -> no_turbo.
        Relachement: seulement une fois bien refroidi (cible-8), et palier par
        palier - pas de yo-yo stock/frein.
        """
        temp = self.temperature
        if temp is None:
            return self.current_level  # pas de donnee -> on ne touche a rien

        t = self.target_temp
        if temp >= t + 8:
            self._apply_level("hard", f"{temp:.0f}C >= {t + 8:.0f}C")
        elif temp >= t + 3:
            if self.current_level != "hard":
                self._apply_level("brake", f"{temp:.0f}C >= {t + 3:.0f}C")
        elif temp >= t:
            if self.current_level == "stock":
                self._apply_level("no_turbo", f"{temp:.0f}C >= cible {t:.0f}C")
        elif temp <= t - 8 and self.current_level != "stock":
            self._apply_level("stock", f"{temp:.0f}C <= {t - 8:.0f}C (refroidi)")
        return self.current_level

    # ---------- cycle de vie ----------
    def release(self) -> None:
        """Restaure 100% (powercfg persiste apres la mort du process !)."""
        self._stop.set()
        if self.current_level != "stock":
            self._apply_level("stock", "arret du monitor")

    def status_line(self) -> str:
        temp = self.temperature
        temp_txt = f"{temp:.0f}°C" if temp is not None else "temp N/A"
        if self.available is False:
            return "CPU: zone thermique indisponible (etage passif)"
        labels = {
            "stock": "stock (100%)",
            "no_turbo": "sans Turbo (99%)",
            "brake": "frein 80%",
            "hard": "FREIN DUR 60%",
        }
        return f"CPU {temp_txt} · {labels[self.current_level]}"
