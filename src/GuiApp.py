import sys
from PySide2.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QHBoxLayout, QGroupBox, QWidget, QCheckBox)
from PySide2.QtCore import Qt
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

        # Widgets
        self.play = QPushButton("Start/Stop Playback")
        self.text = QLabel("Hello World")
        self.text.setAlignment(Qt.AlignCenter)
        self.check_tcp = QCheckBox("TCP")
        self.check_rs232 = QCheckBox("RS232")
        self.tcp_label = QLabel("TCP Status:")

        # Widget contructor
        self.stop_handler.setEnabled(False)
        self.record.setEnabled(False)
        self.play.setEnabled(False)
        self.check_tcp.setEnabled(True)
        self.check_rs232.setEnabled(True)

        # Layouts
        self.main_layout = QHBoxLayout()

        self.verticalGroupBox = QGroupBox()
        self.verticalGroupBox2 = QGroupBox()

        self.main_layout.addWidget(self.verticalGroupBox)
        self.main_layout.addWidget(self.verticalGroupBox2)

        # GroupBox 1
        self.layout_v = QVBoxLayout()
        self.layout_v.addWidget(self.text)
        self.layout_v.addWidget(self.start_handler)
        self.layout_v.addWidget(self.stop_handler)
        self.layout_v.addWidget(self.record)
        self.layout_v.addWidget(self.play)
        self.verticalGroupBox.setLayout(self.layout_v)

        # GroupBox 2
        self.layout_v2 = QVBoxLayout()
        self.layout_v2.setAlignment(Qt.AlignTop)
        self.layout_v2.addWidget(self.check_tcp)
        self.layout_v2.addWidget(self.check_rs232)
        self.layout_v2.addWidget(self.tcp_label)
        self.verticalGroupBox2.setLayout(self.layout_v2)

        # set main layout
        self.setLayout(self.main_layout)

        # Connecting the signal
        self.start_handler.clicked.connect(self.start_hook)
        self.stop_handler.clicked.connect(self.stop_hook)
        self.record.clicked.connect(self.start_record)
        self.play.clicked.connect(self.start_play)
        self.check_tcp.clicked.connect(self.start_tcp)

    def closeEvent(self, event):
        print("application closed")

    def start_hook(self):
        self.t_hook = threading.Thread(name='start hand', target=self.hook.hook_mouse_and_key)
        self.t_hook.start()
        self.stop_handler.setEnabled(True)
        self.start_handler.setEnabled(False)
        self.record.setEnabled(True)
        self.play.setEnabled(True)
        self.check_tcp.setEnabled(False)
        self.check_rs232.setEnabled(False)

    def stop_hook(self):
        self.hook.stop_handling()
        self.t_hook.join()
        self.stop_handler.setEnabled(False)
        self.start_handler.setEnabled(True)
        self.record.setEnabled(False)
        self.check_tcp.setEnabled(True)
        self.check_rs232.setEnabled(True)

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
        self.t_start = threading.Thread(name='button stat', target=self.check_play_status)
        self.t_start.start()

    def check_play_status(self):
        while True:
            time.sleep(0.100)
            if not self.hook.event_manager.get_playback_status():
                self.play.setEnabled(True)
                self.record.setEnabled(True)
                break

    def start_tcp(self):
        self.hook.send_tcp(True)
        if self.hook.event_manager.get_send_tcp_status():
            self.tcp_label.setText("TCP Status: ON")
            self.check_tcp.setChecked(True)
        else:
            self.tcp_label.setText("TCP Status: OFF")
            self.check_tcp.setChecked(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())
