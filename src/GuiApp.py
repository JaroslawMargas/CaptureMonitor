import sys
from PySide2.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QGroupBox, QWidget, QGridLayout, QListWidget)
from PySide2.QtCore import Qt
import Handler
import threading
import time
from queue import Empty


class MyWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.hook = Handler.Handler()
        self.t_hook = None
        self.t_start = None
        self.tcp_button_pressed = False
        self.rs232_button_pressed = False
        self.capture_button_pressed = False

        # Widgets
        self.start_handler = QPushButton("Start Hook")
        self.stop_handler = QPushButton("Stop Hook")

        self.event_list = QListWidget()

        self.start_stop_record = QPushButton("Start Recording")
        self.start_stop_play = QPushButton("Start Playback")
        self.start_stop_tcp = QPushButton("TCP Start/Stop")
        self.start_stop_rs232 = QPushButton("RS232 Start/Stop")
        self.start_stop_capture = QPushButton("Capture Start/Stop")
        self.clear_sequence = QPushButton("Clear Sequence")
        self.tcp_label = QLabel("TCP Status: OFF")
        self.rs232_label = QLabel("RS232 Status: OFF")
        self.capture_label = QLabel("Capture after click: OFF")

        # Widget constructor
        self.stop_handler.setEnabled(False)
        self.start_stop_record.setEnabled(False)
        self.start_stop_play.setEnabled(False)
        self.start_stop_tcp.setEnabled(True)
        self.start_stop_rs232.setEnabled(True)
        self.start_stop_capture.setEnabled(True)
        self.clear_sequence.setEnabled(True)

        # Layouts
        self.main_layout = QVBoxLayout()

        self.grid_layout = QGridLayout()

        self.verticalGroupBox_operation = QGroupBox()
        self.verticalGroupBox_status = QGroupBox()
        self.verticalGroupBox_events = QGroupBox()

        self.grid_layout.addWidget(self.verticalGroupBox_operation, 0, 0)
        self.grid_layout.addWidget(self.verticalGroupBox_status, 0, 1)
        self.grid_layout.addWidget(self.verticalGroupBox_events, 1, 0, 1, 2)

        # verticalGroupBox_operation
        self.layout_operation = QVBoxLayout()

        self.layout_operation.setAlignment(Qt.AlignTop)

        self.layout_operation.addWidget(self.start_handler)
        self.layout_operation.addWidget(self.stop_handler)
        self.layout_operation.addWidget(self.start_stop_record)
        self.layout_operation.addWidget(self.start_stop_play)
        self.layout_operation.addWidget(self.clear_sequence)
        self.verticalGroupBox_operation.setLayout(self.layout_operation)

        # verticalGroupBox_status
        self.layout_status = QVBoxLayout()

        self.layout_status.setAlignment(Qt.AlignTop)

        self.layout_status.addWidget(self.start_stop_tcp)
        self.layout_status.addWidget(self.start_stop_rs232)
        self.layout_status.addWidget(self.start_stop_capture)
        self.layout_status.addWidget(self.tcp_label)
        self.layout_status.addWidget(self.rs232_label)
        self.layout_status.addWidget(self.capture_label)
        self.verticalGroupBox_status.setLayout(self.layout_status)

        # verticalGroupBox_events
        self.layout_events = QVBoxLayout()

        self.layout_events.addWidget(self.event_list)

        self.verticalGroupBox_events.setLayout(self.layout_events)

        # set main layout
        self.setLayout(self.grid_layout)

        # Connecting the signal
        self.start_handler.clicked.connect(self.start_hook)
        self.stop_handler.clicked.connect(self.stop_hook)
        self.start_stop_record.clicked.connect(self.start_record)
        self.start_stop_play.clicked.connect(self.start_play)
        self.start_stop_tcp.clicked.connect(self.start_tcp)
        self.start_stop_rs232.clicked.connect(self.start_rs232)
        self.start_stop_capture.clicked.connect(self.start_capture)
        self.clear_sequence.clicked.connect(self.clear)

        self.t_tcp = threading.Thread(name='button stat', target=self.tcp_label_status)
        self.t_tcp.start()

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
        # self.check_tcp.setEnabled(Trself.event_listue)
        self.start_stop_rs232.setEnabled(True)

    def start_record(self):
        self.hook.record(True)
        if self.hook.event_manager.get_recording_status():
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
        if self.hook.event_manager.get_playback_status():
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
                self.start_stop_play.setText("Start Playback")
                self.stop_handler.setEnabled(True)
                self.start_stop_play.setEnabled(True)
                self.start_stop_record.setEnabled(True)
                break

    def start_tcp(self):
        self.tcp_button_pressed = True

    def start_rs232(self):
        self.rs232_button_pressed = True

    def start_capture(self):
        self.capture_button_pressed = True

    def tcp_label_status(self):
        time_out_empty = 2
        while True:
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

            if self.capture_button_pressed:
                if not self.hook.event_manager.get_capture_status():
                    self.hook.event_manager.set_start_capture()
                else:
                    self.hook.event_manager.set_stop_capture()

            if not self.hook.event_manager.get_capture_status():
                self.capture_label.setText("Capture after click: OFF")
                self.capture_button_pressed = False
            else:
                self.capture_label.setText("Capture after click: ON")
                self.capture_button_pressed = False
            if not self.hook.event_manager.get_recording_status():
                try:
                    value = self.hook.event_manager.widget_queue.get(timeout=time_out_empty)
                    str_val = "pos X: " + str(value[0]) + " pos Y: " + str(value[1]) + " Event type: " + str(
                        value[2]) + " key1: " + str(value[3]) + " key2: " + str(value[4])
                    self.event_list.addItem(str_val)
                    self.event_list.setEnabled(False)
                except Empty:
                    self.event_list.scrollToBottom()
                    self.event_list.setEnabled(True)
                    # self.widget_queue.task_done()

    def clear(self):
        self.hook.clear(True)
        self.event_list.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())
