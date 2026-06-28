# 🚀 Quick Start - Universal Game Detection System

## 🎯 What Changed?

Temple IAM now **detects ANY game automatically** instead of being limited to Alan Wake 2!

---

## ⚡ 30-Second Start

### Python (Recommended for Testing)
```bash
# 1. Install dependencies
pip install -r requirements_gpu.txt

# 2. Test the system
python test_universal_system_safe.py

# 3. Run universal monitor
python universal_gpu_monitor.py
```

### Docker (Recommended for Production)
```bash
# Start universal GPU monitor
docker-compose -f docker-compose.gpu.yml up universal-gpu-monitor
```

---

## 🎮 What Games are Supported?

### Built-in (16+ games)
- ✅ Alan Wake 2
- ✅ Cyberpunk 2077
- ✅ Elden Ring
- ✅ Hogwarts Legacy
- ✅ Red Dead Redemption 2
- ✅ Starfield
- ✅ Call of Duty MW3/Warzone
- ✅ Assassin's Creed Mirage/Valhalla
- ✅ Spider-Man Remastered
- ✅ God of War
- ✅ The Last of Us
- ✅ VALORANT
- ✅ Apex Legends
- ✅ Forza Horizon 5
- ✅ **And more...**

### Unknown Games
🆕 **Auto-learns** any game it detects!

---

## 📋 Complete Test

```bash
# Run complete test suite
python test_universal_system_safe.py
```

Expected output:
```
[PASS] - Base de donnees de jeux
[PASS] - Detecteur universel de jeux
[PASS] - Integration GPU Monitor
[PASS] - Integration Thermal Optimizer

Resultat: 4/4 tests reussis
[SUCCESS] TOUS LES TESTS SONT REUSSIS !
```

---

## 🖥️ Usage Examples

### 1. Universal GPU Monitor
```bash
python universal_gpu_monitor.py
```

**What it does:**
- ✅ Detects running games automatically
- ✅ Shows game-specific optimizations
- ✅ Real-time GPU metrics
- ✅ Adaptive thermal targets
- ✅ FPS estimation

### 2. Thermal Optimizer (Now Universal!)
```bash
python temple_iam_thermal_optimizer.py
```

**What changed:**
- ✅ Now detects ANY game (not just Alan Wake 2)
- ✅ Adaptive thermal profiles per game
- ✅ Auto-adjusts based on detected game

---

## 🐳 Docker Commands

### Universal Monitor
```bash
# Start
docker-compose -f docker-compose.gpu.yml up universal-gpu-monitor -d

# Logs
docker logs -f temple_iam_universal_gpu_monitor

# Stop
docker-compose -f docker-compose.gpu.yml down
```

### Full Stack
```bash
# Start everything
docker-compose -f docker-compose.gpu.yml up -d

# View logs
docker-compose -f docker-compose.gpu.yml logs -f
```

### Legacy Mode (Alan Wake 2 only)
```bash
docker-compose -f docker-compose.gpu.yml --profile legacy up legacy-gpu-monitor
```

---

## 🧪 Test Individual Components

### Test Game Database
```python
from games_database import GAMES_DB

# List all games
all_games = GAMES_DB.get_all_games()
print(f"Games in database: {len(all_games)}")

# Search by name
game = GAMES_DB.get_game_by_name("cyberpunk_2077")
print(f"Game: {game.display_name}")
print(f"Thermal profile: {game.thermal_profile}")
```

### Test Game Detector
```python
from universal_game_detector import GAME_DETECTOR

# Detect running games
games = GAME_DETECTOR.detect_running_games()

for game in games:
    print(f"Detected: {game.custom_name}")
    print(f"Known: {game.is_known}")

    profile = GAME_DETECTOR.get_game_optimization_profile(game)
    print(f"Target temp: {profile['target_temp']}°C")
```

---

## 📊 How It Works

1. **Game Detection**
   - Scans running processes
   - Matches against database (16+ games)
   - Auto-learns unknown games

2. **Profile Selection**
   - Loads game-specific profile
   - Sets thermal targets
   - Applies optimizations

3. **Monitoring**
   - Real-time GPU metrics
   - Game-aware alerts
   - Performance tracking

4. **Optimization**
   - Adaptive fan control
   - Temperature management
   - Power limit adjustment

---

## 🔧 Configuration

### Environment Variables
```bash
# Auto-learning (default: true)
AUTO_LEARN=true

# Monitor interval (default: 1.0s)
MONITOR_INTERVAL=1.0

# Log level
LOG_LEVEL=INFO
```

### Learned Games File
The system creates `learned_games.json` automatically:
```json
{
  "MyGame.exe": {
    "custom_name": "My Game",
    "first_detected": "2024-12-14T17:50:00",
    "detection_count": 5
  }
}
```

---

## 🆚 Old vs New

### Old System (v1.0)
```bash
# Manual configuration required
GAME_NAME=AlanWake2  # Must specify!

# Only Alan Wake 2 supported
python alan_wake2_gpu_monitor.py
```

### New System (v2.0)
```bash
# Zero configuration!
# Detects ANY game automatically

python universal_gpu_monitor.py
```

---

## 📚 Documentation

- **Full Migration Guide**: `MIGRATION_GUIDE.md`
- **Changelog**: `UNIVERSAL_SYSTEM_CHANGELOG.md`
- **Main README**: `README.md`

---

## ⚠️ Troubleshooting

### "No games detected"
```bash
# Check if processes are running
python -c "from universal_game_detector import GAME_DETECTOR; print(GAME_DETECTOR.detect_running_games())"
```

### "GPU not available"
```bash
# Check NVIDIA drivers
nvidia-smi

# Check GPUtil
python -c "import GPUtil; print(GPUtil.getGPUs())"
```

### "Module not found"
```bash
# Ensure you're in the right directory
cd C:\Users\admin\.claude-worktrees\temple-iam-gpu-agents\jolly-austin

# Reinstall dependencies
pip install -r requirements_gpu.txt
```

---

## 🎉 Success Indicators

You'll know it's working when you see:

1. ✅ Test suite passes: `4/4 tests reussis`
2. ✅ Games detected automatically
3. ✅ Game-specific profiles loaded
4. ✅ Real-time monitoring active
5. ✅ `learned_games.json` created

---

## 🚀 Next Steps

1. **Run Tests**
   ```bash
   python test_universal_system_safe.py
   ```

2. **Start Monitoring**
   ```bash
   python universal_gpu_monitor.py
   ```

3. **Launch Your Game**
   - System detects automatically
   - Applies optimizations
   - Monitors performance

4. **Check Results**
   - View real-time stats
   - Check learned games
   - Monitor temperatures

---

## 💡 Pro Tips

1. **Let it Learn**: Run with different games to build your library
2. **Check Learned Games**: Review `learned_games.json` periodically
3. **Use Docker**: For production, Docker is more stable
4. **Monitor Logs**: Keep an eye on detection logs
5. **Customize**: Add your own games to `games_database.py`

---

**Ready to go?** 🚀

```bash
python universal_gpu_monitor.py
```

**PLUS ULTRA ! DATTEBAYO !** 🏛️⚡
