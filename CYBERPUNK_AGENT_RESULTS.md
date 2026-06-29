# GPU Agent — résultats Cyberpunk 2077 (RTX 2070 laptop)

Validation de l'agent GPU sur charge AAA réelle, et de l'orchestration d'upscaler
externe. Machine : RTX 2070 mobile 8 GB · i7-8750H · Windows 11 · 1920×1080.

## 1. FPS mesurés (Cyberpunk 2077 v2.0, benchmark intégré)

| Config | Résolution | FPS moy. | Mécanisme du gain |
|---|---|---|---|
| Path tracing natif | 1080p | **2.4 – 5.3** | aucune aide (charge max) |
| RT Ultra (sans path tracing) | 1080p | **15.7 – 15.9** | path tracing désactivé |
| **Path tracing + DLSS Perf Ultra + Ray Reconstruction** | 1080p | **24.5** | render interne ~1/9 + motion vectors |
| **Path tracing 720p + Magpie (FSR)** | 720p→1080p | **10.8** | render bas (×2.3 moins de pixels) + upscale externe |

Lectures clés :
- **DLSS in-game gagne** (24.5) : il rend encore plus bas en interne ET reconstruit
  avec les vrais **motion vectors** du moteur — inaccessibles de l'extérieur.
- **Magpie double largement** (4.3 → 10.8, ×2.5) **sans** le DLSS du jeu : le gain
  vient de la résolution interne baissée, Magpie remonte en plein écran via FSR.
- Magpie = l'option « DLSS-like sans le DLSS du jeu » → utile surtout sur les jeux
  **qui n'ont pas** DLSS. Sur Cyberpunk (qui l'a), DLSS reste supérieur.

## 2. Pourquoi l'agent ne peut PAS reproduire DLSS

DLSS s'exécute **dans le moteur de rendu**, alimenté à chaque frame par trois
buffers que seul le jeu possède : frame basse-rés jitterée, **depth buffer**,
**motion vectors**. Un process externe peut hooker l'API graphique (D3D12/Vulkan)
et obtenir le depth (fragile), mais **pas les motion vectors réels** — seulement
les *estimer* par optical flow (lossy, artefacts). NVIDIA n'expose aucune API pour
piloter DLSS sur un jeu qui ne l'a pas intégré. → l'agent **orchestre** un upscaler
externe (Magpie/Lossless Scaling), il ne reconstruit pas DLSS.

## 3. Action thermique de l'agent (validée en live)

Le scorer (`PerformanceScorer`) pilote une action réelle via
`WorkloadThermalController.apply_thermal_strategy()` :

| Stratégie scorer | Action GPU réelle | Vu en live |
|---|---|---|
| `thermal_focus` | cap **critical** (1200 MHz) | ✅ à 84°C → `cap pilote: critical` |
| `emergency_throttle` / temp ≥ cible+5 | cap **heavy_cool** (900 MHz) | ✅ |
| temp ≤ cible−3 | relâche, reset clocks | ✅ |

Override d'urgence : ne se relâche pas quand un process « stock » (Edge/Ollama)
clignote en principal. La garde thermique a tenu le GPU sur des benchmarks de
200 s+ à charge max sur un laptop — la vraie valeur de l'agent : **fiabilité sous
charge soutenue**, pas un gain de FPS.

## 4. Gating strict gaming vs training

Les features gaming (vrais FPS RTSS, conseiller upscaling, orchestration Magpie)
sont **strictement gatées** sur `category == "gaming"`. Pour `local_ai` (Ollama,
entraînement GPT-2 from-scratch), l'agent reste **purement thermique** — aucun
upscaler, aucun conseil DLSS. L'argument transférable : si une RTX 2070 laptop
tient Cyberpunk path-tracé sous gestion thermique, un GPT-2 from-scratch tient sur
un meilleur hardware cloud (Vast.ai) — c'est l'agent **thermique** qui transfère,
pas l'upscaling (spécifique au jeu).

## 5. Clocks optimaux par workload (rappel)

| Workload | Optimal | Pourquoi |
|---|---|---|
| Inférence LLM (memory-bound) | ~1200 MHz | la bande passante limite, pas le core |
| Gaming compute-bound | ~1700 MHz | sweet spot perf/°C |
| Path tracing (charge max) | cap thermique | survie > FPS bruts |
