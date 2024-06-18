from PySide6.QtWidgets import QApplication
from Downloader import MainWindow
# This initialize the code
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()