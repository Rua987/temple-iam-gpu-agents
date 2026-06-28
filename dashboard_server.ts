/**
 * 📊 TEMPLE IAM DASHBOARD - SERVEUR BUN.JS TEMPS RÉEL ! 🔥
 *
 * Objectif : Dashboard web temps réel pour visualiser les métriques GPU
 *
 * FONCTIONNALITÉS :
 * - WebSocket pour données temps réel
 * - API REST pour données historiques
 * - Interface web moderne et responsive
 *
 * LANCEMENT : bun run dashboard_server.ts
 * URL : http://localhost:3000
 *
 * PLUS ULTRA ! DATTEBAYO ! 🚀⚡
 */

import { serve, file } from "bun";

// Types
interface GPUMetrics {
  timestamp: string;
  temperature: number;
  usage: number;
  clock_speed: number;
  memory_clock: number;
  fan_speed: number;
  power_draw: number;
  vram_used: number;
  vram_total: number;
}

interface FPSMetrics {
  current: number;
  avg: number;
  min: number;
  max: number;
  fps_1_low: number;
  frametime_ms: number;
}

interface MLPrediction {
  predicted_5s: number;
  predicted_10s: number;
  predicted_30s: number;
  trend: string;
  spike_probability: number;
  recommended_action: string;
  confidence: number;
}

interface SweetSpot {
  optimal_clock: number;
  optimal_temp: number;
  expected_fps: number;
  efficiency: number;
  recommendation: string;
}

interface PerformanceScore {
  overall: number;
  state: string;
  strategy: string;
  thermal: number;
  fps: number;
  efficiency: number;
  stability: number;
  trend: string;
  trend_delta: number;
  recommendations: string[];
}

interface DashboardData {
  gpu: GPUMetrics;
  fps: FPSMetrics;
  ml: MLPrediction;
  sweet_spot: SweetSpot | null;
  score: PerformanceScore | null;
  game: {
    name: string;
    profile: string;
    is_known: boolean;
  } | null;
  optimizations: string[];
  uptime_seconds: number;
}

// État global
let currentData: DashboardData | null = null;
let dataHistory: DashboardData[] = [];
const MAX_HISTORY = 3600; // 1 heure de données

// WebSocket clients
const wsClients = new Set<any>();

// HTML du dashboard
const dashboardHTML = `
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 Temple IAM Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }

        .header h1 {
            font-size: 2.5em;
            background: linear-gradient(45deg, #ff6b6b, #feca57, #48dbfb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        .game-info {
            font-size: 1.2em;
            color: #48dbfb;
        }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }

        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        .card h2 {
            font-size: 1.3em;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        .metric:last-child {
            border-bottom: none;
        }

        .metric-label {
            color: #a0a0a0;
        }

        .metric-value {
            font-size: 1.4em;
            font-weight: bold;
        }

        .temp-cold { color: #48dbfb; }
        .temp-normal { color: #1dd1a1; }
        .temp-warm { color: #feca57; }
        .temp-hot { color: #ff9f43; }
        .temp-critical { color: #ff6b6b; }

        .progress-bar {
            width: 100%;
            height: 10px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
            overflow: hidden;
            margin-top: 5px;
        }

        .progress-fill {
            height: 100%;
            border-radius: 5px;
            transition: width 0.3s, background 0.3s;
        }

        .gauge {
            width: 150px;
            height: 150px;
            margin: 0 auto;
            position: relative;
        }

        .gauge-value {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 2em;
            font-weight: bold;
        }

        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }

        .status-good { background: #1dd1a1; color: #000; }
        .status-warning { background: #feca57; color: #000; }
        .status-danger { background: #ff6b6b; color: #fff; }

        /* Score Container Styles */
        .score-container {
            max-width: 1400px;
            margin: 0 auto 20px auto;
            padding: 0 20px;
        }

        .score-card {
            background: linear-gradient(135deg, rgba(29, 209, 161, 0.2) 0%, rgba(72, 219, 251, 0.2) 100%);
            border-radius: 20px;
            padding: 25px;
            border: 2px solid rgba(29, 209, 161, 0.5);
            box-shadow: 0 10px 40px rgba(29, 209, 161, 0.2);
        }

        .score-header {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 20px;
        }

        .score-icon {
            font-size: 2.5em;
        }

        .score-title {
            font-size: 1.8em;
            font-weight: bold;
            background: linear-gradient(45deg, #1dd1a1, #48dbfb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .score-main {
            display: flex;
            gap: 40px;
            align-items: center;
            flex-wrap: wrap;
            justify-content: center;
        }

        .score-gauge {
            width: 180px;
            height: 180px;
            position: relative;
            flex-shrink: 0;
        }

        .score-value-container {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }

        .score-value {
            font-size: 3em;
            font-weight: bold;
            color: #1dd1a1;
        }

        .score-max {
            font-size: 1em;
            color: #a0a0a0;
        }

        .score-details {
            flex: 1;
            min-width: 300px;
        }

        .score-state {
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .score-strategy {
            color: #a0a0a0;
            margin-bottom: 15px;
        }

        .score-breakdown {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 15px;
        }

        .breakdown-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .breakdown-label {
            font-size: 0.9em;
            white-space: nowrap;
        }

        .breakdown-bar {
            flex: 1;
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
        }

        .breakdown-fill {
            height: 100%;
            border-radius: 4px;
            background: linear-gradient(90deg, #1dd1a1, #48dbfb);
            transition: width 0.3s;
        }

        .breakdown-value {
            font-size: 0.9em;
            font-weight: bold;
            min-width: 30px;
            text-align: right;
        }

        .score-recommendations {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 10px 15px;
            font-size: 0.9em;
        }

        .score-recommendations ul {
            margin: 0;
            padding-left: 20px;
        }

        .score-recommendations li {
            margin: 5px 0;
            color: #feca57;
        }

        /* Score state colors */
        .score-emergency { color: #ff6b6b; }
        .score-poor { color: #ff9f43; }
        .score-acceptable { color: #feca57; }
        .score-good { color: #1dd1a1; }
        .score-excellent { color: #48dbfb; }
        .score-peak { color: #a29bfe; }

        @media (max-width: 600px) {
            .score-breakdown {
                grid-template-columns: 1fr;
            }
            .score-main {
                flex-direction: column;
            }
        }

        .chart-container {
            width: 100%;
            height: 200px;
            margin-top: 15px;
        }

        .chart-card {
            grid-column: span 2;
        }

        @media (max-width: 768px) {
            .chart-card {
                grid-column: span 1;
            }
        }

        .ml-prediction {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .prediction-box {
            flex: 1;
            min-width: 80px;
            text-align: center;
            padding: 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }

        .prediction-time {
            font-size: 0.8em;
            color: #a0a0a0;
        }

        .prediction-temp {
            font-size: 1.5em;
            font-weight: bold;
        }

        .trend-rising { color: #ff6b6b; }
        .trend-stable { color: #feca57; }
        .trend-falling { color: #48dbfb; }

        .optimization-list {
            list-style: none;
        }

        .optimization-list li {
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        .connection-status {
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
        }

        .connected { background: #1dd1a1; color: #000; }
        .disconnected { background: #ff6b6b; color: #fff; }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        .updating {
            animation: pulse 1s infinite;
        }

        /* 🌙 MODE CLAIR */
        body.light-mode {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 50%, #d0d5db 100%);
            color: #1a1a2e;
        }

        body.light-mode .header {
            background: rgba(0,0,0,0.05);
        }

        body.light-mode .header h1 {
            background: linear-gradient(45deg, #e74c3c, #f39c12, #3498db);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        body.light-mode .card {
            background: rgba(255,255,255,0.8);
            border: 1px solid rgba(0,0,0,0.1);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        body.light-mode .metric-label {
            color: #666;
        }

        body.light-mode .metric-value {
            color: #1a1a2e;
        }

        body.light-mode .game-info {
            color: #3498db;
        }

        body.light-mode .progress-bar {
            background: rgba(0,0,0,0.1);
        }

        body.light-mode .prediction-box {
            background: rgba(0,0,0,0.05);
        }

        body.light-mode .optimization-list li {
            border-bottom-color: rgba(0,0,0,0.1);
        }

        /* Toggle Button */
        .theme-toggle {
            position: fixed;
            top: 10px;
            left: 10px;
            padding: 10px 15px;
            border-radius: 20px;
            border: none;
            cursor: pointer;
            font-size: 1.2em;
            background: rgba(255,255,255,0.2);
            color: #fff;
            backdrop-filter: blur(10px);
            transition: all 0.3s;
            z-index: 1000;
        }

        .theme-toggle:hover {
            background: rgba(255,255,255,0.3);
            transform: scale(1.1);
        }

        body.light-mode .theme-toggle {
            background: rgba(0,0,0,0.1);
            color: #1a1a2e;
        }

        body.light-mode .theme-toggle:hover {
            background: rgba(0,0,0,0.2);
        }
    </style>
</head>
<body>
    <button id="theme-toggle" class="theme-toggle" onclick="toggleTheme()">🌙</button>

    <div id="connection-status" class="connection-status disconnected">
        🔴 Déconnecté
    </div>

    <div class="header">
        <h1>🔥 TEMPLE IAM DASHBOARD</h1>
        <div id="game-info" class="game-info">En attente de données...</div>
        <div id="uptime" style="margin-top: 10px; color: #a0a0a0;"></div>
    </div>

    <!-- Score Global - NOUVEAU ! -->
    <div id="score-container" class="score-container" style="display: none;">
        <div class="score-card">
            <div class="score-header">
                <span class="score-icon" id="score-icon">🎯</span>
                <span class="score-title">SCORE PERFORMANCE</span>
            </div>
            <div class="score-main">
                <div class="score-gauge">
                    <svg viewBox="0 0 120 120">
                        <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="12"/>
                        <circle id="score-gauge-circle" cx="60" cy="60" r="54" fill="none" stroke="#1dd1a1" stroke-width="12"
                                stroke-dasharray="339" stroke-dashoffset="339" stroke-linecap="round"
                                transform="rotate(-90 60 60)"/>
                    </svg>
                    <div class="score-value-container">
                        <span id="score-value" class="score-value">--</span>
                        <span class="score-max">/100</span>
                    </div>
                </div>
                <div class="score-details">
                    <div id="score-state" class="score-state">En attente...</div>
                    <div id="score-strategy" class="score-strategy"></div>
                    <div class="score-breakdown">
                        <div class="breakdown-item">
                            <span class="breakdown-label">🌡️ Thermique</span>
                            <div class="breakdown-bar"><div id="score-thermal-bar" class="breakdown-fill" style="width: 0%;"></div></div>
                            <span id="score-thermal" class="breakdown-value">--</span>
                        </div>
                        <div class="breakdown-item">
                            <span class="breakdown-label">🎮 FPS</span>
                            <div class="breakdown-bar"><div id="score-fps-bar" class="breakdown-fill" style="width: 0%;"></div></div>
                            <span id="score-fps" class="breakdown-value">--</span>
                        </div>
                        <div class="breakdown-item">
                            <span class="breakdown-label">⚡ Efficacité</span>
                            <div class="breakdown-bar"><div id="score-efficiency-bar" class="breakdown-fill" style="width: 0%;"></div></div>
                            <span id="score-efficiency" class="breakdown-value">--</span>
                        </div>
                        <div class="breakdown-item">
                            <span class="breakdown-label">📈 Stabilité</span>
                            <div class="breakdown-bar"><div id="score-stability-bar" class="breakdown-fill" style="width: 0%;"></div></div>
                            <span id="score-stability" class="breakdown-value">--</span>
                        </div>
                    </div>
                    <div id="score-recommendations" class="score-recommendations"></div>
                </div>
            </div>
        </div>
    </div>

    <div class="dashboard">
        <!-- Température GPU -->
        <div class="card">
            <h2>🌡️ Température GPU</h2>
            <div class="gauge">
                <svg viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="10"/>
                    <circle id="temp-gauge" cx="50" cy="50" r="45" fill="none" stroke="#48dbfb" stroke-width="10"
                            stroke-dasharray="283" stroke-dashoffset="283" stroke-linecap="round"
                            transform="rotate(-90 50 50)"/>
                </svg>
                <div id="temp-value" class="gauge-value temp-cold">--°C</div>
            </div>
            <div id="temp-status" class="status-badge status-good" style="display: block; text-align: center; margin-top: 15px;">
                --
            </div>
        </div>

        <!-- Usage GPU -->
        <div class="card">
            <h2>🖥️ Usage GPU</h2>
            <div class="metric">
                <span class="metric-label">Utilisation</span>
                <span id="gpu-usage" class="metric-value">--%</span>
            </div>
            <div class="progress-bar">
                <div id="gpu-usage-bar" class="progress-fill" style="width: 0%; background: #48dbfb;"></div>
            </div>
            <div class="metric">
                <span class="metric-label">Clock GPU</span>
                <span id="gpu-clock" class="metric-value">-- MHz</span>
            </div>
            <div class="metric">
                <span class="metric-label">Clock Mémoire</span>
                <span id="mem-clock" class="metric-value">-- MHz</span>
            </div>
            <div class="metric">
                <span class="metric-label">Puissance</span>
                <span id="power-draw" class="metric-value">-- W</span>
            </div>
            <div class="metric">
                <span class="metric-label">VRAM Utilisée</span>
                <span id="vram-used" class="metric-value">-- GB</span>
            </div>
            <div class="progress-bar">
                <div id="vram-bar" class="progress-fill" style="width: 0%; background: #9b59b6;"></div>
            </div>
        </div>

        <!-- FPS -->
        <div class="card">
            <h2>🎮 FPS Temps Réel</h2>
            <div class="metric">
                <span class="metric-label">FPS Actuel</span>
                <span id="fps-current" class="metric-value" style="color: #1dd1a1;">-- FPS</span>
            </div>
            <div class="metric">
                <span class="metric-label">FPS Moyen</span>
                <span id="fps-avg" class="metric-value">--</span>
            </div>
            <div class="metric">
                <span class="metric-label">FPS Min / Max</span>
                <span id="fps-minmax" class="metric-value">-- / --</span>
            </div>
            <div class="metric">
                <span class="metric-label">1% Low</span>
                <span id="fps-1low" class="metric-value">--</span>
            </div>
            <div class="metric">
                <span class="metric-label">Frametime</span>
                <span id="frametime" class="metric-value">-- ms</span>
            </div>
        </div>

        <!-- ML Prédiction -->
        <div class="card">
            <h2>🧠 ML Prédiction</h2>
            <div id="ml-trend" class="status-badge status-good" style="margin-bottom: 15px;">
                -- Tendance
            </div>
            <div class="ml-prediction">
                <div class="prediction-box">
                    <div class="prediction-time">+5s</div>
                    <div id="pred-5s" class="prediction-temp">--°C</div>
                </div>
                <div class="prediction-box">
                    <div class="prediction-time">+10s</div>
                    <div id="pred-10s" class="prediction-temp">--°C</div>
                </div>
                <div class="prediction-box">
                    <div class="prediction-time">+30s</div>
                    <div id="pred-30s" class="prediction-temp">--°C</div>
                </div>
            </div>
            <div class="metric" style="margin-top: 15px;">
                <span class="metric-label">Probabilité Spike</span>
                <span id="spike-prob" class="metric-value">--%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Confiance</span>
                <span id="ml-confidence" class="metric-value">--%</span>
            </div>
            <div id="ml-action" style="margin-top: 10px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 10px;">
                --
            </div>
        </div>

        <!-- Sweet Spot -->
        <div class="card">
            <h2>🎯 Sweet Spot</h2>
            <div id="sweet-spot-content">
                <p style="color: #a0a0a0; text-align: center;">En attente d'analyse...</p>
            </div>
        </div>

        <!-- Optimisations -->
        <div class="card">
            <h2>⚙️ Optimisations Actives</h2>
            <ul id="optimizations" class="optimization-list">
                <li style="color: #a0a0a0;">Aucune optimisation active</li>
            </ul>
        </div>

        <!-- Graphique Historique Température/FPS -->
        <div class="card chart-card">
            <h2>📈 Historique Temps Réel</h2>
            <div class="chart-container" style="height: 250px;">
                <canvas id="historyChart"></canvas>
            </div>
        </div>

        <!-- Graphique Usage GPU/Puissance -->
        <div class="card chart-card">
            <h2>⚡ Usage & Puissance</h2>
            <div class="chart-container" style="height: 250px;">
                <canvas id="usageChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        // WebSocket connection
        let ws = null;
        let reconnectTimeout = null;

        // 📈 HISTORIQUE GRAPHIQUES
        const MAX_HISTORY_POINTS = 60; // 60 secondes d'historique
        const historyData = {
            labels: [],
            temperature: [],
            fps: [],
            usage: [],
            power: []
        };

        let historyChart = null;
        let usageChart = null;

        function initCharts() {
            // Graphique Température/FPS
            const historyCtx = document.getElementById('historyChart').getContext('2d');
            historyChart = new Chart(historyCtx, {
                type: 'line',
                data: {
                    labels: historyData.labels,
                    datasets: [
                        {
                            label: 'Température (°C)',
                            data: historyData.temperature,
                            borderColor: '#ff6b6b',
                            backgroundColor: 'rgba(255, 107, 107, 0.1)',
                            fill: true,
                            tension: 0.4,
                            yAxisID: 'y'
                        },
                        {
                            label: 'FPS',
                            data: historyData.fps,
                            borderColor: '#1dd1a1',
                            backgroundColor: 'rgba(29, 209, 161, 0.1)',
                            fill: true,
                            tension: 0.4,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: {
                            labels: { color: '#fff' }
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            ticks: { color: '#a0a0a0', maxTicksLimit: 10 },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: { display: true, text: 'Temp (°C)', color: '#ff6b6b' },
                            ticks: { color: '#ff6b6b' },
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            min: 40,
                            max: 100
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: { display: true, text: 'FPS', color: '#1dd1a1' },
                            ticks: { color: '#1dd1a1' },
                            grid: { drawOnChartArea: false },
                            min: 0
                        }
                    }
                }
            });

            // Graphique Usage/Puissance
            const usageCtx = document.getElementById('usageChart').getContext('2d');
            usageChart = new Chart(usageCtx, {
                type: 'line',
                data: {
                    labels: historyData.labels,
                    datasets: [
                        {
                            label: 'Usage GPU (%)',
                            data: historyData.usage,
                            borderColor: '#48dbfb',
                            backgroundColor: 'rgba(72, 219, 251, 0.1)',
                            fill: true,
                            tension: 0.4,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Puissance (W)',
                            data: historyData.power,
                            borderColor: '#feca57',
                            backgroundColor: 'rgba(254, 202, 87, 0.1)',
                            fill: true,
                            tension: 0.4,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: {
                            labels: { color: '#fff' }
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            ticks: { color: '#a0a0a0', maxTicksLimit: 10 },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: { display: true, text: 'Usage (%)', color: '#48dbfb' },
                            ticks: { color: '#48dbfb' },
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            min: 0,
                            max: 100
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: { display: true, text: 'Watts', color: '#feca57' },
                            ticks: { color: '#feca57' },
                            grid: { drawOnChartArea: false },
                            min: 0
                        }
                    }
                }
            });
        }

        function updateCharts(data) {
            // Ajouter le timestamp
            const now = new Date();
            const timeLabel = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

            historyData.labels.push(timeLabel);
            historyData.temperature.push(data.gpu.temperature);
            historyData.fps.push(data.fps.current);
            historyData.usage.push(data.gpu.usage);
            historyData.power.push(data.gpu.power_draw);

            // Limiter l'historique
            if (historyData.labels.length > MAX_HISTORY_POINTS) {
                historyData.labels.shift();
                historyData.temperature.shift();
                historyData.fps.shift();
                historyData.usage.shift();
                historyData.power.shift();
            }

            // Mettre à jour les graphiques
            if (historyChart) {
                historyChart.update('none'); // 'none' pour animation désactivée (plus fluide)
            }
            if (usageChart) {
                usageChart.update('none');
            }
        }

        // Initialiser les graphiques au chargement
        document.addEventListener('DOMContentLoaded', initCharts);

        // 🌙 THEME TOGGLE
        function toggleTheme() {
            const body = document.body;
            const btn = document.getElementById('theme-toggle');

            body.classList.toggle('light-mode');

            if (body.classList.contains('light-mode')) {
                btn.textContent = '☀️';
                localStorage.setItem('theme', 'light');

                // Mettre à jour les couleurs des graphiques pour le mode clair
                if (historyChart) {
                    historyChart.options.plugins.legend.labels.color = '#1a1a2e';
                    historyChart.options.scales.x.ticks.color = '#666';
                    historyChart.options.scales.x.grid.color = 'rgba(0,0,0,0.1)';
                    historyChart.options.scales.y.grid.color = 'rgba(0,0,0,0.1)';
                    historyChart.update();
                }
                if (usageChart) {
                    usageChart.options.plugins.legend.labels.color = '#1a1a2e';
                    usageChart.options.scales.x.ticks.color = '#666';
                    usageChart.options.scales.x.grid.color = 'rgba(0,0,0,0.1)';
                    usageChart.options.scales.y.grid.color = 'rgba(0,0,0,0.1)';
                    usageChart.update();
                }
            } else {
                btn.textContent = '🌙';
                localStorage.setItem('theme', 'dark');

                // Remettre les couleurs sombres
                if (historyChart) {
                    historyChart.options.plugins.legend.labels.color = '#fff';
                    historyChart.options.scales.x.ticks.color = '#a0a0a0';
                    historyChart.options.scales.x.grid.color = 'rgba(255,255,255,0.1)';
                    historyChart.options.scales.y.grid.color = 'rgba(255,255,255,0.1)';
                    historyChart.update();
                }
                if (usageChart) {
                    usageChart.options.plugins.legend.labels.color = '#fff';
                    usageChart.options.scales.x.ticks.color = '#a0a0a0';
                    usageChart.options.scales.x.grid.color = 'rgba(255,255,255,0.1)';
                    usageChart.options.scales.y.grid.color = 'rgba(255,255,255,0.1)';
                    usageChart.update();
                }
            }
        }

        // Charger le thème sauvegardé
        document.addEventListener('DOMContentLoaded', () => {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'light') {
                document.body.classList.add('light-mode');
                document.getElementById('theme-toggle').textContent = '☀️';
            }
        });

        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(protocol + '//' + window.location.host + '/ws');

            ws.onopen = () => {
                document.getElementById('connection-status').className = 'connection-status connected';
                document.getElementById('connection-status').textContent = '🟢 Connecté';
                console.log('WebSocket connected');
            };

            ws.onclose = () => {
                document.getElementById('connection-status').className = 'connection-status disconnected';
                document.getElementById('connection-status').textContent = '🔴 Déconnecté';
                console.log('WebSocket disconnected');

                // Reconnect after 3 seconds
                reconnectTimeout = setTimeout(connect, 3000);
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
        }

        function updateDashboard(data) {
            // Game info
            if (data.game) {
                document.getElementById('game-info').textContent =
                    '🎮 ' + data.game.name + ' - Profil: ' + data.game.profile.toUpperCase();
            } else {
                document.getElementById('game-info').textContent = '⏳ Aucun jeu détecté';
            }

            // Uptime
            const minutes = Math.floor(data.uptime_seconds / 60);
            document.getElementById('uptime').textContent = '⏰ Durée: ' + minutes + ' minutes';

            // ========== PERFORMANCE SCORE - NOUVEAU ! ==========
            if (data.score) {
                const scoreContainer = document.getElementById('score-container');
                scoreContainer.style.display = 'block';

                const score = data.score;

                // Update score value and gauge
                document.getElementById('score-value').textContent = Math.round(score.overall);

                // Score gauge (0-100 mapped to 0-339 stroke offset)
                const scoreOffset = 339 - (339 * score.overall / 100);
                document.getElementById('score-gauge-circle').setAttribute('stroke-dashoffset', scoreOffset);

                // Score color based on state
                const stateConfig = {
                    'emergency': { icon: '🚨', label: 'URGENCE', color: '#ff6b6b', class: 'score-emergency' },
                    'poor': { icon: '🔴', label: 'FAIBLE', color: '#ff9f43', class: 'score-poor' },
                    'acceptable': { icon: '🟡', label: 'ACCEPTABLE', color: '#feca57', class: 'score-acceptable' },
                    'good': { icon: '🟢', label: 'BON', color: '#1dd1a1', class: 'score-good' },
                    'excellent': { icon: '💚', label: 'EXCELLENT', color: '#48dbfb', class: 'score-excellent' },
                    'peak': { icon: '⭐', label: 'OPTIMAL', color: '#a29bfe', class: 'score-peak' }
                };

                const config = stateConfig[score.state] || stateConfig['acceptable'];
                document.getElementById('score-icon').textContent = config.icon;
                document.getElementById('score-value').style.color = config.color;
                document.getElementById('score-gauge-circle').setAttribute('stroke', config.color);

                const stateEl = document.getElementById('score-state');
                stateEl.textContent = config.icon + ' ' + config.label;
                stateEl.className = 'score-state ' + config.class;

                // Strategy display
                const strategyLabels = {
                    'emergency_throttle': '🚨 Throttle Urgence',
                    'thermal_focus': '🌡️ Priorité Refroidissement',
                    'balanced': '⚖️ Équilibré',
                    'performance': '⚡ Priorité Performance',
                    'boost': '🚀 Mode Boost'
                };
                document.getElementById('score-strategy').textContent = 'Stratégie: ' + (strategyLabels[score.strategy] || score.strategy);

                // Breakdown bars
                document.getElementById('score-thermal').textContent = Math.round(score.thermal);
                document.getElementById('score-thermal-bar').style.width = score.thermal + '%';

                document.getElementById('score-fps').textContent = Math.round(score.fps);
                document.getElementById('score-fps-bar').style.width = score.fps + '%';

                document.getElementById('score-efficiency').textContent = Math.round(score.efficiency);
                document.getElementById('score-efficiency-bar').style.width = score.efficiency + '%';

                document.getElementById('score-stability').textContent = Math.round(score.stability);
                document.getElementById('score-stability-bar').style.width = score.stability + '%';

                // Recommendations
                const recsEl = document.getElementById('score-recommendations');
                if (score.recommendations && score.recommendations.length > 0) {
                    recsEl.innerHTML = '<strong>💡 Recommandations:</strong><ul>' +
                        score.recommendations.map(r => '<li>' + r + '</li>').join('') + '</ul>';
                    recsEl.style.display = 'block';
                } else {
                    recsEl.style.display = 'none';
                }
            } else {
                document.getElementById('score-container').style.display = 'none';
            }

            // Temperature
            const temp = data.gpu.temperature;
            document.getElementById('temp-value').textContent = temp.toFixed(1) + '°C';

            // Temperature gauge (0-100°C mapped to 0-283 stroke offset)
            const tempPercent = Math.min(100, (temp / 100) * 100);
            const strokeOffset = 283 - (283 * tempPercent / 100);
            document.getElementById('temp-gauge').setAttribute('stroke-dashoffset', strokeOffset);

            // Temperature color and status
            let tempClass = 'temp-cold';
            let tempStatus = '✅ FROID';
            let tempColor = '#48dbfb';

            if (temp >= 92) {
                tempClass = 'temp-critical';
                tempStatus = '🚨 URGENCE';
                tempColor = '#ff6b6b';
            } else if (temp >= 88) {
                tempClass = 'temp-critical';
                tempStatus = '🔴 CRITIQUE';
                tempColor = '#ff6b6b';
            } else if (temp >= 83) {
                tempClass = 'temp-hot';
                tempStatus = '🟠 TRÈS CHAUD';
                tempColor = '#ff9f43';
            } else if (temp >= 75) {
                tempClass = 'temp-warm';
                tempStatus = '🟡 CHAUD';
                tempColor = '#feca57';
            } else if (temp >= 65) {
                tempClass = 'temp-normal';
                tempStatus = '🟢 NORMAL';
                tempColor = '#1dd1a1';
            }

            document.getElementById('temp-value').className = 'gauge-value ' + tempClass;
            document.getElementById('temp-status').textContent = tempStatus;
            document.getElementById('temp-gauge').setAttribute('stroke', tempColor);

            // GPU Usage
            document.getElementById('gpu-usage').textContent = data.gpu.usage.toFixed(1) + '%';
            document.getElementById('gpu-usage-bar').style.width = data.gpu.usage + '%';

            const usageColor = data.gpu.usage > 90 ? '#1dd1a1' : data.gpu.usage > 50 ? '#feca57' : '#48dbfb';
            document.getElementById('gpu-usage-bar').style.background = usageColor;

            // Clocks
            document.getElementById('gpu-clock').textContent = data.gpu.clock_speed + ' MHz';
            document.getElementById('mem-clock').textContent = data.gpu.memory_clock + ' MHz';
            document.getElementById('power-draw').textContent = data.gpu.power_draw.toFixed(1) + ' W';

            // VRAM
            const vramUsedGB = (data.gpu.vram_used / 1024).toFixed(1);
            const vramTotalGB = (data.gpu.vram_total / 1024).toFixed(1);
            const vramPercent = (data.gpu.vram_used / data.gpu.vram_total) * 100;
            document.getElementById('vram-used').textContent = vramUsedGB + ' / ' + vramTotalGB + ' GB';
            document.getElementById('vram-bar').style.width = vramPercent + '%';

            // Couleur VRAM selon utilisation
            const vramColor = vramPercent > 90 ? '#ff6b6b' : vramPercent > 70 ? '#feca57' : '#9b59b6';
            document.getElementById('vram-bar').style.background = vramColor;

            // FPS
            document.getElementById('fps-current').textContent = data.fps.current.toFixed(1) + ' FPS';
            document.getElementById('fps-avg').textContent = data.fps.avg.toFixed(1);
            document.getElementById('fps-minmax').textContent = data.fps.min.toFixed(0) + ' / ' + data.fps.max.toFixed(0);
            document.getElementById('fps-1low').textContent = data.fps.fps_1_low.toFixed(1);
            document.getElementById('frametime').textContent = data.fps.frametime_ms.toFixed(1) + ' ms';

            // ML Prediction
            const trendText = {
                'rising': '📈 MONTÉE',
                'stable': '➡️ STABLE',
                'falling': '📉 DESCENTE',
                'unknown': '❓ INCONNU'
            };

            const trendClass = {
                'rising': 'status-danger',
                'stable': 'status-warning',
                'falling': 'status-good',
                'unknown': 'status-warning'
            };

            document.getElementById('ml-trend').textContent = trendText[data.ml.trend] || '❓';
            document.getElementById('ml-trend').className = 'status-badge ' + (trendClass[data.ml.trend] || 'status-warning');

            document.getElementById('pred-5s').textContent = data.ml.predicted_5s.toFixed(1) + '°C';
            document.getElementById('pred-10s').textContent = data.ml.predicted_10s.toFixed(1) + '°C';
            document.getElementById('pred-30s').textContent = data.ml.predicted_30s.toFixed(1) + '°C';

            document.getElementById('spike-prob').textContent = (data.ml.spike_probability * 100).toFixed(0) + '%';
            document.getElementById('ml-confidence').textContent = (data.ml.confidence * 100).toFixed(0) + '%';

            const actionText = {
                'none': '✅ Aucune action requise',
                'prepare_throttle': '⚠️ Préparer throttle préventif',
                'throttle_now': '🚨 THROTTLE MAINTENANT !'
            };
            document.getElementById('ml-action').textContent = actionText[data.ml.recommended_action] || '❓';

            // Sweet Spot
            if (data.sweet_spot) {
                document.getElementById('sweet-spot-content').innerHTML =
                    '<div class="metric"><span class="metric-label">Clock Optimal</span><span class="metric-value">' +
                    data.sweet_spot.optimal_clock + ' MHz</span></div>' +
                    '<div class="metric"><span class="metric-label">Temp Cible</span><span class="metric-value">' +
                    data.sweet_spot.optimal_temp.toFixed(0) + '°C</span></div>' +
                    '<div class="metric"><span class="metric-label">FPS Attendu</span><span class="metric-value">' +
                    data.sweet_spot.expected_fps.toFixed(1) + '</span></div>' +
                    '<div class="metric"><span class="metric-label">Efficacité</span><span class="metric-value">' +
                    data.sweet_spot.efficiency.toFixed(2) + '</span></div>' +
                    '<div style="margin-top: 10px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 10px;">' +
                    data.sweet_spot.recommendation + '</div>';
            }

            // Optimizations
            const optList = document.getElementById('optimizations');
            if (data.optimizations && data.optimizations.length > 0) {
                optList.innerHTML = data.optimizations.map(opt => '<li>⚙️ ' + opt + '</li>').join('');
            } else {
                optList.innerHTML = '<li style="color: #a0a0a0;">Aucune optimisation active</li>';
            }

            // 📈 Mettre à jour les graphiques
            updateCharts(data);
        }

        // Start connection
        connect();
    </script>
</body>
</html>
`;

// Serveur principal
const server = serve({
  port: 3000,

  fetch(req, server) {
    const url = new URL(req.url);

    // WebSocket upgrade
    if (url.pathname === "/ws") {
      const success = server.upgrade(req);
      if (success) {
        return undefined;
      }
      return new Response("WebSocket upgrade failed", { status: 400 });
    }

    // API REST
    if (url.pathname === "/api/data") {
      return new Response(JSON.stringify(currentData || {}), {
        headers: { "Content-Type": "application/json" }
      });
    }

    if (url.pathname === "/api/history") {
      return new Response(JSON.stringify(dataHistory), {
        headers: { "Content-Type": "application/json" }
      });
    }

    // POST pour recevoir les données de l'optimiseur Python
    if (url.pathname === "/api/update" && req.method === "POST") {
      return req.json().then((data: DashboardData) => {
        currentData = data;
        dataHistory.push(data);

        if (dataHistory.length > MAX_HISTORY) {
          dataHistory.shift();
        }

        // Broadcast to all WebSocket clients
        for (const client of wsClients) {
          client.send(JSON.stringify(data));
        }

        return new Response(JSON.stringify({ success: true }), {
          headers: { "Content-Type": "application/json" }
        });
      });
    }

    // Dashboard HTML
    if (url.pathname === "/" || url.pathname === "/index.html") {
      return new Response(dashboardHTML, {
        headers: { "Content-Type": "text/html" }
      });
    }

    return new Response("Not Found", { status: 404 });
  },

  websocket: {
    open(ws) {
      wsClients.add(ws);
      console.log("🔌 Client WebSocket connecté");

      // Envoyer les données actuelles si disponibles
      if (currentData) {
        ws.send(JSON.stringify(currentData));
      }
    },

    close(ws) {
      wsClients.delete(ws);
      console.log("🔌 Client WebSocket déconnecté");
    },

    message(ws, message) {
      // Handle ping/pong or commands
      if (message === "ping") {
        ws.send("pong");
      }
    }
  }
});

console.log("=" .repeat(60));
console.log("🔥 TEMPLE IAM DASHBOARD SERVER");
console.log("=" .repeat(60));
console.log("📡 Serveur démarré sur http://localhost:3000");
console.log("🔌 WebSocket disponible sur ws://localhost:3000/ws");
console.log("📊 API REST:");
console.log("   GET  /api/data    - Données actuelles");
console.log("   GET  /api/history - Historique");
console.log("   POST /api/update  - Mise à jour (depuis Python)");
console.log("=" .repeat(60));
console.log("💡 Ouvre http://localhost:3000 dans ton navigateur");
console.log("💡 Lance l'optimiseur Python pour voir les données");
console.log("=" .repeat(60));
