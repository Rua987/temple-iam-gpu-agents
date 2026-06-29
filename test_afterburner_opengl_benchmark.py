"""Benchmark OpenGL 3D/shader pour valider MSI Afterburner profile1/profile2.

Ce test force un vrai rendu GPU (fragment shader lourd en 1080p), compare
stock/secours (profile1) et undervolt (profile2), puis remet toujours profile1.
"""

import csv
import json
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

import glfw
import moderngl


AFTERBURNER = Path(r"C:\Program Files (x86)\MSI Afterburner\MSIAfterburner.exe")
REPORT_PATH = Path("afterburner_opengl_benchmark_results.json")


VERTEX_SHADER = """
#version 330
in vec2 in_pos;
out vec2 uv;
void main() {
    uv = in_pos * 0.5 + 0.5;
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
"""


FRAGMENT_SHADER = """
#version 330
in vec2 uv;
out vec4 fragColor;
uniform float t;

float mandel(vec2 c) {
    vec2 z = vec2(0.0);
    float m = 0.0;
    for (int i = 0; i < 360; i++) {
        z = vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;
        if (dot(z, z) > 16.0) break;
        m += 1.0;
    }
    return m / 360.0;
}

void main() {
    vec2 p = (uv - 0.5) * vec2(3.2, 1.8);
    float zoom = 0.75 + 0.08 * sin(t * 0.3);
    vec2 c0 = vec2(-0.7435, 0.1314) + p * zoom;
    float acc = 0.0;

    // Plusieurs echantillons decales : charge shader proche d'un rendu lourd.
    for (int j = 0; j < 6; j++) {
        float a = float(j) * 1.047 + t * 0.02;
        vec2 off = 0.0015 * vec2(cos(a), sin(a));
        acc += mandel(c0 + off);
    }

    float v = acc / 6.0;
    vec3 col = vec3(v*v, pow(v, 0.65), 1.0 - v);
    fragColor = vec4(col, 1.0);
}
"""


def run(cmd, timeout=10):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def apply_profile(slot: int) -> bool:
    result = run([str(AFTERBURNER), f"-profile{slot}"], timeout=10)
    time.sleep(4)
    return result.returncode == 0


def gpu_sample():
    fields = "clocks.gr,clocks.mem,temperature.gpu,utilization.gpu,power.draw,memory.used"
    result = run(["nvidia-smi", f"--query-gpu={fields}", "--format=csv,noheader,nounits"], timeout=5)
    row = next(csv.reader([result.stdout.strip()]))
    return {
        "clock_mhz": float(row[0].strip()),
        "mem_clock_mhz": float(row[1].strip()),
        "temp_c": float(row[2].strip()),
        "util_percent": float(row[3].strip()),
        "power_w": float(row[4].strip()),
        "memory_mb": float(row[5].strip()),
    }


def summarize(samples):
    active = [s for s in samples if s["util_percent"] >= 60] or samples
    return {
        "samples": len(samples),
        "active_samples": len(active),
        "clock_avg": round(sum(s["clock_mhz"] for s in active) / len(active), 1),
        "clock_max": max(s["clock_mhz"] for s in active),
        "temp_min": min(s["temp_c"] for s in active),
        "temp_max": max(s["temp_c"] for s in active),
        "power_avg": round(sum(s["power_w"] for s in active) / len(active), 2),
        "util_avg": round(sum(s["util_percent"] for s in active) / len(active), 1),
        "fps_avg": round(sum(s["fps"] for s in active) / len(active), 1),
    }


def render_worker(seconds: int, stop_event: threading.Event, perf: dict):
    if not glfw.init():
        perf["error"] = "glfw.init failed"
        return

    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    window = glfw.create_window(640, 360, "Temple IAM OpenGL Benchmark", None, None)
    if not window:
        perf["error"] = "glfw.create_window failed"
        glfw.terminate()
        return

    try:
        glfw.make_context_current(window)
        glfw.swap_interval(0)
        ctx = moderngl.create_context()
        ctx.viewport = (0, 0, 1920, 1080)

        prog = ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)
        vertices = ctx.buffer(b"".join([
            (-1.0).hex().encode(), b" "
        ]))
        # Binary float buffer keeps dependencies minimal.
        import struct
        vbo = ctx.buffer(struct.pack("12f", -1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1))
        vao = ctx.vertex_array(prog, [(vbo, "2f", "in_pos")])
        tex = ctx.texture((1920, 1080), 4)
        fbo = ctx.framebuffer(color_attachments=[tex])
        fbo.use()

        frames = 0
        last = time.time()
        start = last
        end = start + seconds

        while time.time() < end and not stop_event.is_set():
            now = time.time()
            prog["t"].value = now - start
            vao.render(moderngl.TRIANGLES)
            ctx.finish()
            frames += 1
            if now - last >= 1.0:
                perf["fps"] = frames / (now - start)
                last = now
    finally:
        glfw.destroy_window(window)
        glfw.terminate()


def run_phase(name: str, slot: int, seconds: int):
    ok = apply_profile(slot)
    print(f"[PHASE] {name}: profile{slot} applique={ok}")

    stop_event = threading.Event()
    perf = {"fps": 0.0}
    worker = threading.Thread(target=render_worker, args=(seconds, stop_event, perf), daemon=True)
    worker.start()
    time.sleep(2)

    samples = []
    try:
        for t in range(seconds):
            sample = gpu_sample()
            sample["phase"] = name
            sample["t"] = t
            sample["fps"] = float(perf.get("fps", 0.0))
            samples.append(sample)
            print(
                f"{name:10s} t={t:02d}s | "
                f"gpu={sample['util_percent']:5.1f}% | "
                f"clock={sample['clock_mhz']:5.0f} MHz | "
                f"temp={sample['temp_c']:4.0f}C | "
                f"power={sample['power_w']:6.1f} W | "
                f"fps={sample['fps']:5.1f}"
            )
            if sample["temp_c"] >= 88:
                print("[SECURITE] Temperature >= 88C, arret de la phase")
                break
            if perf.get("error"):
                print(f"[ERREUR] {perf['error']}")
                break
            time.sleep(1)
    finally:
        stop_event.set()
        worker.join(timeout=5)

    return samples


def main():
    report = {
        "timestamp": datetime.now().isoformat(),
        "renderer": "OpenGL shader 1920x1080",
        "samples": [],
        "phases": {},
    }

    try:
        report["samples"].extend(run_phase("stock", 1, 35))
        time.sleep(10)
        report["samples"].extend(run_phase("undervolt", 2, 35))
    finally:
        apply_profile(1)

    for phase in ("stock", "undervolt"):
        phase_samples = [s for s in report["samples"] if s["phase"] == phase]
        report["phases"][phase] = summarize(phase_samples)

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("[RESUME]")
    for phase, summary in report["phases"].items():
        print(f"{phase}: {summary}")
    print(f"[RAPPORT] {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
