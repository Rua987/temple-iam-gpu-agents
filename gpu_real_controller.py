"""
GPU REAL CONTROLLER - CONTROLE GPU REEL VIA NVIDIA-SMI !
Objectif : Controle REEL du GPU, pas de simulation !

FONCTIONNALITES REELLES :
- Lock GPU Clocks : nvidia-smi -lgc (FONCTIONNE!)
- Reset GPU Clocks : nvidia-smi -rgc (FONCTIONNE!)
- Ajustement dynamique selon temperature
- Protection thermique automatique

PLUS ULTRA ! DATTEBAYO !
"""

import subprocess
import time
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GPUControlCapability(Enum):
    """Capacites de controle GPU detectees"""
    FULL = "full"           # Desktop - tout supporte
    CLOCK_ONLY = "clock"    # Laptop - seulement clocks GPU
    READ_ONLY = "readonly"  # Aucun controle


@dataclass
class GPUClockProfile:
    """Profil de clocks GPU"""
    name: str
    min_clock_mhz: int
    max_clock_mhz: int
    target_temp: int
    description: str


class GPURealController:
    """
    Controleur GPU REEL via nvidia-smi
    PAS DE SIMULATION - ACTIONS REELLES !
    """

    # Profils de clocks pre-definis pour RTX 2070
    # NOUVELLE APPROCHE PROACTIVE : Intervenir TOT pour garder GPU frais et efficace !
    CLOCK_PROFILES = {
        'performance': GPUClockProfile(
            name='Performance',
            min_clock_mhz=300,
            max_clock_mhz=2100,
            target_temp=70,
            description='Max performance, GPU frais'
        ),
        'balanced': GPUClockProfile(
            name='Balanced',
            min_clock_mhz=300,
            max_clock_mhz=1950,
            target_temp=68,
            description='Equilibre performance/temperature'
        ),
        'quiet': GPUClockProfile(
            name='Quiet',
            min_clock_mhz=300,
            max_clock_mhz=1850,
            target_temp=65,
            description='Silencieux, temperature basse'
        ),
        'power_save': GPUClockProfile(
            name='Power Save',
            min_clock_mhz=300,
            max_clock_mhz=1700,
            target_temp=62,
            description='Economie energie, clocks moderes'
        ),
        'heavy_cool': GPUClockProfile(
            name='Heavy Cool',
            min_clock_mhz=300,
            max_clock_mhz=900,
            target_temp=75,
            description='Cap 900 MHz sous charge 3D (valide FurMark laptop)'
        ),
        'emergency': GPUClockProfile(
            name='Emergency',
            min_clock_mhz=300,
            max_clock_mhz=1000,
            target_temp=55,
            description='Mode urgence thermique - throttle severe'
        ),
        'critical': GPUClockProfile(
            name='Critical',
            min_clock_mhz=300,
            max_clock_mhz=1200,
            target_temp=58,
            description='Mode critique - refroidissement rapide'
        ),
        # NOUVEAUX PROFILS PROACTIFS
        'ultra_cool': GPUClockProfile(
            name='Ultra Cool',
            min_clock_mhz=300,
            max_clock_mhz=1900,
            target_temp=65,
            description='Refroidissement agressif - jeux tres lourds'
        ),
        'esport': GPUClockProfile(
            name='eSport',
            min_clock_mhz=300,
            max_clock_mhz=2100,
            target_temp=75,
            description='Max FPS - tolere plus de chaleur'
        ),
        # PROFILS LOCAL_AI : l'inference (memory-bound) tourne a des clocks bas
        # (~855 MHz mesure sur RTX 2070 laptop). Les caps gaming (1000+) ne mordent
        # jamais ; ces profils descendent SOUS le clock d'inference reel.
        'ai_soft': GPUClockProfile(
            name='AI Soft',
            min_clock_mhz=300,
            max_clock_mhz=750,
            target_temp=74,
            description='Inference IA - throttle leger sous le clock operatoire'
        ),
        'ai_throttle': GPUClockProfile(
            name='AI Throttle',
            min_clock_mhz=300,
            max_clock_mhz=600,
            target_temp=70,
            description='Inference IA - throttle effectif (clock reduit, mesure)'
        ),
        'ai_brake': GPUClockProfile(
            name='AI Brake',
            min_clock_mhz=300,
            max_clock_mhz=450,
            target_temp=65,
            description='Inference IA - frein thermique urgence'
        )
    }

    def __init__(self, dry_run: bool = False, gpu_index: int = 0):
        # dry_run: simule les actions GPU (lock/reset clocks) sans rien actuer.
        # On garde la comptabilite (current_profile, is_clock_locked) pour que le
        # dashboard montre ce qui SERAIT applique. Sert aux tests communautaires.
        self.dry_run = dry_run
        # gpu_index: carte ciblee (multi-GPU). 0 = comportement mono-GPU teste.
        # Injecte via `-i N` dans toutes les commandes nvidia-smi.
        self.gpu_index = int(gpu_index)
        self.nvidia_smi_path = self._find_nvidia_smi()
        self.power_info = self._query_power_info()
        self.capabilities = self._detect_capabilities()
        self.current_profile: Optional[str] = None
        self.current_clock_limit: Optional[Tuple[int, int]] = None
        self.current_power_limit_w: Optional[int] = None
        self.is_clock_locked = False

        # Stats de controle
        self.control_stats = {
            'clock_changes': 0,
            'resets': 0,
            'last_action': None,
            'last_action_time': None
        }

        logging.info("GPU Real Controller initialise")
        logging.info(f"nvidia-smi: {self.nvidia_smi_path} (GPU index {self.gpu_index})")
        logging.info(f"Capacites: {self.capabilities.value}")
        if self.capabilities == GPUControlCapability.FULL and self.power_info.get('default'):
            logging.info(f"Power limit controlable (defaut {self.power_info['default']}W)")

    def _smi(self, *args) -> list:
        """Commande nvidia-smi ciblant le GPU choisi (-i index). Mono-GPU: -i 0."""
        return [self.nvidia_smi_path, '-i', str(self.gpu_index), *args]

    def _find_nvidia_smi(self) -> str:
        """Trouve le chemin de nvidia-smi"""
        paths = [
            'nvidia-smi',
            'C:\\Windows\\System32\\nvidia-smi.exe',
            'C:\\Program Files\\NVIDIA Corporation\\NVSMI\\nvidia-smi.exe'
        ]

        for path in paths:
            try:
                result = subprocess.run(
                    [path, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return path
            except:
                continue

        return 'nvidia-smi'  # Default

    def _detect_capabilities(self) -> GPUControlCapability:
        """Detecte les capacites de controle du GPU"""
        try:
            # Test lock GPU clocks
            result = subprocess.run(
                self._smi('-lgc', '300,2100'),
                capture_output=True,
                text=True,
                timeout=5
            )

            if 'not supported' in result.stdout.lower() or 'not supported' in result.stderr.lower():
                return GPUControlCapability.READ_ONLY

            # Reset immediatement
            subprocess.run(
                self._smi('-rgc'),
                capture_output=True,
                timeout=5
            )

            # Test power-limit support WITHOUT changing the effective limit:
            # probe with the GPU's own default value, so a supporting GPU just
            # re-applies its default (no-op) instead of being dropped to 100W.
            default_pl = self.power_info.get('default')
            if default_pl:
                result = subprocess.run(
                    self._smi('-pl', str(default_pl)),
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                out = (result.stdout + result.stderr).lower()
                if 'not supported' not in out and result.returncode == 0:
                    return GPUControlCapability.FULL

            return GPUControlCapability.CLOCK_ONLY

        except Exception as e:
            logging.error(f"Erreur detection capacites: {e}")
            return GPUControlCapability.READ_ONLY

    def get_gpu_metrics(self) -> Dict[str, Any]:
        """Recupere les metriques GPU actuelles"""
        try:
            result = subprocess.run(
                self._smi(
                    '--query-gpu=temperature.gpu,utilization.gpu,clocks.current.graphics,clocks.max.graphics,memory.used,memory.total,power.draw,fan.speed',
                    '--format=csv,noheader,nounits'),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                parts = result.stdout.strip().split(', ')

                def parse_value(val, val_type='int'):
                    """Parse une valeur, retourne 0 si N/A

                    Gère les formats: '90', '100 %', '1215 MHz', '5957 MiB', '81.45 W', '[N/A]'
                    """
                    val = val.strip()
                    if '[N/A]' in val or val == 'N/A' or not val:
                        return -1 if val_type == 'fan' else 0

                    # Extraire uniquement la partie numérique
                    # Supprimer les unités comme %, MHz, MiB, W
                    import re
                    match = re.search(r'([\d.]+)', val)
                    if match:
                        num_str = match.group(1)
                        try:
                            if val_type == 'float':
                                return float(num_str)
                            else:
                                return int(float(num_str))  # int(float()) pour gérer "81.45"
                        except:
                            return 0
                    return 0

                return {
                    'temperature': parse_value(parts[0]) if len(parts) > 0 else 0,
                    'utilization': parse_value(parts[1]) if len(parts) > 1 else 0,
                    'clock_current': parse_value(parts[2]) if len(parts) > 2 else 0,
                    'clock_max': parse_value(parts[3]) if len(parts) > 3 else 0,
                    'memory_used_mb': parse_value(parts[4]) if len(parts) > 4 else 0,
                    'memory_total_mb': parse_value(parts[5]) if len(parts) > 5 else 0,
                    'power_draw': parse_value(parts[6], 'float') if len(parts) > 6 else 0,
                    'fan_speed': parse_value(parts[7], 'fan') if len(parts) > 7 else -1,  # -1 = non disponible (laptop)
                    'clock_locked': self.is_clock_locked,
                    'current_profile': self.current_profile
                }
        except Exception as e:
            logging.error(f"Erreur recuperation metriques: {e}")

        return {}

    def lock_gpu_clocks(self, min_clock: int, max_clock: int) -> bool:
        """
        CONTROLE REEL : Verrouille les clocks GPU
        Utilise nvidia-smi -lgc
        """
        if self.capabilities == GPUControlCapability.READ_ONLY:
            logging.warning("Lock clocks non supporte sur ce GPU")
            return False

        if self.dry_run:
            # Simulation: on note l'intention sans toucher le GPU.
            self.is_clock_locked = True
            self.current_clock_limit = (min_clock, max_clock)
            logging.info(f"[DRY-RUN] verrouillerait les clocks: {min_clock}-{max_clock} MHz")
            return True

        try:
            cmd = self._smi('-lgc', f'{min_clock},{max_clock}')
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and 'error' not in result.stdout.lower():
                self.is_clock_locked = True
                self.current_clock_limit = (min_clock, max_clock)
                self.control_stats['clock_changes'] += 1
                self.control_stats['last_action'] = f'lock_clocks({min_clock},{max_clock})'
                self.control_stats['last_action_time'] = time.time()

                logging.info(f"GPU Clocks VERROUILLES: {min_clock}-{max_clock} MHz")
                return True
            else:
                logging.error(f"Erreur lock clocks: {result.stdout} {result.stderr}")
                return False

        except Exception as e:
            logging.error(f"Erreur lock_gpu_clocks: {e}")
            return False

    def reset_gpu_clocks(self) -> bool:
        """
        CONTROLE REEL : Reset les clocks GPU aux valeurs par defaut
        Utilise nvidia-smi -rgc
        """
        if self.capabilities == GPUControlCapability.READ_ONLY:
            logging.warning("Reset clocks non supporte sur ce GPU")
            return False

        if self.dry_run:
            self.is_clock_locked = False
            self.current_clock_limit = None
            self.current_profile = None
            logging.info("[DRY-RUN] reinitialiserait les clocks aux valeurs par defaut")
            return True

        try:
            result = subprocess.run(
                self._smi('-rgc'),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                self.is_clock_locked = False
                self.current_clock_limit = None
                self.current_profile = None
                self.control_stats['resets'] += 1
                self.control_stats['last_action'] = 'reset_clocks'
                self.control_stats['last_action_time'] = time.time()

                logging.info("GPU Clocks RESET aux valeurs par defaut")
                return True
            else:
                logging.error(f"Erreur reset clocks: {result.stdout} {result.stderr}")
                return False

        except Exception as e:
            logging.error(f"Erreur reset_gpu_clocks: {e}")
            return False

    def _query_power_info(self) -> Dict[str, Optional[int]]:
        """Lit les limites de puissance (defaut/min/max) en watts. Lecture seule.

        nvidia-smi -q -d POWER peut afficher plusieurs blocs (dont des N/A) :
        on garde la PREMIERE valeur reelle de chaque champ.
        """
        info: Dict[str, Optional[int]] = {'default': None, 'min': None, 'max': None}
        try:
            import re
            result = subprocess.run(
                self._smi('-q', '-d', 'POWER'),
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if ':' not in line:
                    continue
                key, val = line.split(':', 1)
                key, val = key.strip(), val.strip()
                m = re.search(r'([\d.]+)', val)
                if not m:
                    continue
                watts = int(float(m.group(1)))
                if key == 'Default Power Limit' and info['default'] is None:
                    info['default'] = watts
                elif key == 'Min Power Limit' and info['min'] is None:
                    info['min'] = watts
                elif key == 'Max Power Limit' and info['max'] is None:
                    info['max'] = watts
        except Exception as e:
            logging.error(f"Erreur lecture power info: {e}")
        return info

    def set_power_limit(self, watts: int) -> bool:
        """CONTROLE REEL : regle la limite de puissance (nvidia-smi -pl).

        Gate sur la capacite FULL : sur un GPU qui ne supporte pas le power
        limit (beaucoup de GeForce), on ne fait RIEN et on le dit clairement.
        """
        if self.capabilities != GPUControlCapability.FULL:
            logging.info(f"Power limit non supporte sur ce GPU (capacite: {self.capabilities.value}) - ignore")
            return False

        lo = self.power_info.get('min') or 1
        hi = self.power_info.get('max') or watts
        watts = max(lo, min(hi, int(watts)))
        try:
            result = subprocess.run(
                self._smi('-pl', str(watts)),
                capture_output=True, text=True, timeout=5
            )
            out = (result.stdout + result.stderr).lower()
            if 'not supported' in out:
                logging.info("Power limit non supporte (driver) - ignore")
                return False
            if result.returncode == 0:
                self.current_power_limit_w = watts
                self.control_stats['last_action'] = f'set_power_limit({watts}W)'
                self.control_stats['last_action_time'] = time.time()
                logging.info(f"Power limit REGLE: {watts}W")
                return True
            logging.error(f"Erreur set power limit: {result.stdout} {result.stderr}")
            return False
        except Exception as e:
            logging.error(f"Erreur set_power_limit: {e}")
            return False

    def set_power_limit_pct(self, pct: float) -> bool:
        """Regle la limite de puissance a pct (0.0-1.0) du defaut."""
        default = self.power_info.get('default')
        if not default:
            return False
        return self.set_power_limit(int(round(default * pct)))

    def reset_power_limit(self) -> bool:
        """Restaure la limite de puissance par defaut."""
        default = self.power_info.get('default')
        if default and self.capabilities == GPUControlCapability.FULL:
            return self.set_power_limit(default)
        return False

    def apply_profile(self, profile_name: str) -> bool:
        """Applique un profil de clocks pre-defini"""
        if profile_name not in self.CLOCK_PROFILES:
            logging.error(f"Profil inconnu: {profile_name}")
            return False

        profile = self.CLOCK_PROFILES[profile_name]
        success = self.lock_gpu_clocks(profile.min_clock_mhz, profile.max_clock_mhz)

        if success:
            self.current_profile = profile_name
            logging.info(f"Profil '{profile.name}' applique: {profile.description}")

            # Sur les GPU qui le supportent, on plafonne AUSSI la puissance,
            # proportionnellement au cap de clock (clock plus bas -> moins de
            # watts). Sur la 2070 (CLOCK_ONLY) cet appel ne fait rien.
            if self.capabilities == GPUControlCapability.FULL:
                pct = max(0.5, min(1.0, profile.max_clock_mhz / 2100))
                self.set_power_limit_pct(pct)

        return success

    def auto_adjust_for_temperature(self, current_temp: int, thermal_profile: str = 'medium') -> str:
        """
        Ajustement AUTOMATIQUE des clocks selon la temperature
        CONTROLE REEL ! APPROCHE PROACTIVE !

        NOUVELLE LOGIQUE : Intervenir TOT pour maintenir GPU frais et efficace
        La temperature varie VITE selon le mode graphique - on anticipe !

        Args:
            current_temp: Temperature actuelle du GPU
            thermal_profile: Profil thermique du jeu ('ultra', 'extreme', 'high', 'medium', 'low', 'esport')
        """
        if self.capabilities == GPUControlCapability.READ_ONLY:
            return 'readonly'

        # SEUILS PROACTIFS selon le profil thermique du jeu
        # Plus le jeu est lourd, plus on intervient TOT !

        if thermal_profile == 'ultra':
            # ULTRA : Jeux TRES lourds (Teardown, etc.) - PROTECTION AGGRESSIVE
            if current_temp >= 88:
                target_profile = 'emergency'  # 1000 MHz max
            elif current_temp >= 85:
                target_profile = 'critical'   # 1200 MHz max
            elif current_temp >= 82:
                target_profile = 'power_save' # 1700 MHz max
            elif current_temp >= 78:
                target_profile = 'quiet'      # 1850 MHz max
            elif current_temp >= 75:
                target_profile = 'ultra_cool' # 1900 MHz max
            else:
                target_profile = 'balanced'   # 1950 MHz max

        elif thermal_profile == 'extreme':
            # EXTREME : Cyberpunk, etc. - LAPTOP GAMING (tolere 85°C normal)
            if current_temp >= 90:
                target_profile = 'emergency'   # 1000 MHz - urgence
            elif current_temp >= 88:
                target_profile = 'critical'    # 1200 MHz - critique
            elif current_temp >= 86:
                target_profile = 'power_save'  # 1700 MHz - chaud
            elif current_temp >= 83:
                target_profile = 'quiet'       # 1850 MHz - tiède
            elif current_temp >= 80:
                target_profile = 'balanced'    # 1950 MHz - normal
            else:
                target_profile = 'performance' # 2100 MHz - froid

        elif thermal_profile == 'high':
            # HIGH : AAA standard - LAPTOP GAMING (tolere 83°C normal)
            if current_temp >= 90:
                target_profile = 'emergency'
            elif current_temp >= 88:
                target_profile = 'critical'
            elif current_temp >= 85:
                target_profile = 'power_save'
            elif current_temp >= 82:
                target_profile = 'quiet'
            elif current_temp >= 78:
                target_profile = 'balanced'
            else:
                target_profile = 'performance'

        elif thermal_profile == 'esport':
            # ESPORT : Priorite FPS - Tolere plus chaud mais protege quand meme
            if current_temp >= 90:
                target_profile = 'emergency'
            elif current_temp >= 88:
                target_profile = 'critical'
            elif current_temp >= 85:
                target_profile = 'power_save'
            elif current_temp >= 82:
                target_profile = 'quiet'
            else:
                target_profile = 'esport'  # Max performance pour FPS

        elif thermal_profile == 'low':
            # LOW : Jeux legers - Intervient tot
            if current_temp >= 88:
                target_profile = 'emergency'
            elif current_temp >= 85:
                target_profile = 'critical'
            elif current_temp >= 82:
                target_profile = 'power_save'
            elif current_temp >= 78:
                target_profile = 'quiet'
            else:
                target_profile = 'performance'

        elif thermal_profile == 'local_ai':
            # LOCAL_AI : Inference soutenue (Ollama, LM Studio...) - cible ~70-75°C
            # L'inference est memory-bound et tourne a des clocks bas (~855 MHz mesure).
            # Les caps gaming (1000-2100) ne mordent jamais : il faut des caps
            # SOUS le clock operatoire pour avoir un effet reel (valide par mesure).
            if current_temp >= 88:
                target_profile = 'ai_brake'    # 450 MHz - frein d'urgence
            elif current_temp >= 84:
                target_profile = 'ai_throttle' # 600 MHz - throttle effectif
            elif current_temp >= 80:
                target_profile = 'ai_soft'     # 750 MHz - throttle leger
            else:
                target_profile = 'performance' # pas de cap effectif (2100)

        else:
            # MEDIUM (default) : Standard - PROTECTION EQUILIBREE
            if current_temp >= 88:
                target_profile = 'emergency'
            elif current_temp >= 85:
                target_profile = 'critical'
            elif current_temp >= 82:
                target_profile = 'quiet'
            elif current_temp >= 80:
                target_profile = 'balanced'
            else:
                target_profile = 'performance'

        # Appliquer seulement si different du profil actuel
        if target_profile != self.current_profile:
            logging.info(f"🌡️ Ajustement PROACTIF: {current_temp}°C (profil:{thermal_profile}) -> '{target_profile}'")
            self.apply_profile(target_profile)
            return target_profile

        return self.current_profile or 'none'

    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut complet du controleur"""
        metrics = self.get_gpu_metrics()

        return {
            'capabilities': self.capabilities.value,
            'clock_locked': self.is_clock_locked,
            'current_profile': self.current_profile,
            'current_clock_limit': self.current_clock_limit,
            'gpu_metrics': metrics,
            'control_stats': self.control_stats.copy(),
            'available_profiles': list(self.CLOCK_PROFILES.keys())
        }


class GPUThermalManager:
    """
    Gestionnaire thermique avec CONTROLE REEL
    Surveillance continue + ajustement automatique
    """

    def __init__(self, controller: GPURealController):
        self.controller = controller
        self.is_running = False
        self.check_interval = 2.0  # secondes
        self.thermal_history = []
        self.max_history = 300  # 10 minutes a 2s interval

        # Seuils configurables
        self.thresholds = {
            'warning': 70,
            'high': 75,
            'critical': 80,
            'emergency': 85
        }

    def start_monitoring(self):
        """Demarre la surveillance thermique avec controle reel"""
        import threading

        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logging.info("Surveillance thermique REELLE demarree")

    def stop_monitoring(self):
        """Arrete la surveillance et reset le GPU"""
        self.is_running = False
        self.controller.reset_gpu_clocks()
        logging.info("Surveillance thermique arretee - GPU reset")

    def _monitoring_loop(self):
        """Boucle de surveillance avec controle reel"""
        while self.is_running:
            try:
                metrics = self.controller.get_gpu_metrics()
                temp = metrics.get('temperature', 0)

                # Historique
                self.thermal_history.append({
                    'time': time.time(),
                    'temp': temp,
                    'clock': metrics.get('clock_current', 0),
                    'profile': self.controller.current_profile
                })

                if len(self.thermal_history) > self.max_history:
                    self.thermal_history.pop(0)

                # Ajustement automatique REEL
                if temp > 0:
                    self.controller.auto_adjust_for_temperature(temp)

                time.sleep(self.check_interval)

            except Exception as e:
                logging.error(f"Erreur monitoring: {e}")
                time.sleep(5)

    def get_thermal_stats(self) -> Dict[str, Any]:
        """Statistiques thermiques"""
        if not self.thermal_history:
            return {}

        temps = [h['temp'] for h in self.thermal_history]
        return {
            'current': temps[-1] if temps else 0,
            'average': sum(temps) / len(temps),
            'max': max(temps),
            'min': min(temps),
            'samples': len(temps),
            'duration_minutes': len(temps) * self.check_interval / 60
        }


# Instance globale pour import facile
GPU_CONTROLLER = GPURealController()


def test_real_control():
    """Test du controle GPU reel"""
    print("=" * 60)
    print("TEST CONTROLE GPU REEL - TEMPLE IAM")
    print("=" * 60)

    controller = GPURealController()

    # Status initial
    print("\n[1] Status initial:")
    status = controller.get_status()
    print(f"    Capacites: {status['capabilities']}")
    print(f"    GPU Temp: {status['gpu_metrics'].get('temperature', 'N/A')}C")
    print(f"    GPU Clock: {status['gpu_metrics'].get('clock_current', 'N/A')} MHz")

    if controller.capabilities == GPUControlCapability.READ_ONLY:
        print("\n[!] Controle GPU non supporte sur ce systeme")
        return

    # Test profil quiet
    print("\n[2] Test profil 'quiet' (max 1800 MHz):")
    success = controller.apply_profile('quiet')
    print(f"    Succes: {success}")

    time.sleep(2)

    metrics = controller.get_gpu_metrics()
    print(f"    GPU Clock apres: {metrics.get('clock_current', 'N/A')} MHz")
    print(f"    Clock locked: {metrics.get('clock_locked', False)}")

    # Test profil performance
    print("\n[3] Test profil 'performance' (max 2100 MHz):")
    success = controller.apply_profile('performance')
    print(f"    Succes: {success}")

    time.sleep(2)

    metrics = controller.get_gpu_metrics()
    print(f"    GPU Clock apres: {metrics.get('clock_current', 'N/A')} MHz")

    # Reset
    print("\n[4] Reset aux valeurs par defaut:")
    success = controller.reset_gpu_clocks()
    print(f"    Succes: {success}")

    # Stats finales
    print("\n[5] Statistiques de controle:")
    stats = controller.control_stats
    print(f"    Changements clocks: {stats['clock_changes']}")
    print(f"    Resets: {stats['resets']}")
    print(f"    Derniere action: {stats['last_action']}")

    print("\n" + "=" * 60)
    print("TEST TERMINE - CONTROLE GPU REEL FONCTIONNEL !")
    print("=" * 60)


if __name__ == "__main__":
    test_real_control()
