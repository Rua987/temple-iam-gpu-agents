"""
Offline validation for Temple IAM GPU Agents.

These tests do not require installed games, a real NVIDIA GPU, or GPU control.
They simulate running game processes and GPU/ML telemetry.
"""

import tempfile
import sys
import time
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from games_database import GAMES_DB
from gpu_ml_logger import GPUMLLogger
from afterburner_profile_controller import AfterburnerProfileController
from workload_thermal_controller import WorkloadThermalController
from universal_game_detector import UniversalGameDetector
from universal_gpu_monitor import UniversalGPUMonitor
from performance_scorer import (
    PerformanceScorer,
    PerformanceState,
    OptimizationStrategy,
)


class FakeProcess:
    def __init__(self, pid, name, memory_mb=2048, cpu_percent=50.0):
        self.info = {
            "pid": pid,
            "name": name,
            "exe": f"C:/Games/{name}",
            "create_time": time.time() - 3600,
            "cpu_percent": cpu_percent,
            "memory_info": SimpleNamespace(rss=memory_mb * 1024 * 1024),
        }


class FakeGpu:
    name = "NVIDIA GeForce RTX 2070"
    load = 0.88
    temperature = 72
    memoryUsed = 6500
    memoryTotal = 8192


class OfflineAgentValidationTest(unittest.TestCase):
    def test_validated_known_games_are_in_database(self):
        expected = {
            "AlanWake2.exe": "Alan Wake 2",
            "Cyberpunk2077.exe": "Cyberpunk 2077",
            "eldenring.exe": "Elden Ring",
            "teardown.exe": "Teardown",
        }

        for process_name, display_name in expected.items():
            with self.subTest(process_name=process_name):
                profile = GAMES_DB.get_game_by_process(process_name)
                self.assertIsNotNone(profile)
                self.assertEqual(profile.display_name, display_name)

    def test_process_detection_known_and_auto_learned_games(self):
        processes = [
            FakeProcess(101, "AlanWake2.exe", cpu_percent=35.0),
            FakeProcess(102, "Cyberpunk2077.exe", cpu_percent=55.0),
            FakeProcess(103, "eldenring.exe", cpu_percent=45.0),
            FakeProcess(104, "teardown.exe", cpu_percent=40.0),
            FakeProcess(105, "Arma4.exe", cpu_percent=65.0),
            FakeProcess(106, "HITMAN3.exe", cpu_percent=60.0),
            FakeProcess(107, "chrome.exe", cpu_percent=5.0),
        ]

        with tempfile.TemporaryDirectory() as tmp:
            learned_path = str(Path(tmp) / "learned_games.json")
            detector = UniversalGameDetector(auto_learn=True, learned_games_path=learned_path)

            with patch("universal_game_detector.psutil.process_iter", return_value=processes):
                detected = detector.detect_running_games()

        by_process = {game.process_name: game for game in detected}
        self.assertIn("AlanWake2.exe", by_process)
        self.assertIn("Cyberpunk2077.exe", by_process)
        self.assertIn("eldenring.exe", by_process)
        self.assertIn("teardown.exe", by_process)
        self.assertIn("Arma4.exe", by_process)
        self.assertIn("HITMAN3.exe", by_process)
        self.assertNotIn("chrome.exe", by_process)

        self.assertTrue(by_process["AlanWake2.exe"].is_known)
        self.assertTrue(by_process["Cyberpunk2077.exe"].is_known)
        self.assertTrue(by_process["eldenring.exe"].is_known)
        self.assertTrue(by_process["teardown.exe"].is_known)
        self.assertFalse(by_process["Arma4.exe"].is_known)
        self.assertFalse(by_process["HITMAN3.exe"].is_known)

        primary = detector.get_primary_game()
        self.assertEqual(primary.process_name, "Cyberpunk2077.exe")

        arma_profile = detector.get_game_optimization_profile(by_process["Arma4.exe"])
        self.assertEqual(arma_profile["thermal_profile"], "medium")
        self.assertFalse(arma_profile["is_known"])

    def test_workload_classification_local_ai_and_webview(self):
        """Ollama/LM Studio = local_ai (refroidissement stable), webview = observation."""
        processes = [
            FakeProcess(201, "ollama.exe", memory_mb=6000, cpu_percent=70.0),
            FakeProcess(202, "LM Studio.exe", memory_mb=4000, cpu_percent=20.0),
            FakeProcess(203, "msedgewebview2.exe", memory_mb=800, cpu_percent=90.0),
        ]

        with tempfile.TemporaryDirectory() as tmp:
            learned_path = str(Path(tmp) / "learned_games.json")
            detector = UniversalGameDetector(auto_learn=True, learned_games_path=learned_path)

            with patch("universal_game_detector.psutil.process_iter", return_value=processes):
                detected = detector.detect_running_games()

            by_process = {w.process_name: w for w in detected}

            self.assertEqual(by_process["ollama.exe"].category, "local_ai")
            self.assertEqual(by_process["LM Studio.exe"].category, "local_ai")
            self.assertEqual(by_process["msedgewebview2.exe"].category, "browser_webview")

            # IA locale : refroidissement stable, pas de cible FPS
            ollama_profile = detector.get_game_optimization_profile(by_process["ollama.exe"])
            self.assertEqual(ollama_profile["optimization_mode"], "stable_cooling")
            self.assertEqual(ollama_profile["target_temp"], 70)
            self.assertEqual(ollama_profile["target_fps"], 0)

            # WebView : observation seulement
            webview_profile = detector.get_game_optimization_profile(by_process["msedgewebview2.exe"])
            self.assertEqual(webview_profile["optimization_mode"], "observe_only")

            # Le webview ne doit jamais devenir le workload principal,
            # même avec le CPU le plus élevé
            primary = detector.get_primary_game()
            self.assertEqual(primary.process_name, "ollama.exe")

    def test_known_game_beats_local_ai_as_primary(self):
        """Un jeu connu garde la priorité sur l'IA locale pour l'optimisation."""
        processes = [
            FakeProcess(301, "ollama.exe", memory_mb=6000, cpu_percent=80.0),
            FakeProcess(302, "Cyberpunk2077.exe", cpu_percent=50.0),
        ]

        with tempfile.TemporaryDirectory() as tmp:
            learned_path = str(Path(tmp) / "learned_games.json")
            detector = UniversalGameDetector(auto_learn=True, learned_games_path=learned_path)

            with patch("universal_game_detector.psutil.process_iter", return_value=processes):
                detector.detect_running_games()

            primary = detector.get_primary_game()

        self.assertEqual(primary.process_name, "Cyberpunk2077.exe")
        self.assertEqual(primary.category, "gaming")

    def test_monitor_collects_simulated_rtx2070_metrics(self):
        fake_gputil = SimpleNamespace(getGPUs=lambda: [FakeGpu()])
        with patch.dict(sys.modules, {"GPUtil": fake_gputil}):
            monitor = UniversalGPUMonitor(monitor_interval=1.0, max_history=10)

        monitor.gpu_available = True
        monitor.gpu_name = FakeGpu.name
        monitor.start_time = datetime.now()

        cyberpunk = GAMES_DB.get_game_by_process("Cyberpunk2077.exe")
        game = SimpleNamespace(
            profile=cyberpunk,
            process_name="Cyberpunk2077.exe",
            pid=202,
            is_known=True,
            custom_name=cyberpunk.display_name,
            cpu_usage=55.0,
            memory_mb=4096,
        )
        monitor.current_game_profile = {
            "target_fps": cyberpunk.default_settings["target_fps"],
            "target_temp": cyberpunk.default_settings["target_temp"],
            "thermal_profile": cyberpunk.thermal_profile,
        }

        with patch.dict(sys.modules, {"GPUtil": fake_gputil}), \
             patch("universal_gpu_monitor.psutil.cpu_percent", return_value=30.0), \
             patch("universal_gpu_monitor.psutil.virtual_memory", return_value=SimpleNamespace(percent=45.0, available=12 * 1024**3)):
            data = monitor._collect_monitoring_data(game, [game])

        self.assertTrue(data["game_detected"])
        self.assertEqual(data["gpu_name"], "NVIDIA GeForce RTX 2070")
        self.assertEqual(data["gpu_temperature"], 72)
        self.assertAlmostEqual(data["gpu_memory_percent"], 79.3457, places=3)
        self.assertEqual(data["game_info"]["game_name"], "Cyberpunk 2077")
        self.assertGreater(data["fps_estimate"], 0)

    def test_ml_logger_builds_profile_from_replayed_sessions(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = GPUMLLogger(log_directory=tmp)

            for session_idx in range(2):
                logger.start_session("Cyberpunk 2077")
                for i in range(30):
                    logger.log_datapoint({
                        "gpu_temperature": 68 + session_idx + i * 0.1,
                        "gpu_usage": 82 + (i % 8),
                        "fps_estimate": 55 + (i % 5),
                    })
                logger.end_session()
                time.sleep(1.1)

            profile = logger.analyze_game_profile("Cyberpunk 2077")

        self.assertIsNotNone(profile)
        self.assertEqual(profile["game"], "Cyberpunk 2077")
        self.assertEqual(profile["sessions_analyzed"], 2)
        self.assertGreater(profile["thermal_profile"]["avg_temp"], 68)
        self.assertGreater(profile["performance_profile"]["avg_gpu_load"], 82)

    def test_afterburner_profile_controller_is_slot_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exe = root / "MSIAfterburner.exe"
            profiles_dir = root / "Profiles"
            profiles_dir.mkdir()
            exe.write_text("", encoding="utf-8")

            controller = AfterburnerProfileController(
                afterburner_exe=exe,
                profiles_dir=profiles_dir,
                dry_run=True,
            )

            self.assertEqual(controller.choose_profile(None), "stock")
            self.assertEqual(
                controller.choose_profile({"category": "local_ai", "optimization_mode": "stable_cooling"}),
                "efficient",
            )
            self.assertEqual(
                controller.choose_profile({"category": "browser_webview", "optimization_mode": "observe_only"}),
                "stock",
            )

            # Aucun profil sauvegarde : refus d'appliquer, pour ne pas mentir.
            self.assertFalse(controller.apply_profile("efficient"))

            (profiles_dir / "VEN_10DE.cfg").write_text("[Profile2]\nCoreClkBoost=0\n", encoding="utf-8")
            self.assertTrue(controller.apply_profile("efficient"))

    def test_workload_thermal_controller_modes(self):
        class FakeAfterburner:
            def __init__(self):
                self.current_profile = None

            def apply_profile(self, name):
                self.current_profile = name
                return True

        class FakeGPU:
            READ_ONLY = "readonly"

            def __init__(self):
                from gpu_real_controller import GPUControlCapability

                self.capabilities = GPUControlCapability.CLOCK_ONLY
                self.is_clock_locked = False
                self.last_profile = None

            def apply_profile(self, name):
                self.last_profile = name
                self.is_clock_locked = True
                return True

            def reset_gpu_clocks(self):
                self.is_clock_locked = False
                self.last_profile = None
                return True

        afterburner = FakeAfterburner()
        gpu = FakeGPU()
        controller = WorkloadThermalController(afterburner=afterburner, gpu_controller=gpu)

        self.assertEqual(controller.resolve_mode(None), "stock")
        self.assertEqual(
            controller.resolve_mode({"category": "gaming", "optimization_mode": "active"}),
            "heavy_cool",
        )
        self.assertEqual(
            controller.resolve_mode({"category": "local_ai", "optimization_mode": "stable_cooling"}),
            "efficient_only",
        )
        self.assertEqual(
            controller.resolve_mode({"category": "browser_webview", "optimization_mode": "observe_only"}),
            "stock",
        )

        self.assertTrue(controller.apply_for_workload({"category": "gaming", "optimization_mode": "active"}))
        self.assertEqual(controller.current_mode, "heavy_cool")
        self.assertEqual(afterburner.current_profile, "efficient")
        self.assertEqual(gpu.last_profile, "heavy_cool")
        self.assertTrue(gpu.is_clock_locked)

        self.assertTrue(controller.apply_for_workload({"category": "local_ai", "optimization_mode": "stable_cooling"}))
        self.assertEqual(controller.current_mode, "efficient_only")
        self.assertFalse(gpu.is_clock_locked)

        self.assertTrue(controller.apply_for_workload(None))
        self.assertEqual(controller.current_mode, "stock")
        self.assertEqual(afterburner.current_profile, "stock")

    def test_local_ai_temperature_ladder(self):
        class FakeAfterburner:
            def __init__(self):
                self.current_profile = None

            def apply_profile(self, name):
                self.current_profile = name
                return True

        class FakeGPU:
            def __init__(self):
                from gpu_real_controller import GPUControlCapability

                self.capabilities = GPUControlCapability.CLOCK_ONLY
                self.is_clock_locked = False
                self.current_profile = None
                self.applied = []

            def apply_profile(self, name):
                self.applied.append(name)
                self.current_profile = name
                self.is_clock_locked = True
                return True

            def reset_gpu_clocks(self):
                self.applied.append("reset")
                self.current_profile = None
                self.is_clock_locked = False
                return True

        thermal = WorkloadThermalController(afterburner=FakeAfterburner(), gpu_controller=FakeGPU())
        profile = {"category": "local_ai", "optimization_mode": "stable_cooling", "target_temp": 70}
        thermal.apply_for_workload(profile)

        self.assertEqual(thermal.adjust_for_temperature(72, profile), "ai_soft")
        status_soft = thermal.get_display_status()
        self.assertIn("750 MHz", status_soft["ai_ladder"])
        self.assertEqual(thermal.adjust_for_temperature(78, profile), "ai_throttle")
        self.assertEqual(thermal.adjust_for_temperature(88, profile), "ai_brake")
        self.assertEqual(thermal.adjust_for_temperature(68, profile), "none")
        self.assertFalse(thermal.gpu_controller.is_clock_locked)


class PerformanceScorerOfflineTest(unittest.TestCase):
    def test_thermal_emergency_state(self):
        scorer = PerformanceScorer()
        result = scorer.calculate_score(
            temperature=100,
            gpu_usage=100,
            fps_current=5,
            fps_avg=8,
            fps_1_low=2,
            frametime_ms=80,
            clock_current=800,
            cpu_usage=90,
            is_throttling=True,
        )
        self.assertLess(result.overall_score, 30)
        self.assertEqual(result.state, PerformanceState.EMERGENCY)
        self.assertEqual(result.recommended_strategy, OptimizationStrategy.EMERGENCY_THROTTLE)
        self.assertEqual(result.breakdown.malus_throttle, -10.0)

    def test_boost_mode_recommends_boost_strategy(self):
        scorer = PerformanceScorer()
        result = scorer.calculate_score(
            temperature=62,
            gpu_usage=75,
            fps_current=90,
            fps_avg=88,
            fps_1_low=75,
            frametime_ms=11.1,
            clock_current=2100,
            cpu_usage=55,
            is_boosting=True,
        )
        self.assertGreaterEqual(result.overall_score, 85)
        self.assertEqual(result.recommended_strategy, OptimizationStrategy.BOOST)
        self.assertGreater(result.breakdown.bonus_boost_active, 0)

    def test_cpu_bottleneck_applies_malus(self):
        scorer = PerformanceScorer()
        result = scorer.calculate_score(
            temperature=72,
            gpu_usage=45,
            fps_current=45,
            fps_avg=43,
            fps_1_low=35,
            frametime_ms=22.2,
            clock_current=1600,
            cpu_usage=95,
        )
        self.assertEqual(result.breakdown.malus_bottleneck, -5.0)

    def test_good_session_scores_excellent_or_better(self):
        scorer = PerformanceScorer()
        result = scorer.calculate_score(
            temperature=74,
            gpu_usage=82,
            fps_current=62,
            fps_avg=60,
            fps_1_low=50,
            frametime_ms=16,
            clock_current=1800,
            cpu_usage=65,
        )
        self.assertGreaterEqual(result.overall_score, 85)
        self.assertIn(
            result.state,
            (PerformanceState.GOOD, PerformanceState.EXCELLENT, PerformanceState.PEAK),
        )

    def test_configure_for_game_ultra_profile(self):
        scorer = PerformanceScorer()
        scorer.configure_for_game(
            {"thermal_profile": "ultra", "target_temp": 75.0, "target_fps": 60.0}
        )
        self.assertEqual(scorer.config["critical_temp"], 78)
        self.assertEqual(scorer.config["optimal_gpu_usage"], 95)
        self.assertEqual(scorer.config["target_temp"], 75.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
