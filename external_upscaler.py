"""Orchestration d'un upscaler EXTERNE (Lossless Scaling / Magpie).

Pourquoi externe: l'agent ne peut PAS reconstruire DLSS de l'exterieur (il n'a
pas acces aux motion vectors ni au depth buffer du moteur de rendu - cf.
discussion). Le plus proche faisable, c'est ORCHESTRER l'outil tiers qui upscale
la fenetre du jeu (Lossless Scaling, Magpie). L'agent ne fait que:
  - detecter si un tel outil est installe,
  - le LANCER quand un jeu est actif (il devient pret a l'emploi),
  - l'ARRETER quand on n'est plus en jeu (libere les ressources, ex: training).

Note d'honnetete: lancer l'exe rend l'outil DISPONIBLE. Le declenchement du
scaling lui-meme reste un raccourci clavier propre a l'outil (Magpie: Win+Shift+A
par defaut; Lossless Scaling: bouton/raccourci "Scale"). L'agent prepare l'outil
au bon moment, il ne presse pas la touche a ta place.
"""

import os
import subprocess
import logging
from typing import Optional, List


class ExternalUpscaler:
    """Lance/arrete un upscaler externe selon le workload (gaming uniquement)."""

    # Emplacements courants des executables.
    CANDIDATES: List[str] = [
        r"C:\Program Files (x86)\Steam\steamapps\common\Lossless Scaling\LosslessScaling.exe",
        r"C:\Program Files\Magpie\Magpie.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Magpie\Magpie.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Lossless Scaling\LosslessScaling.exe"),
    ]

    def __init__(self, exe_path: Optional[str] = None, dry_run: bool = False):
        self.exe_path = exe_path or self._find_exe()
        self.process: Optional[subprocess.Popen] = None
        self.dry_run = dry_run  # simulation: ne lance pas reellement l'upscaler

    def _find_exe(self) -> Optional[str]:
        for p in self.CANDIDATES:
            try:
                if p and os.path.isfile(p):
                    return p
            except Exception:
                continue
        return None

    @property
    def available(self) -> bool:
        """True si un upscaler externe est installe et localise."""
        return self.exe_path is not None

    @property
    def running(self) -> bool:
        """True si l'instance lancee PAR l'agent tourne encore."""
        return self.process is not None and self.process.poll() is None

    @property
    def name(self) -> str:
        return os.path.basename(self.exe_path) if self.exe_path else "aucun"

    def start(self) -> bool:
        """Lance l'upscaler s'il est dispo et pas deja lance par nous."""
        if not self.available or self.running:
            return self.running
        if self.dry_run:
            logging.info("[DRY-RUN] lancerait l'upscaler externe: %s", self.name)
            return False
        try:
            self.process = subprocess.Popen([self.exe_path])
            logging.info("Upscaler externe lance: %s", self.name)
            return True
        except Exception as e:
            logging.error("Echec lancement upscaler externe: %s", e)
            self.process = None
            return False

    def stop(self) -> bool:
        """Arrete l'instance que NOUS avons lancee (jamais celle de l'user)."""
        if not self.running:
            self.process = None
            return True
        try:
            self.process.terminate()
            logging.info("Upscaler externe arrete: %s", self.name)
        except Exception as e:
            logging.error("Echec arret upscaler externe: %s", e)
            return False
        finally:
            self.process = None
        return True

    def status_line(self) -> str:
        """Resume court pour le dashboard."""
        if not self.available:
            return "aucun upscaler externe installe (Lossless Scaling / Magpie)"
        if self.running:
            return f"{self.name} PRET (active le scaling via son raccourci)"
        return f"{self.name} dispo (sera lance en jeu)"
