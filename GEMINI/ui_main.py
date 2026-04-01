import customtkinter as ctk
import webbrowser
from ui_settings import SettingsWindow

class MainWindow(ctk.CTk):
    def __init__(self, config_manager, history_service):
        super().__init__()
        try:
            self.config_manager = config_manager
            self.history_service = history_service
            self.title("Dashboard")
            self.geometry("900x700")
            self.protocol("WM_DELETE_WINDOW", self.hide_window)
            self.apply_config()
            self.build_ui()
        except:
            pass

    def apply_config(self):
        try:
            self.config = self.config_manager.load()
            ctk.set_appearance_mode(self.config.get("theme", "dark"))
            self.load_history()
        except:
            pass

    def build_ui(self):
        try:
            for widget in self.winfo_children():
                widget.destroy()
                
            self.top_frame = ctk.CTkFrame(self)
            self.top_frame.pack(fill="x", padx=20, pady=20)
            
            lbl_title = ctk.CTkLabel(self.top_frame, text="Recent Browsing History", font=("Segoe UI", 24, "bold"))
            lbl_title.pack(side="left", padx=10)
            
            ctk.CTkButton(self.top_frame, text="Settings", width=100, command=self.open_settings).pack(side="right", padx=10)
            ctk.CTkButton(self.top_frame, text="Refresh", width=100, command=self.load_history).pack(side="right", padx=10)
            
            self.scrollable_frame = ctk.CTkScrollableFrame(self)
            self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            self.load_history()
        except:
            pass

    def load_history(self):
        try:
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
                
            items = self.history_service.get_history(self.config.get("max_items", 20))
            
            for item in items:
                card = ctk.CTkFrame(self.scrollable_frame, corner_radius=10)
                card.pack(fill="x", pady=8, padx=10)
                card.bind("<Double-Button-1>", lambda e, u=item.url: self.open_url(u))
                
                lbl_title = ctk.CTkLabel(card, text=item.title, font=("Segoe UI", 16, "bold"), anchor="w")
                lbl_title.pack(fill="x", padx=15, pady=(10, 2))
                lbl_title.bind("<Double-Button-1>", lambda e, u=item.url: self.open_url(u))
                
                lbl_domain = ctk.CTkLabel(card, text=item.domain, font=("Segoe UI", 12), text_color="gray", anchor="w")
                lbl_domain.pack(fill="x", padx=15, pady=(0, 10))
                lbl_domain.bind("<Double-Button-1>", lambda e, u=item.url: self.open_url(u))
        except:
            pass

    def open_url(self, url):
        try:
            webbrowser.open(url)
        except:
            pass

    def open_settings(self):
        try:
            SettingsWindow(self.config_manager, self.apply_config)
        except:
            pass

    def hide_window(self):
        try:
            self.withdraw()
        except:
            pass