import sys
from PySide6.QtWidgets import QApplication
from app_core import AppController


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    AppController(app)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()