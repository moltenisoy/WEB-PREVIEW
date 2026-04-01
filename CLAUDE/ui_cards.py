import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import os
import webbrowser


class SiteCard(ctk.CTkFrame):
    def __init__(self, master, entry, config, **kwargs):
        super().__init__(
            master,
            corner_radius=config.card_border_radius,
            fg_color=("#FFFFFF", "#1E1E2E"),
            border_width=1,
            border_color=("#E2E8F0", "#2D2D3F"),
            **kwargs,
        )
        self._entry = entry
        self._config = config
        self._build()
        self.bind("<Double-Button-1>", self._on_double_click)

    def _build(self):
        try:
            for w in self.winfo_children():
                w.destroy()
        except Exception:
            pass
        c = self._config
        e = self._entry
        self.configure(width=c.card_width, height=c.card_height)
        mode = c.view_mode
        if mode == "thumbnails":
            self._build_thumbnail_view(e, c)
        elif mode == "compact":
            self._build_compact_view(e, c)
        else:
            self._build_text_view(e, c)

    def _build_thumbnail_view(self, e, c):
        try:
            top = ctk.CTkFrame(self, fg_color="transparent", height=40)
            top.pack(fill="x", padx=12, pady=(10, 4))
            top.pack_propagate(False)
            if c.show_favicon and e.favicon_path and os.path.exists(e.favicon_path):
                try:
                    img = Image.open(e.favicon_path).resize((24, 24), Image.LANCZOS)
                    photo = ctk.CTkImage(light_image=img, dark_image=img, size=(24, 24))
                    lbl = ctk.CTkLabel(top, image=photo, text="")
                    lbl.image = photo
                    lbl.pack(side="left", padx=(0, 8))
                    lbl.bind("<Double-Button-1>", self._on_double_click)
                except Exception:
                    pass
            if c.show_domain:
                d = ctk.CTkLabel(
                    top,
                    text=e.domain[:35],
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=c.accent_color,
                    anchor="w",
                )
                d.pack(side="left", fill="x", expand=True)
                d.bind("<Double-Button-1>", self._on_double_click)
            mid = ctk.CTkFrame(self, fg_color="transparent")
            mid.pack(fill="both", expand=True, padx=12, pady=2)
            t = ctk.CTkLabel(
                mid,
                text=e.title[:60] if e.title else e.url[:60],
                font=ctk.CTkFont(size=c.font_size),
                text_color=("#1A1A2E", "#E2E8F0"),
                anchor="nw",
                wraplength=c.card_width - 40,
                justify="left",
            )
            t.pack(fill="both", expand=True)
            t.bind("<Double-Button-1>", self._on_double_click)
            if c.show_time and e.visit_time:
                bot = ctk.CTkFrame(self, fg_color="transparent", height=22)
                bot.pack(fill="x", padx=12, pady=(0, 8))
                bot.pack_propagate(False)
                tl = ctk.CTkLabel(
                    bot,
                    text=e.visit_time,
                    font=ctk.CTkFont(size=10),
                    text_color=("#94A3B8", "#64748B"),
                    anchor="e",
                )
                tl.pack(side="right")
                tl.bind("<Double-Button-1>", self._on_double_click)
        except Exception:
            pass

    def _build_text_view(self, e, c):
        try:
            f = ctk.CTkFrame(self, fg_color="transparent")
            f.pack(fill="both", expand=True, padx=12, pady=10)
            t = ctk.CTkLabel(
                f,
                text=e.title[:80] if e.title else e.url[:80],
                font=ctk.CTkFont(size=c.font_size, weight="bold"),
                text_color=("#1A1A2E", "#E2E8F0"),
                anchor="nw",
                wraplength=c.card_width - 30,
                justify="left",
            )
            t.pack(fill="x")
            t.bind("<Double-Button-1>", self._on_double_click)
            u = ctk.CTkLabel(
                f,
                text=e.url[:70],
                font=ctk.CTkFont(size=10),
                text_color=c.accent_color,
                anchor="nw",
                wraplength=c.card_width - 30,
            )
            u.pack(fill="x", pady=(4, 0))
            u.bind("<Double-Button-1>", self._on_double_click)
            if c.show_time and e.visit_time:
                tl = ctk.CTkLabel(
                    f,
                    text=e.visit_time,
                    font=ctk.CTkFont(size=10),
                    text_color=("#94A3B8", "#64748B"),
                    anchor="nw",
                )
                tl.pack(fill="x", pady=(4, 0))
                tl.bind("<Double-Button-1>", self._on_double_click)
        except Exception:
            pass

    def _build_compact_view(self, e, c):
        try:
            f = ctk.CTkFrame(self, fg_color="transparent")
            f.pack(fill="both", expand=True, padx=8, pady=6)
            self.configure(height=50)
            if c.show_favicon and e.favicon_path and os.path.exists(e.favicon_path):
                try:
                    img = Image.open(e.favicon_path).resize((16, 16), Image.LANCZOS)
                    photo = ctk.CTkImage(light_image=img, dark_image=img, size=(16, 16))
                    lbl = ctk.CTkLabel(f, image=photo, text="")
                    lbl.image = photo
                    lbl.pack(side="left", padx=(0, 6))
                    lbl.bind("<Double-Button-1>", self._on_double_click)
                except Exception:
                    pass
            t = ctk.CTkLabel(
                f,
                text=(e.title[:45] if e.title else e.domain[:45]),
                font=ctk.CTkFont(size=12),
                text_color=("#1A1A2E", "#E2E8F0"),
                anchor="w",
            )
            t.pack(side="left", fill="x", expand=True)
            t.bind("<Double-Button-1>", self._on_double_click)
            if c.show_domain:
                d = ctk.CTkLabel(
                    f,
                    text=e.domain[:25],
                    font=ctk.CTkFont(size=10),
                    text_color=("#94A3B8", "#64748B"),
                    anchor="e",
                )
                d.pack(side="right", padx=(8, 0))
                d.bind("<Double-Button-1>", self._on_double_click)
        except Exception:
            pass

    def _on_double_click(self, event=None):
        try:
            webbrowser.open(self._entry.url)
        except Exception:
            pass

    def update_entry(self, entry, config):
        self._entry = entry
        self._config = config
        self._build()


class LoadingCard(ctk.CTkFrame):
    def __init__(self, master, config, **kwargs):
        super().__init__(
            master,
            corner_radius=config.card_border_radius,
            fg_color=("#F1F5F9", "#1E1E2E"),
            width=config.card_width,
            height=config.card_height,
            **kwargs,
        )
        try:
            lbl = ctk.CTkLabel(
                self,
                text="Cargando...",
                font=ctk.CTkFont(size=12),
                text_color=("#94A3B8", "#64748B"),
            )
            lbl.place(relx=0.5, rely=0.5, anchor="center")
        except Exception:
            pass


class EmptyStateCard(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=16, fg_color=("#F8FAFC", "#1E1E2E"), **kwargs)
        try:
            icon = ctk.CTkLabel(
                self,
                text="\U0001F310",
                font=ctk.CTkFont(size=48),
            )
            icon.pack(pady=(40, 10))
            msg = ctk.CTkLabel(
                self,
                text="No se encontraron sitios recientes",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=("#64748B", "#94A3B8"),
            )
            msg.pack(pady=(0, 5))
            sub = ctk.CTkLabel(
                self,
                text="Navega un poco y vuelve a intentar",
                font=ctk.CTkFont(size=12),
                text_color=("#94A3B8", "#64748B"),
            )
            sub.pack(pady=(0, 40))
        except Exception:
            pass


class ErrorStateCard(ctk.CTkFrame):
    def __init__(self, master, retry_callback=None, **kwargs):
        super().__init__(master, corner_radius=16, fg_color=("#FEF2F2", "#2D1B1B"), **kwargs)
        try:
            icon = ctk.CTkLabel(self, text="\u26A0\uFE0F", font=ctk.CTkFont(size=48))
            icon.pack(pady=(40, 10))
            msg = ctk.CTkLabel(
                self,
                text="Error al cargar el historial",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=("#DC2626", "#F87171"),
            )
            msg.pack(pady=(0, 5))
            if retry_callback:
                btn = ctk.CTkButton(
                    self,
                    text="Reintentar",
                    command=retry_callback,
                    fg_color="#3B82F6",
                    hover_color="#2563EB",
                    corner_radius=8,
                    width=120,
                    height=36,
                )
                btn.pack(pady=(10, 40))
        except Exception:
            pass