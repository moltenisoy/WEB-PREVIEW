import threading
import keyboard
import mouse


class BaseTrigger:
    def __init__(self, callback):
        self._callback = callback
        self._active = False

    def start(self):
        self._active = True

    def stop(self):
        self._active = False

    def _fire(self):
        try:
            if self._active and self._callback:
                self._callback()
        except Exception:
            pass


class HotkeyTrigger(BaseTrigger):
    def __init__(self, callback, combo="ctrl+shift+b"):
        super().__init__(callback)
        self._combo = combo
        self._hook = None

    def start(self):
        try:
            super().start()
            self._hook = keyboard.add_hotkey(self._combo, self._fire, suppress=True)
        except Exception:
            pass

    def stop(self):
        try:
            super().stop()
            if self._hook is not None:
                keyboard.remove_hotkey(self._hook)
                self._hook = None
        except Exception:
            pass

    def update_combo(self, new_combo):
        try:
            was_active = self._active
            self.stop()
            self._combo = new_combo
            if was_active:
                self.start()
        except Exception:
            pass


class MouseGestureTrigger(BaseTrigger):
    def __init__(self, callback, gesture_type="double_right"):
        super().__init__(callback)
        self._gesture_type = gesture_type
        self._last_right = 0
        self._hook_registered = False

    def start(self):
        try:
            super().start()
            if not self._hook_registered:
                if self._gesture_type == "double_right":
                    mouse.on_double_click(self._on_mouse_event, buttons=("right",))
                elif self._gesture_type == "middle_click":
                    mouse.on_middle_click(self._on_mouse_event)
                elif self._gesture_type == "side_button":
                    mouse.on_button(self._on_mouse_event, buttons=("x",))
                self._hook_registered = True
        except Exception:
            pass

    def _on_mouse_event(self):
        try:
            self._fire()
        except Exception:
            pass

    def stop(self):
        try:
            super().stop()
            mouse.unhook_all()
            self._hook_registered = False
        except Exception:
            pass


class TriggerManager:
    def __init__(self, show_callback):
        self._show = show_callback
        self._hotkey = None
        self._mouse = None
        self._thread = None

    def setup(self, trigger_config):
        try:
            self.stop_all()
            if trigger_config.hotkey_enabled:
                self._hotkey = HotkeyTrigger(self._show, trigger_config.hotkey_combo)
                self._hotkey.start()
            if trigger_config.mouse_gesture_enabled:
                self._mouse = MouseGestureTrigger(self._show, trigger_config.mouse_gesture_type)
                self._mouse.start()
        except Exception:
            pass

    def stop_all(self):
        try:
            if self._hotkey:
                self._hotkey.stop()
                self._hotkey = None
            if self._mouse:
                self._mouse.stop()
                self._mouse = None
        except Exception:
            pass

    def update_config(self, trigger_config):
        try:
            self.setup(trigger_config)
        except Exception:
            pass