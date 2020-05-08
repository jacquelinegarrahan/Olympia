import sys
import os
import random
import logging
import time
import json
import argparse
import requests
from qtpy import QtCore, QtWidgets, QtGui

from olympia import db

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


BUTTON_STYLE = (
    "font: 15pt Helvetica; color: black; border: 1px solid; border-color: black; border-radius: 5px; padding: 5px;"
)


class ChecklistDialog(QtWidgets.QWidget):
    def __init__(
        self, name, songs, checked=False, icon=None, parent=None,
    ):
        super(ChecklistDialog, self).__init__(parent)

        self.name = name
        self.icon = icon
        self.model = QtGui.QStandardItemModel()
        self.listView = QtWidgets.QListView()

        self.midi_id_lookup = {}

        # Add songs to the UI
        for song in songs:
            if song.song_title:
                item = QtGui.QStandardItem(f"{song.song_title} by {song.artist}")
                item.setCheckable(True)
                item.setCheckState(QtCore.Qt.Unchecked)
                self.midi_id_lookup[item.text()] = song.midi_id
                self.model.appendRow(item)

        self.listView.setModel(self.model)
        self.listView.setStyleSheet(BUTTON_STYLE)

        self.ok_button = QtWidgets.QPushButton("OK")
        self.ok_button.setStyleSheet(BUTTON_STYLE)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.setStyleSheet(BUTTON_STYLE)

        self.select_button = QtWidgets.QPushButton("Select All")
        self.select_button.setStyleSheet(BUTTON_STYLE)

        self.unselect_button = QtWidgets.QPushButton("Unselect All")
        self.unselect_button.setStyleSheet(BUTTON_STYLE)

        # set up logo and insert
        self.logo_pixmap = QtGui.QPixmap(os.getcwd() + "/olympia/files/olympia.png")
        self.logo_pixmap = self.logo_pixmap.scaledToWidth(150, mode=QtCore.Qt.SmoothTransformation)
        self.logo_image = QtWidgets.QLabel()
        self.logo_image.setPixmap(self.logo_pixmap)
        self.logo_image.setStyleSheet("margin: 25px;")
        self.logo_image.setAlignment(QtCore.Qt.AlignCenter)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.ok_button)
        hbox.addWidget(self.cancel_button)
        hbox.addWidget(self.select_button)
        hbox.addWidget(self.unselect_button)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.logo_image)
        vbox.addWidget(self.listView)
        vbox.addLayout(hbox)

        self.setWindowTitle(self.name)
        if self.icon:
            self.setWindowIcon(self.icon)

        self.ok_button.clicked.connect(self.on_accepted)
        # self.cancel_button.clicked.connect(self.reject)
        self.select_button.clicked.connect(self.select)
        self.unselect_button.clicked.connect(self.unselect)

    def on_accepted(self):
        self.choices = [
            self.model.item(i).text()
            for i in range(self.model.rowCount())
            if self.model.item(i).checkState() == QtCore.Qt.Checked
        ]
        self.accept()

    def select(self):
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            item.setCheckState(QtCore.Qt.Checked)

    def unselect(self):
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)


# CLASS: MainWindow
# DESCRIPTION: Configures parent window for application and controls application flow
class MainWindow(QtWidgets.QWidget):
    def __init__(self, app):
        super(MainWindow, self).__init__()
        self.app = app

        # set background to white
        self.setStyleSheet("background-color:rgb(255,255,255);")
        self.songs = db.execute_query("SELECT midi_id, song_title, artist FROM midis", ())

        self.form = ChecklistDialog("Song Selections", self.songs, checked=True)
        # self.form.setStyleSheet(
        #    "font: 15pt Helvetica; color: rgb(0,0,0); border-color: black; border-radius: 2px;  border-radius: 10px;"
        # )
        # self.welcome_text = QtWidgets.QLabel("OLYMPIA")
        # self.welcome_text.setAlignment(QtCore.Qt.AlignCenter)
        # self.welcome_text.setStyleSheet("font: 30pt Helvetica; color: rgb(51,51,204);")

        # submit username on enter key press
        # self.username_input.returnPressed.connect(self.button.click)

        # build and setlayout
        hbox = QtWidgets.QHBoxLayout()
        vbox = QtWidgets.QVBoxLayout()
        # vbox.addWidget(self.logo_image)
        # vbox.addWidget(self.welcome_text)
        vbox.addLayout(hbox)
        vbox.addWidget(self.form)
        vbox.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(vbox)


if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication([])

        # setup timer for refreshing chat feed
        timer = QtCore.QTimer()
        timer.timeout.connect(app.processEvents)
        timer.start(500)

        widget = MainWindow(app)
        widget.resize(800, 700)
        widget.show()

        sys.exit(app.exec_())

    except KeyboardInterrupt:
        logger.info("Closing...")
