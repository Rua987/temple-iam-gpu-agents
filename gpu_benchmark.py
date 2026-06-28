"""Standardized GPU-bound benchmark for testing auto-tuning without a game.

Renders a GPU-intensive fractal computation in fullscreen, no vsync, so the FPS
directly reflects GPU clock performance. RTSS hooks it like a real game.

Usage:
    python gpu_benchmark.py              # Run indefinitely
    python gpu_benchmark.py 30           # Run for 30 seconds
    python gpu_benchmark.py --sweep      # Run, then auto-tune via gpu_autoresearch
"""

import sys
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

try:
    import glfw
    import moderngl
    import numpy as np
except ImportError as e:
    logging.error(f"Missing dependency: {e}")
    logging.info("Install: pip install moderngl glfw numpy")
    sys.exit(1)


class GPUBenchmark:
    """GPU-intensive fractal renderer, no vsync (GPU-bound)."""

    VERTEX_SHADER = """
    #version 330
    in vec2 p;
    out vec2 uv;
    void main(){
        uv = p * 0.5 + 0.5;
        gl_Position = vec4(p, 0.0, 1.0);
    }
    """

    FRAGMENT_SHADER = """
    #version 330
    in vec2 uv;
    out vec4 f;
    uniform float t;
    void main(){
        vec3 c = vec3(0.0);
        vec2 z = (uv - 0.5) * 3.0;
        // Heavy per-pixel loop: GPU-bound workload
        for(int i = 0; i < 1500; i++){
            z = vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + vec2(sin(t*0.1), cos(t*0.1));
            c += 0.0004 * vec3(sin(z.x), cos(z.y), sin(z.x+z.y));
        }
        f = vec4(abs(c), 1.0);
    }
    """

    def __init__(self, width: int = 1600, height: int = 900):
        self.width, self.height = width, height
        self.ctx = None
        self.window = None
        self.start_time = None

    def init(self):
        """Initialize GLFW window and OpenGL context."""
        if not glfw.init():
            raise RuntimeError("GLFW init failed")
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.FLOATING, glfw.TRUE)  # Always-on-top

        self.window = glfw.create_window(self.width, self.height, "GPU Benchmark", None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Window creation failed")

        glfw.make_context_current(self.window)
        glfw.swap_interval(0)  # No vsync -> GPU-bound

        self.ctx = moderngl.create_context()

        # Compile shader program
        self.prog = self.ctx.program(
            vertex_shader=self.VERTEX_SHADER,
            fragment_shader=self.FRAGMENT_SHADER
        )

        # Quad for fullscreen rendering
        quad_data = np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype='f4')
        quad_buf = self.ctx.buffer(quad_data)
        self.vao = self.ctx.simple_vertex_array(self.prog, quad_buf, 'p')

        self.start_time = time.time()
        logging.info(f"Benchmark initialized: {self.width}x{self.height} fullscreen, no vsync")

    def render_frame(self):
        """Render one frame."""
        if not self.window or not self.ctx:
            return False

        elapsed = time.time() - self.start_time
        self.prog["t"].value = elapsed

        self.ctx.clear()
        self.vao.render(moderngl.TRIANGLE_STRIP)
        glfw.swap_buffers(self.window)
        glfw.poll_events()

        return not glfw.window_should_close(self.window)

    def run(self, duration_s: float = 0):
        """Run for duration_s seconds (0 = infinite until window close)."""
        try:
            self.init()
            frame_count = 0
            loop_start = time.time()

            while True:
                if not self.render_frame():
                    break
                frame_count += 1

                if duration_s > 0 and time.time() - loop_start >= duration_s:
                    break

            elapsed = time.time() - self.start_time
            fps_avg = frame_count / elapsed if elapsed > 0 else 0
            logging.info(f"Benchmark complete: {frame_count} frames in {elapsed:.1f}s = {fps_avg:.1f} fps avg")
            return fps_avg

        finally:
            if self.window:
                glfw.destroy_window(self.window)
            glfw.terminate()

    def run_with_tuning(self, duration_per_sweep: float = 30.0):
        """Run benchmark, then auto-tune via gpu_autoresearch."""
        try:
            import gpu_autoresearch
            from rtss_reader import RTSSReader
        except ImportError:
            logging.error("gpu_autoresearch or rtss_reader not available")
            self.run(duration_per_sweep)
            return

        logging.info(f"Running benchmark with auto-tuning (RTSS must be running)")
        self.init()

        # Warm-up
        logging.info("Warm-up rendering (5s)...")
        loop_start = time.time()
        while time.time() - loop_start < 5:
            if not self.render_frame():
                return

        # Setup RTSS FPS provider
        rtss = RTSSReader()
        if not rtss.available:
            logging.warning("RTSS not detected - running without real FPS tuning")
            self.run(duration_per_sweep)
            return

        perf_provider = lambda: rtss.read_max_fps()

        # Minimize window during tuning so GPU is free
        glfw.hide_window(self.window)

        try:
            optimal_mhz = gpu_autoresearch.auto_tune_workload(
                "gpu_benchmark",
                perf_provider=perf_provider,
                perf_unit="fps",
                is_gaming=True,
                duration_s=duration_per_sweep
            )

            if optimal_mhz:
                logging.info(f"✅ Optimal clock: {optimal_mhz} MHz")
            else:
                logging.warning("Auto-tuning inconclusive")
        finally:
            if self.window:
                glfw.destroy_window(self.window)
            glfw.terminate()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="GPU-bound benchmark for auto-tuning validation")
    parser.add_argument("duration", nargs="?", type=float, default=0, help="Run duration (s), 0=infinite")
    parser.add_argument("--sweep", action="store_true", help="Run with auto-tuning sweep")
    args = parser.parse_args()

    bench = GPUBenchmark()
    if args.sweep:
        bench.run_with_tuning(duration_per_sweep=30.0)
    else:
        bench.run(duration_s=args.duration)
