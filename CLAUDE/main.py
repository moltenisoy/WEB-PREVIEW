import sys
import ctypes


def _single_instance():
    try:
        mutex = ctypes.windll.kernel32.CreateMutexW(None, 1, "BrowseDash_SingleInstance_Mutex")
        if ctypes.windll.kernel32.GetLastError() == 183:
            ctypes.windll.kernel32.CloseHandle(mutex)
            sys.exit(0)
    except Exception:
        pass


def _hide_console():
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass


def _set_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


if __name__ == "__main__":
    _single_instance()
    _hide_console()
    _set_dpi_awareness()
    from app_core import BrowseDashApp
    app = BrowseDashApp()
    app.run()