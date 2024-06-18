from PySide6.QtWidgets import ( 
    QMainWindow, QWidget, QVBoxLayout, 
    QLineEdit, QPushButton, QLabel, QMenuBar, 
    QFileDialog, QProgressBar, QDialog, QComboBox, QDialogButtonBox)
from PySide6.QtGui import QAction
from PySide6.QtCore import Slot
from pytube import YouTube, Stream

class MainWindow(QMainWindow):  # This function create the main window and what is inside of it
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.setFixedSize(600,570)

        self.total_bytes_downloaded = 0
        self.total_bytes_expected = None

        self.download_path = ""

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.link_input = QLineEdit(self)
        layout.addWidget(self.link_input)
        self.link_input.setPlaceholderText("Insert the link of the video: ")

        self.link_input.textChanged.connect(self.start_download_if_ready)

        button = QPushButton("Download")
        button.clicked.connect(self.download)
        layout.addWidget(button)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel(self)
        layout.addWidget(self.status_label)
        self.init_menu()

    def show_resolution_dialog(self, yt): # This function initialize the menu for choosing the resolution for the download.
        resolutions = yt.streams.filter(progressive=True).order_by('resolution').desc()
        resolution_list = [f"{stream.resolution} ({stream.abr})" for stream in resolutions]
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Resolution")
        layout = QVBoxLayout()
        
        label = QLabel("Select the desired resolution:")
        layout.addWidget(label)
        
        combo_box = QComboBox()
        combo_box.addItems(resolution_list)
        layout.addWidget(combo_box)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        if dialog.exec() == QDialog.Accepted:
            selected_index = combo_box.currentIndex()
            selected_stream = resolutions[selected_index]
            return selected_stream
        else:
            return None

    def start_download_if_ready(self):
        url = self.get_input()
        if not url or not self.download_path:
            return
        
        self.download()

    def init_menu(self): # This function define the menu for choosing the path
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        file_menu = menu_bar.addMenu('File')
        select_path_action = QAction('Select Download Path', self)
        select_path_action.triggered.connect(self.select_download_path)
        file_menu.addAction(select_path_action)

    @Slot()  # This is the signal that indicates when the path for download was chosen
    def select_download_path(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        
        if dialog.exec():
            self.download_path = dialog.selectedFiles()[0]
            self.start_download_if_ready()

    def get_input(self):
        url = self.link_input.text()
        return url
    
    def download(self): 
        url = self.get_input()
        if not url:
            self.status_label.setText("Please enter a URL")
            return
        
        if not self.download_path:
            self.status_label.setText("Please select a download path first")
            return
        
        self.status_label.setText("Downloading")
        self.progress_bar.setValue(0)
        try:
            YT = YouTube(url, on_progress_callback=self.update_progress)
            selected_stream = self.show_resolution_dialog(YT)
            if selected_stream:
                selected_stream.download(output_path=self.download_path)
                self.status_label.setText("Download Completed!")
            else:
                self.status_label.setText("Download canceled")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
        finally:
            self.progress_bar.setValue(100)
            self.download_path = ""
            self.link_input.setText("")

    def update_progress(self, stream, chunk, bytes_remaining): # This function update the progress for the progress bar
        self.total_bytes_downloaded += len(chunk)
        if self.total_bytes_expected:
            progress = (self.total_bytes_downloaded / self.total_bytes_expected) * 100
            self.progress_bar.setValue(int(progress))