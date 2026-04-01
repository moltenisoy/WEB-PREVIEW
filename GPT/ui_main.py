import webbrowser
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QPushButton


class SiteCard(QFrame):
    openRequested = Signal(str)

    def __init__(self, site, mode="thumbnails", density="comfortable"):
        super().__init__()
        self.site = site
        self.setObjectName("card")
        root = QHBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        if mode == "thumbnails":
            thumb = QLabel("🌐")
            thumb.setFixedSize(QSize(36, 36))
            thumb.setAlignment(Qt.AlignCenter)
            root.addWidget(thumb)

        text_box = QVBoxLayout()
        title = QLabel(site.title)
        domain = QLabel(site.domain)
        meta = QLabel(site.visited_at)
        title.setObjectName("title")
        domain.setObjectName("domain")
        meta.setObjectName("meta")
        text_box.addWidget(title)
        if mode != "compact":
            text_box.addWidget(domain)
            text_box.addWidget(meta)
        root.addLayout(text_box)

    def mouseDoubleClickEvent(self, event):
        self.openRequested.emit(self.site.url)
        super().mouseDoubleClickEvent(event)


class MainWindow(QWidget):
    openSettingsRequested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recent Sites Dashboard")
        self.resize(900, 620)

        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.title = QLabel("Últimos sitios visitados")
        self.btn_settings = QPushButton("Configuración")
        self.btn_settings.clicked.connect(self.openSettingsRequested.emit)
        top.addWidget(self.title)
        top.addStretch()
        top.addWidget(self.btn_settings)
        layout.addLayout(top)

        self.status = QLabel("")
        layout.addWidget(self.status)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.cards_layout = QVBoxLayout(self.container)
        self.cards_layout.setSpacing(8)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        self.setStyleSheet("""
            QWidget { background: #121212; color: #e8e8e8; font-family: Segoe UI; }
            #card { background: #1d1d1d; border: 1px solid #2b2b2b; border-radius: 10px; }
            #title { font-size: 14px; font-weight: 600; }
            #domain { color: #9ecbff; }
            #meta { color: #9a9a9a; font-size: 11px; }
            QPushButton { background: #2c2c2c; border: 1px solid #3a3a3a; padding: 6px 12px; border-radius: 8px; }
        """)

    def set_loading(self):
        self.clear_cards()
        self.status.setText("Cargando...")

    def set_error(self):
        self.clear_cards()
        self.status.setText("No se pudieron cargar datos")

    def set_empty(self):
        self.clear_cards()
        self.status.setText("No hay historial disponible")

    def show_sites(self, items, mode="thumbnails", density="comfortable"):
        self.clear_cards()
        self.status.setText("")
        for s in items:
            card = SiteCard(s, mode=mode, density=density)
            card.openRequested.connect(webbrowser.open)
            self.cards_layout.addWidget(card)
        self.cards_layout.addStretch()

    def clear_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()