import sys
import random
from PySide2.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QWidget, QDialogButtonBox)
from PySide2.QtCore import Slot, Qt, Signal, QObject
import Handler
import threading
import time


class MyWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.hook = Handler.Handler()
        self.t_hook = None
        self.t_start = None

        self.start_handler = QPushButton("Start Hook")
        self.stop_handler = QPushButton("Stop Hook")

        self.record = QPushButton("Start Recording")

        # this button will have a one state but add Widget for monitoring of playback.

        self.play = QPushButton("Start/Stop Playback")
        self.text = QLabel("Hello World")
        self.text.setAlignment(Qt.AlignCenter)

        self.stop_handler.setEnabled(False)
        self.record.setEnabled(False)
        self.play.setEnabled(False)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.start_handler)
        self.layout.addWidget(self.stop_handler)
        self.layout.addWidget(self.record)
        self.layout.addWidget(self.play)
        self.setLayout(self.layout)

        # Connecting the signal
        self.start_handler.clicked.connect(self.start_hook)
        self.stop_handler.clicked.connect(self.stop_hook)
        self.record.clicked.connect(self.start_record)
        self.play.clicked.connect(self.start_play)

    def closeEvent(self, event):
        print("close pressed")

    def start_hook(self):
        self.t_hook = threading.Thread(name='start hand', target=self.hook.make_hand)
        self.t_hook.start()
        self.stop_handler.setEnabled(True)
        self.start_handler.setEnabled(False)
        self.record.setEnabled(True)
        self.play.setEnabled(True)

    def stop_hook(self):
        self.hook.stop_handling()
        self.t_hook.join()
        self.stop_handler.setEnabled(False)
        self.start_handler.setEnabled(True)
        self.record.setEnabled(False)

    def start_record(self):
        self.hook.record(True)
        is_record = self.hook.event_manager.get_recording_status()
        if is_record:
            self.record.setText("Stop Recording")
            self.play.setEnabled(False)
            self.stop_handler.setEnabled(False)
        else:
            self.record.setText("Start Recording")
            self.play.setEnabled(True)
            self.stop_handler.setEnabled(True)

    def start_play(self):
        self.hook.play(True)
        self.play.setEnabled(False)
        self.record.setEnabled(False)
        self.t_start = threading.Thread(name='button stat', target=self.set_play_status)
        self.t_start.start()

    def set_play_status(self):
        while True:
            time.sleep(0.100)
            if not self.hook.event_manager.get_playback_status():
                self.play.setEnabled(True)
                self.record.setEnabled(True)
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())
