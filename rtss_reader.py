"""Correct RTSS (RivaTuner Statistics Server) shared-memory FPS reader.

RTSS ships with MSI Afterburner and publishes a shared memory block named
'RTSSSharedMemoryV2' with one entry per hooked application. Each entry holds a
frame counter and a time window, so the FPS of a hooked app is:

    FPS = dwFrames * 1000 / (dwTime1 - dwTime0)

This module attaches to the EXISTING mapping via the Win32 OpenFileMapping API
and parses the documented RTSS_SHARED_MEMORY_APP_ENTRY layout. It replaces the
earlier broken approach (mmap(-1, ...), which CREATES a fresh empty block
instead of attaching, then read a float at a guessed offset).

Requires RTSS to be running and the target game/app to be hooked by it.
"""

import logging
from typing import List, Optional, Tuple

_FILE_MAP_READ = 0x0004
_SIGNATURE = 0x52545353  # 'RTSS'
# byte offsets inside RTSS_SHARED_MEMORY_APP_ENTRY
_OFF_NAME, _OFF_TIME0, _OFF_TIME1, _OFF_FRAMES = 4, 268, 272, 276


class RTSSReader:
    """Reads real per-application FPS from RTSS shared memory (read-only)."""

    def __init__(self):
        self._addr = None
        self._ctypes = None
        self._entry_size = self._arr_off = self._arr_size = 0
        self._attach()

    def _attach(self):
        try:
            import ctypes
            from ctypes import wintypes
        except Exception as e:  # non-Windows / no ctypes
            logging.info(f"RTSS reader indisponible (ctypes): {e}")
            return
        try:
            k = ctypes.windll.kernel32
            k.OpenFileMappingW.restype = wintypes.HANDLE
            k.OpenFileMappingW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
            k.MapViewOfFile.restype = ctypes.c_void_p
            k.MapViewOfFile.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                        wintypes.DWORD, wintypes.DWORD, ctypes.c_size_t]
            h = k.OpenFileMappingW(_FILE_MAP_READ, False, "RTSSSharedMemoryV2")
            if not h:
                logging.info("RTSS non detecte (lancez MSI Afterburner / RTSS)")
                return
            addr = k.MapViewOfFile(h, _FILE_MAP_READ, 0, 0, 0)
            if not addr:
                return
            hdr = (ctypes.c_uint32 * 8).from_address(addr)
            if hdr[0] != _SIGNATURE:
                logging.info(f"RTSS signature inattendue: {hex(hdr[0])}")
                return
            self._ctypes = ctypes
            self._addr = addr
            self._entry_size, self._arr_off, self._arr_size = hdr[2], hdr[3], hdr[4]
            logging.info(f"RTSS detecte: {self._arr_size} slots d'app")
        except Exception as e:
            logging.info(f"RTSS indisponible: {e}")

    @property
    def available(self) -> bool:
        return self._addr is not None

    def read_all(self) -> List[Tuple[int, str, float]]:
        """Return (pid, exe_name, fps) for every currently hooked app."""
        if not self._addr:
            return []
        c = self._ctypes
        out: List[Tuple[int, str, float]] = []
        for i in range(self._arr_size):
            base = self._addr + self._arr_off + i * self._entry_size
            pid = c.c_uint32.from_address(base).value
            if pid == 0:
                continue
            name = c.string_at(base + _OFF_NAME, 260).split(b"\x00")[0].decode("ascii", "replace")
            t0 = c.c_uint32.from_address(base + _OFF_TIME0).value
            t1 = c.c_uint32.from_address(base + _OFF_TIME1).value
            frames = c.c_uint32.from_address(base + _OFF_FRAMES).value
            fps = frames * 1000.0 / (t1 - t0) if t1 > t0 else 0.0
            out.append((pid, name, fps))
        return out

    def read_max_fps(self, name_filter: Optional[str] = None) -> float:
        """Highest FPS among currently hooked apps (0.0 if none/unavailable).

        name_filter: optional substring of the exe name to target one app.
        """
        best = 0.0
        for _pid, name, fps in self.read_all():
            if name_filter and name_filter.lower() not in name.lower():
                continue
            best = max(best, fps)
        return best
