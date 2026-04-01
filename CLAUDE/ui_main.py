import customtkinter as ctk
import threading
from ui_cards import SiteCard, LoadingCard, EmptyStateCard, ErrorStateCard
from svc_browser import get_browser_history
from svc_favicon import get_favicon_for_entries
from storage import get_config


class MainWindow(ctk.CTkToplevel):
    def __init__(self, master, open_config_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self._config = get_config()
        self._open_config_cb = open_config_callback
        self._entries = []
        self._cards = []
        self._auto_refresh_id = None
        self._setup_window()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(100, self._load_data)

    def _setup_window(self):
        try:
            self.title("BrowseDash")
            w = min(self._config.columns * (self._config.card_width + self._config.card_spacing) + 60, 1600)
            h = 720
            self.geometry(f"{w}x{h}")
            self.minsize(600, 400)
            ctk.set_appearance_mode("dark" if self._config.theme == "dark" else "light")
        except Exception:
            pass

    def _build_ui(self):
        try:
            header = ctk.CTkFrame(self, fg_color=("#F8FAFC", "#12121A"), height=56)
            header.pack(fill="x", side="top")
            header.pack_propagate(False)
            title = ctk.CTkLabel(
                header,
                text="\U0001F310  BrowseDash",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=("#1E293B", "#F1F5F9"),
            )
            title.pack(side="left", padx=20)
            btn_frame = ctk.CTkFrame(header, fg_color="transparent")
            btn_frame.pack(side="right", padx=15)
            refresh_btn = ctk.CTkButton(
                btn_frame,
                text="\U0001F504 Actualizar",
                command=self._load_data,
                fg_color=self._config.accent_color,
                hover_color="#2563EB",
                corner_radius=8,
                width=110,
                height=32,
                font=ctk.CTkFont(size=12),
            )
            refresh_btn.pack(side="left", padx=5)
            config_btn = ctk.CTkButton(
                btn_frame,
                text="\u2699\uFE0F Config",
                command=self._open_config,
                fg_color=("#E2E8F0", "#2D2D3F"),
                hover_color=("#CBD5E1", "#3D3D5C"),
                text_color=("#1E293B", "#E2E8F0"),
                corner_radius=8,
                width=90,
                height=32,
                font=ctk.CTkFont(size=12),
            )
            config_btn.pack(side="left", padx=5)
            view_var = ctk.StringVar(value=self._config.view_mode)
            view_seg = ctk.CTkSegmentedButton(
                btn_frame,
                values=["thumbnails", "text", "compact"],
                variable=view_var,
                command=self._change_view,
                font=ctk.CTkFont(size=11),
                height=30,
            )
            view_seg.pack(side="left", padx=(10, 0))
            self._scroll = ctk.CTkScrollableFrame(
                self,
                fg_color=("#F1F5F9", "#0F0F1A"),
                corner_radius=0,
            )
            self._scroll.pack(fill="both", expand=True, padx=0, pady=0)
            self._content_frame = self._scroll
        except Exception:
            pass

    def _open_config(self):
        try:
            if self._open_config_cb:
                self._open_config_cb()
        except Exception:
            pass

    def _change_view(self, value):
        try:
            self._config.view_mode = value
            from storage import save_config
            save_config(self._config)
            self._render_cards()
        except Exception:
            pass

    def _load_data(self):
        try:
            self._show_loading()
            t = threading.Thread(target=self._fetch_history, daemon=True)
            t.start()
        except Exception:
            pass

    def _fetch_history(self):
        try:
            self._config = get_config()
            entries = get_browser_history(self._config.max_sites)
            entries = get_favicon_for_entries(entries)
            self._entries = entries
            self.after(0, self._render_cards)
        except Exception:
            self.after(0, self._show_error)

    def _clear_content(self):
        try:
            for w in self._content_frame.winfo_children():
                w.destroy()
            self._cards = []
        except Exception:
            pass

    def _show_loading(self):
        try:
            self._clear_content()
            for i in range(min(8, self._config.max_sites)):
                card = LoadingCard(self._content_frame, self._config)
                card.grid(
                    row=i // self._config.columns,
                    column=i % self._config.columns,
                    padx=self._config.card_spacing // 2,
                    pady=self._config.card_spacing // 2,
                )
        except Exception:
            pass

    def _show_error(self):
        try:
            self._clear_content()
            err = ErrorStateCard(self._content_frame, retry_callback=self._load_data)
            err.pack(fill="both", expand=True, padx=40, pady=40)
        except Exception:
            pass

    def _render_cards(self):
        try:
            self._clear_content()
            c = self._config
            if not self._entries:
                empty = EmptyStateCard(self._content_frame)
                empty.pack(fill="both", expand=True, padx=40, pady=40)
                self._schedule_refresh()
                return
            for i in self._content_frame.grid_slaves():
                i.destroy()
            cols = c.columns
            for idx, entry in enumerate(self._entries):
                card = SiteCard(self._content_frame, entry, c)
                row = idx // cols
                col = idx % cols
                card.grid(
                    row=row,
                    column=col,
                    padx=c.card_spacing // 2,
                    pady=c.card_spacing // 2,
                    sticky="nsew",
                )
                self._cards.append(card)
            for col in range(cols):
                self._content_frame.grid_columnconfigure(col, weight=1)
            self._schedule_refresh()
        except Exception:
            pass

    def _schedule_refresh(self):
        try:
            if self._auto_refresh_id:
                self.after_cancel(self._auto_refresh_id)
            interval = max(self._config.refresh_interval, 30) * 1000
            self._auto_refresh_id = self.after(interval, self._load_data)
        except Exception:
            pass

    def refresh_config(self):
        try:
            self._config = get_config()
            ctk.set_appearance_mode("dark" if self._config.theme == "dark" else "light")
            self._render_cards()
        except Exception:
            pass

    def _on_close(self):
        try:
            if self._auto_refresh_id:
                self.after_cancel(self._auto_refresh_id)
            self.withdraw()
        except Exception:
            pass

    def show(self):
        try:
            self.deiconify()
            self.lift()
            self.focus_force()
        except Exception:
            pass