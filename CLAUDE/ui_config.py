import customtkinter as ctk
from storage import get_config, save_config
from models import AppConfig, TriggerConfig


class ConfigWindow(ctk.CTkToplevel):
    def __init__(self, master, on_save_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self._on_save = on_save_callback
        self._config = get_config()
        self._widgets = {}
        self._setup()
        self._build()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup(self):
        try:
            self.title("BrowseDash \u2014 Configuraci\u00f3n")
            self.geometry("520x680")
            self.minsize(480, 600)
            self.resizable(True, True)
        except Exception:
            pass

    def _build(self):
        try:
            header = ctk.CTkFrame(self, fg_color=("#F8FAFC", "#12121A"), height=50)
            header.pack(fill="x")
            header.pack_propagate(False)
            ctk.CTkLabel(
                header,
                text="\u2699\uFE0F  Configuraci\u00f3n",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=("#1E293B", "#F1F5F9"),
            ).pack(side="left", padx=20)
            scroll = ctk.CTkScrollableFrame(self, fg_color=("#F1F5F9", "#0F0F1A"))
            scroll.pack(fill="both", expand=True, padx=0, pady=0)
            self._add_section(scroll, "Apariencia")
            self._add_option_menu(scroll, "Tema", "theme", ["dark", "light"])
            self._add_option_menu(scroll, "Vista", "view_mode", ["thumbnails", "text", "compact"])
            self._add_entry(scroll, "Color de acento", "accent_color", self._config.accent_color)
            self._add_slider(scroll, "Tama\u00f1o de fuente", "font_size", 10, 20, self._config.font_size)
            self._add_section(scroll, "Tarjetas")
            self._add_slider(scroll, "Ancho tarjeta", "card_width", 200, 400, self._config.card_width)
            self._add_slider(scroll, "Alto tarjeta", "card_height", 80, 300, self._config.card_height)
            self._add_slider(scroll, "Columnas", "columns", 1, 8, self._config.columns)
            self._add_slider(scroll, "Espaciado", "card_spacing", 4, 30, self._config.card_spacing)
            self._add_slider(scroll, "Radio borde", "card_border_radius", 0, 24, self._config.card_border_radius)
            self._add_section(scroll, "Datos")
            self._add_slider(scroll, "Sitios a mostrar", "max_sites", 5, 50, self._config.max_sites)
            self._add_slider(scroll, "Actualizar cada (seg)", "refresh_interval", 30, 1800, self._config.refresh_interval)
            self._add_switch(scroll, "Mostrar dominio", "show_domain", self._config.show_domain)
            self._add_switch(scroll, "Mostrar hora", "show_time", self._config.show_time)
            self._add_switch(scroll, "Mostrar favicon", "show_favicon", self._config.show_favicon)
            self._add_section(scroll, "Triggers")
            self._add_switch(scroll, "Atajo de teclado", "hotkey_enabled", self._config.trigger.hotkey_enabled)
            self._add_entry(scroll, "Combinaci\u00f3n de teclas", "hotkey_combo", self._config.trigger.hotkey_combo)
            self._add_switch(scroll, "Clic bandeja", "tray_click_enabled", self._config.trigger.tray_click_enabled)
            self._add_switch(scroll, "Gesto de mouse", "mouse_gesture_enabled", self._config.trigger.mouse_gesture_enabled)
            self._add_option_menu(scroll, "Tipo de gesto", "mouse_gesture_type", ["double_right", "middle_click", "side_button"])
            footer = ctk.CTkFrame(self, fg_color=("#F8FAFC", "#12121A"), height=56)
            footer.pack(fill="x", side="bottom")
            footer.pack_propagate(False)
            save_btn = ctk.CTkButton(
                footer,
                text="\U0001F4BE  Guardar",
                command=self._save,
                fg_color="#3B82F6",
                hover_color="#2563EB",
                corner_radius=8,
                width=140,
                height=36,
                font=ctk.CTkFont(size=13, weight="bold"),
            )
            save_btn.pack(side="right", padx=20, pady=10)
            cancel_btn = ctk.CTkButton(
                footer,
                text="Cancelar",
                command=self._on_close,
                fg_color=("#E2E8F0", "#2D2D3F"),
                hover_color=("#CBD5E1", "#3D3D5C"),
                text_color=("#1E293B", "#E2E8F0"),
                corner_radius=8,
                width=100,
                height=36,
                font=ctk.CTkFont(size=13),
            )
            cancel_btn.pack(side="right", padx=5, pady=10)
        except Exception:
            pass

    def _add_section(self, parent, title):
        try:
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=(16, 4))
            ctk.CTkLabel(
                f,
                text=title,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("#3B82F6", "#60A5FA"),
            ).pack(anchor="w")
            sep = ctk.CTkFrame(parent, fg_color=("#CBD5E1", "#2D2D3F"), height=1)
            sep.pack(fill="x", padx=20, pady=(0, 8))
        except Exception:
            pass

    def _add_slider(self, parent, label, key, from_, to_, value):
        try:
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(fill="x", padx=24, pady=3)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=12), anchor="w", width=180).pack(side="left")
            val_label = ctk.CTkLabel(f, text=str(int(value)), font=ctk.CTkFont(size=12), width=40)
            val_label.pack(side="right", padx=(5, 0))
            slider = ctk.CTkSlider(
                f, from_=from_, to=to_, number_of_steps=to_ - from_,
                command=lambda v, vl=val_label: vl.configure(text=str(int(v))),
                width=180,
            )
            slider.set(value)
            slider.pack(side="right")
            self._widgets[key] = slider
        except Exception:
            pass

    def _add_switch(self, parent, label, key, value):
        try:
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(fill="x", padx=24, pady=3)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=12), anchor="w", width=180).pack(side="left")
            var = ctk.BooleanVar(value=value)
            sw = ctk.CTkSwitch(f, text="", variable=var, onvalue=True, offvalue=False)
            sw.pack(side="right")
            self._widgets[key] = var
        except Exception:
            pass

    def _add_entry(self, parent, label, key, value):
        try:
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(fill="x", padx=24, pady=3)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=12), anchor="w", width=180).pack(side="left")
            entry = ctk.CTkEntry(f, width=180)
            entry.insert(0, str(value))
            entry.pack(side="right")
            self._widgets[key] = entry
        except Exception:
            pass

    def _add_option_menu(self, parent, label, key, values):
        try:
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(fill="x", padx=24, pady=3)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=12), anchor="w", width=180).pack(side="left")
            current = getattr(self._config, key, None)
            if current is None:
                current = getattr(self._config.trigger, key, values[0])
            var = ctk.StringVar(value=str(current))
            menu = ctk.CTkOptionMenu(f, variable=var, values=values, width=180)
            menu.pack(side="right")
            self._widgets[key] = var
        except Exception:
            pass

    def _get_value(self, key):
        try:
            w = self._widgets.get(key)
            if w is None:
                return None
            if isinstance(w, ctk.CTkSlider):
                return int(w.get())
            if isinstance(w, ctk.BooleanVar):
                return w.get()
            if isinstance(w, ctk.StringVar):
                return w.get()
            if isinstance(w, ctk.CTkEntry):
                return w.get()
        except Exception:
            pass
        return None

    def _save(self):
        try:
            v_hotkey_enabled = self._get_value("hotkey_enabled")
            v_tray_click = self._get_value("tray_click_enabled")
            v_mouse_gesture = self._get_value("mouse_gesture_enabled")
            v_show_domain = self._get_value("show_domain")
            v_show_time = self._get_value("show_time")
            v_show_favicon = self._get_value("show_favicon")
            trigger = TriggerConfig(
                hotkey_enabled=v_hotkey_enabled if v_hotkey_enabled is not None else True,
                hotkey_combo=self._get_value("hotkey_combo") or "ctrl+shift+b",
                tray_click_enabled=v_tray_click if v_tray_click is not None else True,
                mouse_gesture_enabled=v_mouse_gesture if v_mouse_gesture is not None else False,
                mouse_gesture_type=self._get_value("mouse_gesture_type") or "double_right",
                desktop_shortcut_enabled=True,
            )
            config = AppConfig(
                card_width=self._get_value("card_width") or 280,
                card_height=self._get_value("card_height") or 160,
                columns=self._get_value("columns") or 4,
                max_sites=self._get_value("max_sites") or 20,
                refresh_interval=self._get_value("refresh_interval") or 300,
                view_mode=self._get_value("view_mode") or "thumbnails",
                theme=self._get_value("theme") or "dark",
                accent_color=self._get_value("accent_color") or "#3B82F6",
                card_border_radius=self._get_value("card_border_radius") or 12,
                card_spacing=self._get_value("card_spacing") or 10,
                font_size=self._get_value("font_size") or 13,
                show_domain=v_show_domain if v_show_domain is not None else True,
                show_time=v_show_time if v_show_time is not None else True,
                show_favicon=v_show_favicon if v_show_favicon is not None else True,
                trigger=trigger,
            )
            save_config(config)
            if self._on_save:
                self._on_save()
            self.destroy()
        except Exception:
            pass

    def _on_close(self):
        try:
            self.destroy()
        except Exception:
            pass