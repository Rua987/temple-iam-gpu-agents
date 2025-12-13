"""
🎮 ALAN WAKE 2 GPU MONITOR - MONITORING CONTINU DIVIN ! 🏛️
Objectif : Monitoring GPU temps réel pendant Alan Wake 2

FONCTIONNALITÉS DIVINES :
🎯 Détection Alan Wake 2 : Reconnaissance automatique du processus
🎯 Monitoring Continu : Surveillance 24/7
🎯 Métriques Temps Réel : GPU, CPU, Mémoire, FPS estimé
🎯 Alertes Intelligentes : Recommandations automatiques
🎯 Dashboard Live : Affichage en temps réel

PLUS ULTRA ! DATTEBAYO ! 🚀⚡🥷🏛️
"""

import time
import threading
import psutil
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
import sys

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='🎮 %(asctime)s - %(levelname)s - %(message)s')

class AlanWake2GPUMonitor:
    """Moniteur GPU Alan Wake 2 - SURVEILLANCE DIVINE CONTINUE ! 🎮"""
    
    def __init__(self):
        """Initialisation du moniteur Alan Wake 2 divin"""
        self.is_running = False
        self.alan_wake2_detected = False
        self.alan_wake2_process = None
        self.monitoring_data = []
        self.alert_history = []
        
        # Configuration du monitoring
        self.monitor_interval = 1.0  # secondes
        self.max_history = 1000  # points de données
        
        # Seuils d'alerte
        self.alert_thresholds = {
            'gpu_usage': 90.0,  # % - Alerte si GPU > 90%
            'gpu_memory': 85.0,  # % - Alerte si mémoire GPU > 85%
            'gpu_temperature': 80.0,  # °C - Alerte si température > 80°C
            'cpu_usage': 95.0,  # % - Alerte si CPU > 95%
            'memory_usage': 90.0,  # % - Alerte si RAM > 90%
            'fps_drop': 30.0  # FPS - Alerte si FPS < 30
        }
        
        # Initialisation GPU
        self._initialize_gpu_monitoring()
        
        logging.info("🎮 Moniteur Alan Wake 2 GPU initialisé - SURVEILLANCE DIVINE ACTIVE !")
    
    def _initialize_gpu_monitoring(self):
        """Initialisation du monitoring GPU - CONFIGURATION DIVINE ! ⚡"""
        try:
            # Import GPU monitoring
            import GPUtil
            self.gpu_available = True
            self.gpu_name = "NVIDIA GPU"
            
            # Test initial
            gpus = GPUtil.getGPUs()
            if gpus:
                self.gpu_name = gpus[0].name
                logging.info(f"✅ GPU détecté: {self.gpu_name}")
            else:
                logging.warning("⚠️ Aucun GPU NVIDIA détecté")
                
        except ImportError:
            logging.warning("⚠️ GPUtil non disponible - Monitoring GPU limité")
            self.gpu_available = False
        except Exception as e:
            logging.error(f"❌ Erreur initialisation GPU: {str(e)}")
            self.gpu_available = False
    
    def start_monitoring(self):
        """Démarrage du monitoring continu - SURVEILLANCE DIVINE ! 👁️"""
        logging.info("🎮 DÉMARRAGE MONITORING ALAN WAKE 2 GPU CONTINU !")
        
        self.is_running = True
        self.start_time = datetime.now()
        
        try:
            # Démarrage du monitoring en continu
            self._run_continuous_monitoring()
            
        except KeyboardInterrupt:
            logging.info("🛑 Arrêt manuel du monitoring...")
        except Exception as e:
            logging.error(f"❌ Erreur monitoring: {str(e)}")
        finally:
            self.stop_monitoring()
    
    def _run_continuous_monitoring(self):
        """Exécution du monitoring continu - VISION DIVINE ! 🔮"""
        print("\n" + "="*80)
        print("🎮 MONITEUR ALAN WAKE 2 GPU - SURVEILLANCE DIVINE EN COURS")
        print("="*80)
        print("💡 Appuie sur Ctrl+C pour arrêter le monitoring")
        print("="*80)
        
        while self.is_running:
            try:
                # Collecte des données
                monitoring_data = self._collect_monitoring_data()
                
                # Stockage des données
                self.monitoring_data.append(monitoring_data)
                if len(self.monitoring_data) > self.max_history:
                    self.monitoring_data.pop(0)
                
                # Affichage temps réel
                self._display_realtime_metrics(monitoring_data)
                
                # Vérification des alertes
                self._check_alerts(monitoring_data)
                
                # Attente avant la prochaine collecte
                time.sleep(self.monitor_interval)
                
            except Exception as e:
                logging.error(f"❌ Erreur collecte données: {str(e)}")
                time.sleep(5)
    
    def _collect_monitoring_data(self) -> Dict[str, Any]:
        """Collecte des données de monitoring - COLLECTE DIVINE ! 📊"""
        try:
            # Timestamp
            timestamp = datetime.now()
            
            # Détection Alan Wake 2
            alan_wake2_info = self._detect_alan_wake2()
            
            # Métriques système
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Métriques GPU
            gpu_metrics = self._get_gpu_metrics()
            
            # Estimation FPS
            estimated_fps = self._estimate_fps(cpu_usage, gpu_metrics.get('gpu_usage_percent', 0))
            
            # Temps de fonctionnement
            uptime = (timestamp - self.start_time).total_seconds() if self.start_time else 0
            
            return {
                'timestamp': timestamp,
                'uptime_seconds': uptime,
                'alan_wake2_detected': alan_wake2_info['detected'],
                'alan_wake2_process': alan_wake2_info['process_name'],
                'alan_wake2_pid': alan_wake2_info['pid'],
                'cpu_usage_percent': cpu_usage,
                'memory_usage_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'memory_total_gb': memory.total / (1024**3),
                'gpu_usage_percent': gpu_metrics.get('gpu_usage_percent', 0),
                'gpu_memory_percent': gpu_metrics.get('gpu_memory_percent', 0),
                'gpu_memory_used_mb': gpu_metrics.get('gpu_memory_used_mb', 0),
                'gpu_memory_total_mb': gpu_metrics.get('gpu_memory_total_mb', 0),
                'gpu_temperature_c': gpu_metrics.get('gpu_temperature_c', 0),
                'estimated_fps': estimated_fps,
                'gpu_name': gpu_metrics.get('gpu_name', 'Unknown')
            }
            
        except Exception as e:
            logging.error(f"❌ Erreur collecte données: {str(e)}")
            return {
                'timestamp': datetime.now(),
                'error': str(e)
            }
    
    def _detect_alan_wake2(self) -> Dict[str, Any]:
        """Détection d'Alan Wake 2 - DÉTECTION DIVINE ! 🔍"""
        try:
            # Noms de processus possibles pour Alan Wake 2
            alan_wake2_processes = [
                'AlanWake2.exe',
                'alanwake2.exe',
                'Alan Wake 2.exe',
                'alan wake 2.exe',
                'AW2.exe',
                'aw2.exe'
            ]
            
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name']
                    if proc_name in alan_wake2_processes:
                        self.alan_wake2_detected = True
                        self.alan_wake2_process = proc
                        return {
                            'detected': True,
                            'process_name': proc_name,
                            'pid': proc.info['pid'],
                            'exe': proc.info['exe']
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Si pas trouvé, reset
            if self.alan_wake2_detected:
                self.alan_wake2_detected = False
                self.alan_wake2_process = None
            
            return {
                'detected': False,
                'process_name': 'Non détecté',
                'pid': None,
                'exe': None
            }
            
        except Exception as e:
            logging.error(f"❌ Erreur détection Alan Wake 2: {str(e)}")
            return {
                'detected': False,
                'process_name': 'Erreur',
                'pid': None,
                'exe': None
            }
    
    def _get_gpu_metrics(self) -> Dict[str, Any]:
        """Collecte des métriques GPU - MÉTRIQUES DIVINES ! 📈"""
        try:
            if not self.gpu_available:
                return {
                    'gpu_usage_percent': 0,
                    'gpu_memory_percent': 0,
                    'gpu_memory_used_mb': 0,
                    'gpu_memory_total_mb': 0,
                    'gpu_temperature_c': 0,
                    'gpu_name': 'Non disponible'
                }
            
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                return {
                    'gpu_usage_percent': gpu.load * 100,
                    'gpu_memory_percent': (gpu.memoryUsed / gpu.memoryTotal) * 100,
                    'gpu_memory_used_mb': gpu.memoryUsed,
                    'gpu_memory_total_mb': gpu.memoryTotal,
                    'gpu_temperature_c': gpu.temperature,
                    'gpu_name': gpu.name
                }
            
            return {
                'gpu_usage_percent': 0,
                'gpu_memory_percent': 0,
                'gpu_memory_used_mb': 0,
                'gpu_memory_total_mb': 0,
                'gpu_temperature_c': 0,
                'gpu_name': 'Non détecté'
            }
            
        except Exception as e:
            logging.error(f"❌ Erreur métriques GPU: {str(e)}")
            return {
                'gpu_usage_percent': 0,
                'gpu_memory_percent': 0,
                'gpu_memory_used_mb': 0,
                'gpu_memory_total_mb': 0,
                'gpu_temperature_c': 0,
                'gpu_name': 'Erreur'
            }
    
    def _estimate_fps(self, cpu_usage: float, gpu_usage: float) -> float:
        """Estimation des FPS - PRÉDICTION DIVINE ! 🔮"""
        try:
            # Estimation basée sur l'utilisation CPU et GPU
            # Plus l'utilisation est élevée, plus les FPS sont bas
            
            # Facteurs de performance
            cpu_factor = max(0, 100 - cpu_usage) / 100
            gpu_factor = max(0, 100 - gpu_usage) / 100
            
            # FPS de base pour Alan Wake 2 (RTX 2070)
            base_fps = 60.0
            
            # Ajustement selon l'utilisation
            adjusted_fps = base_fps * (cpu_factor * 0.6 + gpu_factor * 0.4)
            
            # Limites réalistes
            min_fps = 15.0
            max_fps = 120.0
            
            return max(min_fps, min(max_fps, adjusted_fps))
            
        except:
            return 60.0
    
    def _display_realtime_metrics(self, data: Dict[str, Any]):
        """Affichage des métriques temps réel - VISION DIVINE ! 👁️"""
        try:
            # Nettoyage de l'écran (optionnel)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # En-tête
            print("\n" + "="*80)
            print(f"🎮 MONITEUR ALAN WAKE 2 GPU - {data['timestamp'].strftime('%H:%M:%S')}")
            print("="*80)
            
            # Statut Alan Wake 2
            if data.get('alan_wake2_detected', False):
                print(f"✅ ALAN WAKE 2: ACTIF (PID: {data.get('alan_wake2_pid', 'N/A')})")
            else:
                print("⏳ ALAN WAKE 2: EN ATTENTE...")
            
            print("="*80)
            
            # Métriques système
            print("🧠 SYSTÈME:")
            print(f"   CPU: {data.get('cpu_usage_percent', 0):.1f}%")
            print(f"   RAM: {data.get('memory_usage_percent', 0):.1f}% ({data.get('memory_used_gb', 0):.1f}GB / {data.get('memory_total_gb', 0):.1f}GB)")
            
            # Métriques GPU
            print(f"\n🖥️ GPU ({data.get('gpu_name', 'Unknown')}):")
            print(f"   Usage: {data.get('gpu_usage_percent', 0):.1f}%")
            print(f"   Mémoire: {data.get('gpu_memory_percent', 0):.1f}% ({data.get('gpu_memory_used_mb', 0):.0f}MB / {data.get('gpu_memory_total_mb', 0):.0f}MB)")
            print(f"   Température: {data.get('gpu_temperature_c', 0):.1f}°C")
            
            # Performance
            print(f"\n⚡ PERFORMANCE:")
            print(f"   FPS Estimé: {data.get('estimated_fps', 0):.1f}")
            
            # Temps de fonctionnement
            uptime_minutes = data.get('uptime_seconds', 0) / 60
            print(f"\n⏰ Temps de monitoring: {uptime_minutes:.1f} minutes")
            
            # Alertes récentes
            if self.alert_history:
                print(f"\n🚨 DERNIÈRES ALERTES:")
                for alert in self.alert_history[-3:]:  # 3 dernières alertes
                    print(f"   {alert['timestamp'].strftime('%H:%M:%S')}: {alert['message']}")
            
            print("="*80)
            
        except Exception as e:
            logging.error(f"❌ Erreur affichage: {str(e)}")
    
    def _check_alerts(self, data: Dict[str, Any]):
        """Vérification des alertes - ALERTES DIVINES ! 🚨"""
        try:
            alerts = []
            
            # Alerte GPU usage
            if data.get('gpu_usage_percent', 0) > self.alert_thresholds['gpu_usage']:
                alerts.append(f"GPU usage élevé: {data.get('gpu_usage_percent', 0):.1f}%")
            
            # Alerte GPU mémoire
            if data.get('gpu_memory_percent', 0) > self.alert_thresholds['gpu_memory']:
                alerts.append(f"GPU mémoire élevée: {data.get('gpu_memory_percent', 0):.1f}%")
            
            # Alerte GPU température
            if data.get('gpu_temperature_c', 0) > self.alert_thresholds['gpu_temperature']:
                alerts.append(f"GPU température élevée: {data.get('gpu_temperature_c', 0):.1f}°C")
            
            # Alerte CPU usage
            if data.get('cpu_usage_percent', 0) > self.alert_thresholds['cpu_usage']:
                alerts.append(f"CPU usage élevé: {data.get('cpu_usage_percent', 0):.1f}%")
            
            # Alerte mémoire système
            if data.get('memory_usage_percent', 0) > self.alert_thresholds['memory_usage']:
                alerts.append(f"Mémoire système élevée: {data.get('memory_usage_percent', 0):.1f}%")
            
            # Alerte FPS bas
            if data.get('estimated_fps', 0) < self.alert_thresholds['fps_drop']:
                alerts.append(f"FPS bas: {data.get('estimated_fps', 0):.1f}")
            
            # Ajout des alertes à l'historique
            for alert_message in alerts:
                alert = {
                    'timestamp': data['timestamp'],
                    'message': alert_message,
                    'severity': 'warning'
                }
                self.alert_history.append(alert)
                
                # Limitation de l'historique
                if len(self.alert_history) > 50:
                    self.alert_history.pop(0)
                
                # Log de l'alerte
                logging.warning(f"🚨 ALERTE: {alert_message}")
            
        except Exception as e:
            logging.error(f"❌ Erreur vérification alertes: {str(e)}")
    
    def stop_monitoring(self):
        """Arrêt du monitoring - ARRÊT DIVIN ! 🛑"""
        logging.info("🛑 ARRÊT MONITORING ALAN WAKE 2 GPU")
        
        self.is_running = False
        
        # Affichage du résumé final
        self._display_final_summary()
        
        logging.info("✅ Monitoring arrêté avec succès")
    
    def _display_final_summary(self):
        """Affichage du résumé final - RÉSUMÉ DIVIN ! 📊"""
        if not self.monitoring_data:
            return
        
        print("\n" + "="*80)
        print("🏁 RÉSUMÉ FINAL - MONITORING ALAN WAKE 2 GPU")
        print("="*80)
        
        # Statistiques générales
        total_points = len(self.monitoring_data)
        alan_wake2_sessions = sum(1 for data in self.monitoring_data if data.get('alan_wake2_detected', False))
        
        print(f"📊 Points de données collectés: {total_points}")
        print(f"🎮 Sessions Alan Wake 2 détectées: {alan_wake2_sessions}")
        
        if self.monitoring_data:
            # Métriques moyennes
            avg_cpu = sum(data.get('cpu_usage_percent', 0) for data in self.monitoring_data) / total_points
            avg_gpu = sum(data.get('gpu_usage_percent', 0) for data in self.monitoring_data) / total_points
            avg_fps = sum(data.get('estimated_fps', 0) for data in self.monitoring_data) / total_points
            
            print(f"🧠 CPU Moyen: {avg_cpu:.1f}%")
            print(f"🖥️ GPU Moyen: {avg_gpu:.1f}%")
            print(f"⚡ FPS Moyen: {avg_fps:.1f}")
        
        # Alertes
        if self.alert_history:
            print(f"🚨 Alertes totales: {len(self.alert_history)}")
        
        print("="*80)
        print("🎮 MONITORING ALAN WAKE 2 GPU TERMINÉ - MISSION ACCOMPLIE !")
        print("Plus Ultra ! DATTEBAYO ! ⚡")

def main():
    """Fonction principale - DÉMARRAGE DIVIN ! 🚀"""
    print("🎮 MONITEUR ALAN WAKE 2 GPU - TEMPLE IAM ULTRA INSTINCT")
    print("="*60)
    print("💡 Ce moniteur va surveiller ton GPU en temps réel")
    print("💡 Lance Alan Wake 2 pour voir les métriques en action")
    print("💡 Appuie sur Ctrl+C pour arrêter")
    print("="*60)
    
    # Création et démarrage du moniteur
    monitor = AlanWake2GPUMonitor()
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt manuel du moniteur...")
        monitor.stop_monitoring()

if __name__ == "__main__":
    main() 