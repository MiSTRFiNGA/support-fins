"""Support Fins — HiVEMiND desktop launcher.

Serves ./web (the upstream no-cache dev server handler) on 127.0.0.1:PORT and opens it
in a chromeless Edge/Chrome app window centred on the PRIMARY monitor's work area.

The window gets a dedicated browser profile (_runtime/edge-profile), so the browser
process launched here lives exactly as long as the app's windows: when the last one
closes, the server stops too. A second launch while the app is running finds the port
already answering and just asks the running browser for another window.

Stdlib only — no venv needed.
"""
import ctypes
import functools
import http.server
import importlib.util
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

APP_NAME = "Support Fins"
PORT = 4731                      # claimed in D:\Drive\AI\_shared\port_registry.json
HOST = "127.0.0.1"
WINDOW_W, WINDOW_H = 1500, 950
HERE = Path(__file__).resolve().parent
RUNTIME = HERE / "_runtime"
PROFILE = RUNTIME / "edge-profile"
LOG = RUNTIME / "launch.log"
URL = f"http://localhost:{PORT}/"


def log(msg: str) -> None:
    RUNTIME.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %I:%M:%S %p')}  {msg}\n")


def _load_dev_server():
    """Import the upstream dev-server.py (hyphenated name) to reuse its handler."""
    spec = importlib.util.spec_from_file_location("dev_server", HERE / "dev-server.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Handler(_load_dev_server().NoCacheHandler):
    # Windows' registry can map .js to text/plain, which makes browsers refuse ES
    # modules outright. Pin the types the app depends on.
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript", ".mjs": "text/javascript",
        ".wasm": "application/wasm", ".svg": "image/svg+xml", ".json": "application/json",
    }

    def log_message(self, fmt, *args):
        pass                      # pythonw has no stderr; requests are not worth logging


def port_answers() -> bool:
    try:
        with urllib.request.urlopen(URL, timeout=1.5) as r:
            return r.status == 200
    except Exception:
        return False


def primary_work_area():
    """(x, y, w, h) of the primary monitor minus the taskbar (SPI_GETWORKAREA)."""
    class RECT(ctypes.Structure):
        _fields_ = [("l", ctypes.c_long), ("t", ctypes.c_long),
                    ("r", ctypes.c_long), ("b", ctypes.c_long)]
    rc = RECT()
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        if ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rc), 0):
            return rc.l, rc.t, rc.r - rc.l, rc.b - rc.t
    except Exception as e:
        log(f"work area lookup failed: {e}")
    return 0, 0, 1920, 1040


def centred_geometry(w: int, h: int):
    x0, y0, sw, sh = primary_work_area()
    w, h = min(w, sw), min(h, sh)
    return x0 + max(0, (sw - w) // 2), y0 + max(0, (sh - h) // 2), w, h


def find_browser():
    import winreg
    for exe in ("msedge.exe", "chrome.exe", "brave.exe"):
        for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                with winreg.OpenKey(hive, rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{exe}") as k:
                    path = winreg.QueryValueEx(k, "")[0].strip('"')
                if Path(path).exists():
                    return path
            except OSError:
                pass
    for root in filter(None, (os.environ.get(v) for v in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA"))):
        for suffix in (r"Microsoft\Edge\Application\msedge.exe", r"Google\Chrome\Application\chrome.exe"):
            if (Path(root) / suffix).exists():
                return str(Path(root) / suffix)
    return None


def open_window():
    """Launch the app window; returns the Popen, or None if it fell back to a browser tab."""
    browser = find_browser()
    if not browser:
        log("no Edge/Chrome found; opening the default browser instead")
        webbrowser.open(URL)
        return None
    x, y, w, h = centred_geometry(WINDOW_W, WINDOW_H)
    log(f"window: {browser} at {x},{y} {w}x{h}")
    return subprocess.Popen([
        browser, f"--app={URL}", f"--user-data-dir={PROFILE}",
        f"--window-position={x},{y}", f"--window-size={w},{h}",
        "--no-first-run", "--no-default-browser-check",
    ])


def fail(msg: str) -> None:
    log(f"FATAL {msg}")
    ctypes.windll.user32.MessageBoxW(None, msg, APP_NAME, 0x10)
    sys.exit(1)


def main() -> None:
    if port_answers():
        log("already running; opening another window")
        open_window()
        return
    try:
        server = http.server.ThreadingHTTPServer(
            (HOST, PORT), functools.partial(Handler, directory=str(HERE / "web")))
    except OSError as e:
        fail(f"Port {PORT} is in use by something else, so Support Fins can't start.\n\n{e}")
    threading.Thread(target=server.serve_forever, daemon=True).start()
    log(f"serving {HERE / 'web'} on {URL}")
    if "--no-window" in sys.argv:
        threading.Event().wait()  # serve only, until killed
    proc = open_window()
    if proc is None:              # plain browser tab: no lifetime to track, serve until killed
        threading.Event().wait()
    proc.wait()
    log(f"window closed (exit {proc.returncode}); stopping server")
    server.shutdown()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:      # pythonw discards tracebacks; never fail silently
        import traceback
        log(traceback.format_exc())
        fail(f"Support Fins crashed on launch:\n\n{e}\n\nDetails: {LOG}")
