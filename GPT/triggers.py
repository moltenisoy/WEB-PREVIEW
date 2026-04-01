import keyboard


class TriggerManager:
    def __init__(self):
        self.handlers = {}
        self.callback = None

    def set_callback(self, cb):
        self.callback = cb

    def register_hotkey(self, combo):
        if combo in self.handlers:
            self.unregister_hotkey(combo)
        h = keyboard.add_hotkey(combo, self.callback)
        self.handlers[combo] = h

    def unregister_hotkey(self, combo):
        if combo in self.handlers:
            keyboard.remove_hotkey(self.handlers[combo])
            del self.handlers[combo]

    def unregister_all(self):
        for combo in list(self.handlers.keys()):
            self.unregister_hotkey(combo)