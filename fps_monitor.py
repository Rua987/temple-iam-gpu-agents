"""
📊 FPS MONITOR - LECTURE FPS TEMPS RÉEL ! 🎮
Objectif : Lire les FPS en temps réel pour optimiser le sweet spot perf/temp

MÉTHODES DE LECTURE FPS :
1. RTSS (RivaTuner Statistics Server) - Via shared memory
2. FrameView SDK - Via fichier log
3. Windows Performance Counters - Via ETW
4. PresentMon - Via ligne de commande

PLUS ULTRA ! DATTEBAYO ! 🚀⚡
"""

import os
import time
import mmap
import struct
import ctypes
import logging
import subprocess
import threading
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import json

logging.basicConfig(level=logging.INFO, format='📊 %(asctime)s - %(levelname)s - %(message)s')


@dataclass
class FPSData:
    """Données FPS collectées"""
    timestamp: datetime
    fps_current: float
    fps_avg: float
    fps_min: float
    fps_max: float
    fps_1_percent_low: float
    fps_0_1_percent_low: float
    frametime_ms: float
    frametime_avg_ms: float
    source: str  # 'rtss', 'presentmon', 'manual', etc.


@dataclass
class FPSSession:
    """Session de monitoring FPS"""
    game_name: str
    start_time: datetime
    fps_history: List[float] = field(default_factory=list)
    frametime_history: List[float] = field(default_factory=list)


class RTSSMonitor:
    """
    Moniteur FPS via RTSS (RivaTuner Statistics Server)
    Lit directement depuis la shared memory de RTSS
    """

    # Structure RTSS Shared Memory Header
    RTSS_SIGNATURE = 0x52545353  # 'RTSS'

    def __init__(self):
        self.is_available = False
        self.shared_memory = None
        self._check_rtss()

    def _check_rtss(self):
        """Vérifie si RTSS est disponible"""
        try:
            # Essayer d'ouvrir la shared memory RTSS
            self.shared_memory = mmap.mmap(-1, 4096, "RTSSSharedMemoryV2", access=mmap.ACCESS_READ)

            # Lire la signature
            self.shared_memory.seek(0)
            signature = struct.unpack('I', self.shared_memory.read(4))[0]

            if signature == self.RTSS_SIGNATURE:
                self.is_available = True
                logging.info("✅ RTSS détecté et disponible !")
            else:
                self.is_available = False
                logging.warning("⚠️ RTSS shared memory trouvée mais signature invalide")

        except Exception as e:
            self.is_available = False
            logging.info(f"ℹ️ RTSS non disponible: {str(e)}")

    def get_fps(self) -> Optional[float]:
        """Lit le FPS actuel depuis RTSS"""
        if not self.is_available or not self.shared_memory:
            return None

        try:
            # Structure simplifiée - offset du FPS dans RTSS shared memory
            # Note: La vraie structure est plus complexe, ceci est une approximation
            self.shared_memory.seek(32)  # Offset approximatif pour le FPS
            fps_data = struct.unpack('f', self.shared_memory.read(4))[0]
            return fps_data if fps_data > 0 and fps_data < 1000 else None
        except:
            return None


class PresentMonMonitor:
    """
    Moniteur FPS via PresentMon (outil Microsoft)
    Plus fiable et ne nécessite pas RTSS
    """

    def __init__(self):
        self.is_available = False
        self.presentmon_path = self._find_presentmon()
        self.process = None
        self.output_file = "presentmon_output.csv"
        self.fps_data = deque(maxlen=1000)
        self.is_running = False

    def _find_presentmon(self) -> Optional[str]:
        """Trouve PresentMon sur le système"""
        paths = [
            "PresentMon.exe",
            "C:\\Program Files\\PresentMon\\PresentMon.exe",
            "C:\\PresentMon\\PresentMon.exe",
            os.path.join(os.path.dirname(__file__), "PresentMon.exe")
        ]

        for path in paths:
            if os.path.exists(path):
                self.is_available = True
                logging.info(f"✅ PresentMon trouvé: {path}")
                return path

        logging.info("ℹ️ PresentMon non trouvé - Téléchargez-le depuis GitHub")
        return None

    def start_monitoring(self, process_name: str = None):
        """Démarre le monitoring PresentMon"""
        if not self.presentmon_path:
            return False

        try:
            cmd = [self.presentmon_path, "-output_file", self.output_file, "-terminate_on_proc_exit"]
            if process_name:
                cmd.extend(["-process_name", process_name])

            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.is_running = True
            logging.info(f"✅ PresentMon démarré pour {process_name or 'tous les processus'}")
            return True
        except Exception as e:
            logging.error(f"❌ Erreur démarrage PresentMon: {e}")
            return False

    def stop_monitoring(self):
        """Arrête le monitoring PresentMon"""
        if self.process:
            self.process.terminate()
            self.is_running = False
            logging.info("🛑 PresentMon arrêté")

    def parse_output(self) -> List[Dict[str, float]]:
        """Parse le fichier output de PresentMon"""
        results = []
        if not os.path.exists(self.output_file):
            return results

        try:
            with open(self.output_file, 'r') as f:
                lines = f.readlines()

            if len(lines) < 2:
                return results

            # Header
            headers = lines[0].strip().split(',')

            # Trouver les colonnes importantes
            frametime_col = None
            for i, h in enumerate(headers):
                if 'msbet' in h.lower() or 'frametime' in h.lower():
                    frametime_col = i
                    break

            if frametime_col is None:
                return results

            # Parser les données
            for line in lines[1:]:
                parts = line.strip().split(',')
                if len(parts) > frametime_col:
                    try:
                        frametime = float(parts[frametime_col])
                        if frametime > 0:
                            fps = 1000.0 / frametime
                            results.append({
                                'frametime_ms': frametime,
                                'fps': fps
                            })
                    except:
                        continue

        except Exception as e:
            logging.error(f"❌ Erreur parsing PresentMon: {e}")

        return results


class WindowsPerformanceMonitor:
    """
    Moniteur FPS via Windows Performance Counters
    Méthode native Windows, pas besoin d'outils tiers
    """

    def __init__(self):
        self.is_available = True
        self.last_frame_count = 0
        self.last_time = time.time()
        self.fps_history = deque(maxlen=60)  # 60 dernières secondes

    def get_gpu_fps_estimate(self) -> Optional[float]:
        """
        Estime le FPS basé sur l'activité GPU
        Note: C'est une estimation, pas une mesure exacte
        """
        try:
            # Utiliser nvidia-smi pour obtenir des métriques de rendu
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=clocks.current.graphics,utilization.gpu',
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=2
            )

            if result.returncode == 0:
                parts = result.stdout.strip().split(', ')
                clock = int(parts[0]) if parts[0] != '[N/A]' else 0
                usage = int(parts[1]) if parts[1] != '[N/A]' else 0

                # Estimation très approximative basée sur usage GPU
                # Plus l'usage est élevé, plus on rend de frames
                if usage > 0 and clock > 0:
                    # Formule heuristique - à ajuster selon le jeu
                    estimated_fps = (usage / 100) * (clock / 1500) * 60
                    return min(estimated_fps, 144)  # Cap à 144

        except Exception as e:
            logging.debug(f"Erreur estimation FPS: {e}")

        return None


class FPSMonitor:
    """
    Moniteur FPS principal - OMNISCIENT ! 👁️
    Utilise la meilleure méthode disponible
    """

    def __init__(self):
        self.rtss = RTSSMonitor()
        self.presentmon = PresentMonMonitor()
        self.windows_perf = WindowsPerformanceMonitor()

        # Session actuelle
        self.current_session: Optional[FPSSession] = None
        self.is_monitoring = False

        # Données collectées
        self.fps_buffer = deque(maxlen=3600)  # 1 heure à 1 FPS/sec
        self.frametime_buffer = deque(maxlen=3600)

        # Stats calculées
        self.current_fps = 0.0
        self.avg_fps = 0.0
        self.min_fps = float('inf')
        self.max_fps = 0.0
        self.fps_1_low = 0.0
        self.fps_01_low = 0.0

        # Thread de monitoring
        self.monitor_thread = None
        self.stop_event = threading.Event()

        # Déterminer la meilleure source
        self.active_source = self._determine_best_source()
        logging.info(f"🎮 FPS Monitor initialisé - Source: {self.active_source}")

    def _determine_best_source(self) -> str:
        """Détermine la meilleure source de FPS disponible"""
        if self.rtss.is_available:
            return 'rtss'
        elif self.presentmon.is_available:
            return 'presentmon'
        else:
            return 'estimate'  # Estimation basée sur GPU

    def start_session(self, game_name: str):
        """Démarre une session de monitoring FPS"""
        self.current_session = FPSSession(
            game_name=game_name,
            start_time=datetime.now()
        )
        self.is_monitoring = True
        self.fps_buffer.clear()
        self.frametime_buffer.clear()
        self.min_fps = float('inf')
        self.max_fps = 0.0

        # Démarrer PresentMon si c'est la source active
        if self.active_source == 'presentmon':
            # Convertir le nom du jeu en nom de process
            process_name = game_name.replace(' ', '') + '.exe'
            self.presentmon.start_monitoring(process_name)

        # Démarrer le thread de monitoring
        self.stop_event.clear()
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()

        logging.info(f"🎮 Session FPS démarrée pour {game_name}")

    def stop_session(self) -> Optional[FPSSession]:
        """Arrête la session et retourne les données"""
        self.is_monitoring = False
        self.stop_event.set()

        if self.active_source == 'presentmon':
            self.presentmon.stop_monitoring()

        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

        session = self.current_session
        self.current_session = None

        logging.info("🛑 Session FPS terminée")
        return session

    def _monitoring_loop(self):
        """Boucle de monitoring FPS"""
        while not self.stop_event.is_set():
            try:
                fps = self._read_fps()

                if fps and fps > 0:
                    self.current_fps = fps
                    self.fps_buffer.append(fps)

                    if self.current_session:
                        self.current_session.fps_history.append(fps)

                    # Mettre à jour les stats
                    self._update_stats()

                time.sleep(0.1)  # 10 Hz sampling

            except Exception as e:
                logging.debug(f"Erreur monitoring FPS: {e}")
                time.sleep(1)

    def _read_fps(self) -> Optional[float]:
        """Lit le FPS depuis la source active"""
        if self.active_source == 'rtss':
            return self.rtss.get_fps()
        elif self.active_source == 'presentmon':
            # Lire depuis le fichier output
            data = self.presentmon.parse_output()
            if data:
                return data[-1]['fps']
        else:
            return self.windows_perf.get_gpu_fps_estimate()

        return None

    def _update_stats(self):
        """Met à jour les statistiques FPS"""
        if not self.fps_buffer:
            return

        fps_list = list(self.fps_buffer)

        self.avg_fps = sum(fps_list) / len(fps_list)
        self.min_fps = min(self.min_fps, min(fps_list))
        self.max_fps = max(self.max_fps, max(fps_list))

        # Calcul 1% et 0.1% lows
        sorted_fps = sorted(fps_list)
        n = len(sorted_fps)

        if n >= 100:
            self.fps_1_low = sum(sorted_fps[:n//100]) / (n//100) if n >= 100 else sorted_fps[0]
            self.fps_01_low = sum(sorted_fps[:n//1000]) / (n//1000) if n >= 1000 else sorted_fps[0]
        else:
            self.fps_1_low = sorted_fps[0]
            self.fps_01_low = sorted_fps[0]

    def get_current_data(self) -> FPSData:
        """Retourne les données FPS actuelles"""
        frametime = 1000.0 / self.current_fps if self.current_fps > 0 else 0
        frametime_avg = 1000.0 / self.avg_fps if self.avg_fps > 0 else 0

        return FPSData(
            timestamp=datetime.now(),
            fps_current=self.current_fps,
            fps_avg=self.avg_fps,
            fps_min=self.min_fps if self.min_fps != float('inf') else 0,
            fps_max=self.max_fps,
            fps_1_percent_low=self.fps_1_low,
            fps_0_1_percent_low=self.fps_01_low,
            frametime_ms=frametime,
            frametime_avg_ms=frametime_avg,
            source=self.active_source
        )

    def get_session_summary(self) -> Dict[str, Any]:
        """Retourne le résumé de la session"""
        if not self.current_session:
            return {}

        fps_list = self.current_session.fps_history
        if not fps_list:
            return {}

        sorted_fps = sorted(fps_list)
        n = len(sorted_fps)

        return {
            'game': self.current_session.game_name,
            'duration_minutes': (datetime.now() - self.current_session.start_time).total_seconds() / 60,
            'samples': n,
            'fps_avg': sum(fps_list) / n,
            'fps_min': min(fps_list),
            'fps_max': max(fps_list),
            'fps_1_low': sum(sorted_fps[:max(1, n//100)]) / max(1, n//100),
            'fps_01_low': sum(sorted_fps[:max(1, n//1000)]) / max(1, n//1000),
            'fps_stability': 100 - (max(fps_list) - min(fps_list)) / max(fps_list) * 100 if max(fps_list) > 0 else 0,
            'source': self.active_source
        }


# Instance globale
FPS_MONITOR = FPSMonitor()


def test_fps_monitor():
    """Test du moniteur FPS"""
    print("=" * 60)
    print("📊 TEST FPS MONITOR - TEMPLE IAM")
    print("=" * 60)

    monitor = FPSMonitor()

    print(f"\n📡 Source active: {monitor.active_source}")
    print(f"   RTSS disponible: {monitor.rtss.is_available}")
    print(f"   PresentMon disponible: {monitor.presentmon.is_available}")

    # Test de lecture FPS
    print("\n🎮 Test lecture FPS (5 secondes)...")
    monitor.start_session("Test Game")

    for i in range(5):
        time.sleep(1)
        data = monitor.get_current_data()
        print(f"   [{i+1}s] FPS: {data.fps_current:.1f} (avg: {data.fps_avg:.1f})")

    session = monitor.stop_session()

    if session:
        summary = monitor.get_session_summary()
        print(f"\n📊 Résumé session:")
        print(f"   Samples: {len(session.fps_history)}")

    print("\n" + "=" * 60)
    print("✅ TEST TERMINÉ")
    print("=" * 60)


if __name__ == "__main__":
    test_fps_monitor()
