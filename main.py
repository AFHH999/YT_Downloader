from PySide6.QtWidgets import QApplication
from Downloader import MainWindow

# First select the file_path and then paste the link
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()