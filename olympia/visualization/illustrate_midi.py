import sys
import numpy as np
import time
from PySide2 import QtCore, QtWidgets, QtGui

from olympia.data import song
from olympia import ROOT_DIR

SAMPLE_MAX = 32767
SAMPLE_MIN = -(SAMPLE_MAX + 1)
SAMPLE_RATE = 44100  # [Hz]
NYQUIST = SAMPLE_RATE / 2
SAMPLE_SIZE = 16  # [bit]
CHANNEL_COUNT = 1
BUFFER_SIZE = 5000


def get_song_data(raw_path):
    song_item = song.Song(raw_path)
    clusters = song_item.get_cluster_sequence()
    stream = song_item.get_stream()

    return stream, clusters


class Visualizer(QtWidgets.QLabel):
    def __init__(self, midi_file, update_interval=33):
        super(Visualizer, self).__init__()

        # self.get_data = get_data
        self.update_interval = update_interval  # 33ms ~= 30 fps
        self.sizeHint = lambda: QtCore.QSize(800, 600)
        self.setStyleSheet("background-color: black;")
        self.setWindowTitle("Olympia")
        self.stream, self.clusters = get_song_data(midi_file)
        self.offset = 0
        self.scene = QtWidgets.QGraphicsScene()
        self.pixmap = QtWidgets.QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap)
        self.ui.graphicsView.setScene(self.scene)
        self.x = 30
        self.y = 40

    def show(self):
        """Show the label and begin updating the visualization."""
        super(Visualizer, self).show()
        self.refresh()

    def refresh(self):
        """Generate a frame, display it, and set queue the next frame"""
        self.setPixmap(QtWidgets.QGraphicsPixmapItem.fromImage(self.generate()))
        # decrease the time till next frame by the processing time so that the framerate stays consistent
        # interval -= 1000 * (time.clock() - t1)
        self.offset += self.update_interval
        # generate random location
        self.x += np.random.uniform(-50, 50)
        self.y += np.random.uniform(-50, 50)

    def generate(self, data):
        raise NotImplementedError()


class SongVisualization(Visualizer):
    def generate(self):
        note = self.stream.flat.getElementsByOffset(self.offset).notes[0]
        pitch = note.pitch.ps

        img = QtGui.QImage(self.width(), self.height(), QtGui.QImage.Format_RGB32)
        img.fill(0)

        painter = QtGui.QPainter(img)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))  # white)
        painter.drawEllipse(self.x, self.y, 200, 200)
        painter.end()
        del painter

        return img


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    midi_path = f"{ROOT_DIR}/olympia/files/songs/subset.mid"
    window = SongVisualization(midi_path)
    window.generate()
    window.show()
    sys.exit(app.exec_())

