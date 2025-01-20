import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from matcher import Matcher
import traceback

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)

        # Initialize the Matcher instance for video/audio matching
        self.matcher = Matcher()

        # Create the menu bar and add an "Open" action
        self.file_menu = self.menuBar().addMenu("&File")
        icon = QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen)
        open_action = QAction(icon, "&Open...", self, shortcut=QKeySequence.Open, triggered=self.open)
        self.file_menu.addAction(open_action)

        # Initialize audio output and video widget
        self.audio_output = QAudioOutput()
        self.video = QVideoWidget()
    
        # Create a media player and link it to the video and audio outputs
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.video)
        self.player.setAudioOutput(self.audio_output)
        self.player.positionChanged.connect(self.update_slider_position)
        self.player.durationChanged.connect(self.update_slider_duration)

        # Set up the main layout
        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)
        self.layout = QtWidgets.QVBoxLayout(widget)
        self.layout.addWidget(self.video)

        # Create controls for playback (play button, slider, time label)
        self.controls = QtWidgets.QWidget()
        self.controls.setMaximumHeight(30)
        self.controls_layout = QtWidgets.QHBoxLayout(self.controls)
        self.controls_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.controls)

        # Play button
        self.play_button = QtWidgets.QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackStart), "")
        self.play_button.setFlat(True)
        self.play_button.setFixedSize(30, 30)
        self.play_button.clicked.connect(self.play)
        self.controls_layout.addWidget(self.play_button)

        # Slider for media position
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.valueChanged.connect(self.slider_moved)
        self.controls_layout.addWidget(self.slider)

        # Label to display the current time and duration
        self.time_label = QtWidgets.QLabel("0:00 / 0:00")
        self.time_label.setContentsMargins(0, 0, 10, 0)
        self.controls_layout.addWidget(self.time_label)

        # Volume slider
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)  # Default volume level at 50%
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(self.change_volume)
        self.controls_layout.addWidget(self.volume_slider)

        # Button for finding matching clips
        self.find_button = QtWidgets.QPushButton("No clip selected")
        self.find_button.setEnabled(False)
        self.find_button.clicked.connect(self.find)
        self.layout.addWidget(self.find_button)

    @QtCore.Slot()
    def open(self):
        # Worker thread for loading the original media file
        class Worker(QThread):
            finished = Signal()
            error = Signal(str)

            def __init__(self, matcher, url):
                super().__init__()
                self.matcher = matcher
                self.url = url

            def run(self):
                try:
                    self.matcher.set_original(self.url)
                    self.finished.emit()
                except BaseException as e:
                    self.error.emit(str(e))
                    traceback.print_exc() 

        # Open file dialog to select any type of file
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setMimeTypeFilters(["*/*"])  # Allow all file types
        if file_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            url = file_dialog.selectedUrls()[0]
            self.selected_file = url
            self.player.setSource(url)
            self.find_button.setText("Loading...")
            self.find_button.setEnabled(False)
            self.worker = Worker(self.matcher, url.toLocalFile())
            self.worker.error.connect(lambda message: QtWidgets.QMessageBox.critical(self, "Error", message))
            self.worker.finished.connect(self.set_original_finished)
            self.worker.start()

    @QtCore.Slot()
    def set_original_finished(self):
        # Enable the "Find" button once the original media file is loaded
        self.find_button.setEnabled(True)
        self.find_button.setText("Find")

    @QtCore.Slot()
    def slider_moved(self, value):
        # Update the media player's position when the slider is moved
        if self.player.duration() > 0:
            self.player.setPosition(value * self.player.duration() // 1000)

    @QtCore.Slot()
    def update_slider_position(self, position):
        # Update the slider's position and the time label as the media plays
        if self.player.duration() > 0:
            self.slider.blockSignals(True)  # Prevent recursive signals
            self.slider.setValue(position * 1000 // self.player.duration())
            self.time_label.setText("{0}:{1:02} / {2}:{3:02}".format(
                position // 60000, (position // 1000) % 60,
                self.player.duration() // 60000, (self.player.duration() // 1000) % 60)
            )
            self.slider.blockSignals(False)

    @QtCore.Slot()
    def update_slider_duration(self, duration):
        # Update the duration in the time label when the media loads
        self.time_label.setText("0:00 / {0}:{1:02}".format(
            duration // 60000, (duration // 1000) % 60)
        )

    @QtCore.Slot()
    def play(self):
        # Toggle play and pause when the play button is clicked
        if self.player.isPlaying():
            self.player.pause()
            self.play_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackStart))
        else:
            self.player.play()
            self.play_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackPause))

    @QtCore.Slot()
    def change_volume(self, value):
        # Adjust the volume level based on the slider's position
        self.audio_output.setVolume(value / 100)

    @QtCore.Slot()
    def find(self):
        # Worker thread for finding the matching clip
        class Worker(QThread):
            finished = Signal(int)
            error = Signal(str)

            def __init__(self, matcher, url):
                super().__init__()
                self.matcher = matcher
                self.url = url

            def run(self):
                try:
                    self.matcher.set_clip(self.url)
                    index, accuracy = self.matcher.correlate()
                    time = index * 1000 // self.matcher.frequency
                    self.finished.emit(time)
                    print("Clip starts at {0} seconds with {1} accuracy".format(time / 1000, accuracy))
                except BaseException as e:
                    self.error.emit(str(e))
                    traceback.print_exc() 

        # Open file dialog to select any type of file
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setMimeTypeFilters(["*/*"])  # Allow all file types
        if file_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            url = file_dialog.selectedUrls()[0]
            self.selected_file = url
            self.find_button.setEnabled(False)
            self.find_button.setText("Finding...")
            self.worker = Worker(self.matcher, url.toLocalFile())
            self.worker.error.connect(lambda message: QtWidgets.QMessageBox.critical(self, "Error", message))
            self.worker.finished.connect(self.set_find_finished)
            self.worker.start()

    @QtCore.Slot()
    def set_find_finished(self, time):
        # Set the media player's position to the found time and pause playback
        self.player.setPosition(time)
        self.player.pause()
        self.play_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackStart))
        self.find_button.setEnabled(True)
        self.find_button.setText("Find")

def main():
    # Entry point for the application
    app = QtWidgets.QApplication([])
    widget = Window()
    widget.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
