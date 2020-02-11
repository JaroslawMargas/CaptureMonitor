import sys
from PySide2.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QHBoxLayout, QGroupBox, QWidget)
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
        self.tcp_button_pressed = False
        self.rs232_button_pressed = False

        self.t_tcp = threading.Thread(name='button stat', target=self.tcp_label_status)
        self.t_tcp.start()

        # Widgets
        self.start_handler = QPushButton("Start Hook")
        self.stop_handler = QPushButton("Stop Hook")

        self.start_stop_record = QPushButton("Start/Stop Recording")
        self.start_stop_play = QPushButton("Start/Stop Playback")
        self.text = QLabel("Hello World")
        self.text.setAlignment(Qt.AlignCenter)
        self.start_stop_tcp = QPushButton("TCP Start/Stop")
        self.start_stop_rs232 = QPushButton("RS232 Start/Stop")
        self.clear_sequence = QPushButton("Clear Sequence")
        self.tcp_label = QLabel("TCP Status: OFF")
        self.rs232_label = QLabel("RS232 Status: OFF")

        # Widget constructor
        self.stop_handler.setEnabled(False)
        self.start_stop_record.setEnabled(False)
        self.start_stop_play.setEnabled(False)
        self.start_stop_tcp.setEnabled(True)
        self.start_stop_rs232.setEnabled(True)
        self.clear_sequence.setEnabled(True)

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
        self.layout_v.addWidget(self.start_stop_record)
        self.layout_v.addWidget(self.start_stop_play)
        self.layout_v.addWidget(self.clear_sequence)
        self.verticalGroupBox.setLayout(self.layout_v)

        # GroupBox 2
        self.layout_v2 = QVBoxLayout()
        self.layout_v2.setAlignment(Qt.AlignTop)
        self.layout_v2.addWidget(self.start_stop_tcp)
        self.layout_v2.addWidget(self.start_stop_rs232)
        self.layout_v2.addWidget(self.tcp_label)
        self.layout_v2.addWidget(self.rs232_label)
        self.verticalGroupBox2.setLayout(self.layout_v2)

        # set main layout
        self.setLayout(self.main_layout)

        # Connecting the signal
        self.start_handler.clicked.connect(self.start_hook)
        self.stop_handler.clicked.connect(self.stop_hook)
        self.start_stop_record.clicked.connect(self.start_record)
        self.start_stop_play.clicked.connect(self.start_play)
        self.start_stop_tcp.clicked.connect(self.start_tcp)
        self.start_stop_rs232.clicked.connect(self.start_rs232)
        self.clear_sequence.clicked.connect(self.clear)

    def closeEvent(self, event):
        print("application closed")

    def start_hook(self):
        self.t_hook = threading.Thread(name='start hand', target=self.hook.hook_mouse_and_key)
        self.t_hook.start()
        self.stop_handler.setEnabled(True)
        self.start_handler.setEnabled(False)
        self.start_stop_record.setEnabled(True)
        self.start_stop_play.setEnabled(True)
        # self.check_tcp.setEnabled(False)
        # self.check_rs232.setEnabled(False)

    def stop_hook(self):
        self.hook.stop_handling()
        self.t_hook.join()
        self.stop_handler.setEnabled(False)
        self.start_handler.setEnabled(True)
        self.start_stop_record.setEnabled(False)
        self.start_stop_play.setEnabled(False)
        # self.check_tcp.setEnabled(True)
        self.start_stop_rs232.setEnabled(True)

    def start_record(self):
        self.hook.record(True)
        is_record = self.hook.event_manager.get_recording_status()
        if is_record:
            self.start_stop_record.setText("Stop Recording")
            self.start_stop_play.setEnabled(False)
            self.stop_handler.setEnabled(False)
            self.clear_sequence.setEnabled(False)
        else:
            self.start_stop_record.setText("Start Recording")
            self.start_stop_play.setEnabled(True)
            self.stop_handler.setEnabled(True)
            self.clear_sequence.setEnabled(True)

    def start_play(self):
        self.hook.play(True)
        # self.play_sequence.setEnabled(False)
        is_play = self.hook.event_manager.get_playback_status()
        if is_play:
            self.start_stop_play.setText("Stop Playback")
            self.start_stop_record.setEnabled(False)
            self.stop_handler.setEnabled(False)
        else:
            self.start_stop_play.setText("Start Playback")
            self.start_stop_record.setEnabled(True)
            self.stop_handler.setEnabled(True)

        self.t_start = threading.Thread(name='button stat', target=self.check_play_status)
        self.t_start.start()

    def check_play_status(self):
        while True:
            time.sleep(0.100)
            if not self.hook.event_manager.get_playback_status():
                self.stop_handler.setEnabled(True)
                self.start_stop_play.setEnabled(True)
                self.start_stop_record.setEnabled(True)
                break

    def start_tcp(self):
        self.tcp_button_pressed = True

    def start_rs232(self):
        self.rs232_button_pressed = True

    def tcp_label_status(self):
        while True:
            time.sleep(0.100)
            # if self.tcp_button_pressed:
            if self.tcp_button_pressed:
                if not self.hook.event_manager.get_send_tcp_status():
                    self.hook.event_manager.set_start_send_tcp()
                else:
                    self.hook.event_manager.set_stop_send_tcp()

            if not self.hook.event_manager.get_send_tcp_status():
                self.tcp_label.setText("TCP Status: OFF")
                self.tcp_button_pressed = False
            else:
                self.tcp_label.setText("TCP Status: ON")
                self.tcp_button_pressed = False

            if self.rs232_button_pressed:
                if not self.hook.event_manager.get_send_rs232_status():
                    self.hook.event_manager.set_start_send_rs232()
                else:
                    self.hook.event_manager.set_stop_send_rs232()

            if not self.hook.event_manager.get_send_rs232_status():
                self.rs232_label.setText("RS232 Status: OFF")
                self.rs232_button_pressed = False
            else:
                self.rs232_label.setText("RS232 Status: ON")
                self.rs232_button_pressed = False

    def clear(self):
        self.hook.clear(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())
