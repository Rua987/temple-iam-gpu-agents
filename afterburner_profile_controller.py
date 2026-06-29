"""Pont minimal entre l'agent et MSI Afterburner.

Le controle reel reste dans Afterburner : l'agent ne dessine pas de courbe
undervolt, il bascule seulement entre des profils deja sauvegardes.
"""

from __future__ import annotations

import logging
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


DEFAULT_AFTERBURNER_EXE = Path(r"C:\Program Files (x86)\MSI Afterburner\MSIAfterburner.exe")
DEFAULT_PROFILES_DIR = Path(r"C:\Program Files (x86)\MSI Afterburner\Profiles")


@dataclass(frozen=True)
class AfterburnerProfile:
    name: str
    slot: int
    description: str


class AfterburnerProfileController:
    """Applique des profils Afterburner via `MSIAfterburner.exe -profileN`.

    Securite volontaire : si le slot n'a pas ete sauvegarde dans Afterburner,
    on refuse de l'appliquer. Sinon l'agent pourrait afficher "undervolt actif"
    alors qu'il ne charge rien de reel.
    """

    PROFILES: Dict[str, AfterburnerProfile] = {
        "stock": AfterburnerProfile("stock", 1, "profil stock/secours"),
        "efficient": AfterburnerProfile("efficient", 2, "profil undervolt efficace"),
    }

    def __init__(
        self,
        afterburner_exe: Path = DEFAULT_AFTERBURNER_EXE,
        profiles_dir: Path = DEFAULT_PROFILES_DIR,
        enabled: Optional[bool] = None,
        dry_run: Optional[bool] = None,
    ):
        self.afterburner_exe = Path(afterburner_exe)
        self.profiles_dir = Path(profiles_dir)
        self.enabled = self.afterburner_exe.exists() if enabled is None else enabled
        self.dry_run = os.getenv("TEMPLE_IAM_AFTERBURNER_DRY_RUN", "0") == "1" if dry_run is None else dry_run
        self.current_profile: Optional[str] = None

    def choose_profile(self, optimization_profile: Optional[Dict]) -> str:
        if not optimization_profile:
            return "stock"

        category = optimization_profile.get("category", "gaming")
        mode = optimization_profile.get("optimization_mode", "active")

        if category == "browser_webview" or mode == "observe_only":
            return "stock"
        if category in {"gaming", "local_ai", "unknown_gpu_app"}:
            return "efficient"
        return "stock"

    def apply_for_workload(self, optimization_profile: Optional[Dict]) -> bool:
        return self.apply_profile(self.choose_profile(optimization_profile))

    def apply_profile(self, profile_name: str) -> bool:
        if not self.enabled:
            logging.info("MSI Afterburner absent/desactive - profil ignore")
            return False

        profile = self.PROFILES.get(profile_name)
        if not profile:
            logging.warning("Profil Afterburner inconnu: %s", profile_name)
            return False

        if self.current_profile == profile.name:
            return True

        if not self._profile_slot_exists(profile.slot):
            logging.warning(
                "Profil Afterburner %s (slot %d) non sauvegarde - action ignoree",
                profile.name,
                profile.slot,
            )
            return False

        cmd = [str(self.afterburner_exe), f"-profile{profile.slot}"]
        if self.dry_run:
            logging.info("DRY-RUN Afterburner: %s", " ".join(cmd))
        else:
            subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        self.current_profile = profile.name
        logging.info("Profil Afterburner applique: %s (%s)", profile.name, profile.description)
        return True

    def _profile_slot_exists(self, slot: int) -> bool:
        if not self.profiles_dir.exists():
            return False

        markers = (
            f"[Profile{slot}]",
            f"Profile{slot}",
            f"CoreClkBoost{slot}",
            f"MemClkBoost{slot}",
            f"VFCurve{slot}",
        )

        for profile_file in self.profiles_dir.glob("*.cfg"):
            try:
                text = profile_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if any(marker in text for marker in markers):
                return True

        return False
