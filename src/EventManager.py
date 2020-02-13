import EventExecutor
import MonitorParams
import XmlCreator
import TCPServer
import RS232Serial
import CaptureScreen
import time
import logging
import os
import threading
import queue
from queue import Empty
import pickle

Event_type = {
    "mouse move": 1,
    "key down": 2,
    "key up": 3,
    "key sys down": 4,
    "key sys up": 5,
    "mouse left down": 6,
    "mouse left up": 7,
    "mouse right down": 8,
    "mouse right up": 9,
    "mouse wheel": 10,
}


class EventManager(object):
    def __init__(self):
        self.logger = logging.getLogger('application.EventManager')

        self.xml = XmlCreator.XmlCreator()
        self.rsCommand = RS232Serial.RS232Serial()

        self.playback_list = []
        self.start_time = time.time()
        self.monitor = MonitorParams.MonitorParams()
        self.is_play = False
        self.is_recording = False

        self.server = None
        self.tcp_thread = None
        self.rs232_thread = None
        self.send_tcp = None

        self.is_connected = False
        self.send_rs232 = False

        self.do_capture = False

        self.tcp_queue = queue.Queue()
        self.rs232_queue = queue.Queue()
        self.widget_queue = queue.Queue()
        # self.new_widget = False

        self.event_tcp_thread = threading.Event()
        self.event_rs232_thread = threading.Event()

    def set_stop_playback(self):
        self.is_play = False

    def set_start_playback(self):
        self.is_play = True

    def get_playback_status(self):
        return self.is_play

    def set_stop_recording(self):
        self.is_recording = False

    def set_start_recording(self):
        self.is_recording = True
        # set the timer value when recording has started
        # elapsed time between previous (or starting recorting) and next command = current time - start_time
        self.start_time = time.time()

    def get_recording_status(self):
        return self.is_recording

    def set_stop_send_tcp(self):
        self.send_tcp = False
        self.tcp_thread.join()
        self.logger.info('STOP SEND TCP ')

    def set_start_send_tcp(self):
        time_out_event = 2
        time_out_empty = 0.25
        self.send_tcp = True
        self.tcp_thread = threading.Thread(name='TCP send',
                                           target=self.send_tcp_command,
                                           args=(self.event_tcp_thread, time_out_event, self.tcp_queue,
                                                 time_out_empty))
        self.tcp_thread.start()

    def get_send_tcp_status(self):
        return self.send_tcp

    def set_stop_send_rs232(self):
        self.send_rs232 = False
        self.rs232_thread.join()
        self.logger.info('STOP SEND RS232 ')

    def set_start_send_rs232(self):
        time_out_event = 2
        time_out_empty = 0.25
        self.send_rs232 = True
        self.rs232_thread = threading.Thread(name='RS232 send',
                                             target=self.send_rs232_command,
                                             args=(
                                                 self.event_rs232_thread, time_out_event, self.rs232_queue,
                                                 time_out_empty))
        self.rs232_thread.start()

    def get_send_rs232_status(self):
        return self.send_rs232

    def set_stop_capture(self):
        self.do_capture = False

    def set_start_capture(self):
        self.do_capture = True

    def get_capture_status(self):
        return self.do_capture

    def fill_tcp_queue(self, data):
        self.tcp_queue.put(data)
        self.event_tcp_thread.set()
        self.logger.debug('Set event to send tcp: %s', self.event_tcp_thread.is_set())

    def fill_rs232_queue(self, data):
        # add KEY value to queue [key, status:press/released]
        self.rs232_queue.put(data)
        self.event_rs232_thread.set()
        self.logger.info('Set event to send rs232: %s', self.event_rs232_thread.is_set())

    def fill_buffers(self, event_message_type, key1, key2):
        elapsed_time = time.time() - self.start_time

        self.start_time = time.time()
        # self.get_monitor_params()

        (x, y) = self.monitor.get_cursor_position()
        self.logger.debug('Mouse event: %s position %s %s ', event_message_type, x, y)

        arg_list = [x, y, event_message_type, key1, key2, elapsed_time]

        if self.get_recording_status():
            self.playback_list.append(arg_list)
            self.widget_queue.put(arg_list)

        if self.get_send_tcp_status() and self.is_connected:
            self.fill_tcp_queue(arg_list)

        if self.get_send_rs232_status():
            self.logger.info("fill_rs232_queue:" + str(key1) + str(str(key2)))
            self.fill_rs232_queue((hex(key2), event_message_type))

        self.logger.info('Event %s %s %s ', event_message_type, hex(key1), hex(key2))

        return True

    def clear_playback_list(self):
        del self.playback_list[:]

    def clear_tcp_queue(self):
        mutex = threading.Lock()
        mutex.acquire()
        try:
            # self.tcp_queue.queue.clear()
            self.tcp_queue = queue.Queue()
            # self.tcp_queue.task_done()
            # self.tcp_queue.unfinished_tasks = 0
        finally:
            mutex.release()

    def clear_rs232_queue(self):
        mutex = threading.Lock()
        mutex.acquire()
        try:
            # self.tcp_queue.queue.clear()
            self.rs232_queue = queue.Queue()
            # self.rs232_queue.task_done()
            # self.rs232_queue.unfinished_tasks = 0
        finally:
            mutex.release()

    def play_playback_list(self, stop_playback):

        self.is_play = stop_playback
        executor = EventExecutor.EventExecutor()

        while self.is_play:
            for value in self.playback_list:
                # self.logger.info('Play event delay : %s ',value[4])
                self.logger.debug('Wait delay time to execute next command: %s', value[5])
                time.sleep(value[5])  # first wait elapsed time then press

                if value[2] == Event_type['mouse move']:
                    # Pass the coordinates (x,y) as a tuple:
                    executor.do_mouse_move(value[0], value[1])

                if (value[2] == Event_type['key down']) or (value[2] == Event_type['key sys down']):
                    if value[3] == 0:
                        executor.do_key_down(value[4])
                    else:
                        executor.do_extended_key_down(value[3])
                        executor.do_extended_key_down(value[4])
                        # ctr+C is registered as extended if ctr and c pressed or ctr and c released
                        # not registered if c  and ctr (c is first released before ctr)
                        # it's better to do  redundant auto extended Up
                        executor.do_extended_key_up(value[3])
                        executor.do_extended_key_up(value[4])
                if (value[2] == Event_type['key up']) or (value[2] == Event_type['key sys up']):
                    if value[3] == 0:
                        executor.do_key_up(value[4])
                    else:
                        executor.do_extended_key_up(value[3])
                        executor.do_extended_key_up(value[4])
                if value[2] == Event_type['mouse left down']:
                    executor.do_left_mouse_down(value[0], value[1])
                if value[2] == Event_type['mouse left up']:
                    executor.do_left_mouse_up(value[0], value[1])
                if value[2] == Event_type['mouse right down']:
                    executor.do_right_mouse_down(value[0], value[1])
                if value[2] == Event_type['mouse right up']:
                    executor.do_right_mouse_up(value[0], value[1])
                if value[2] == Event_type['mouse wheel']:
                    executor.do_mouse_wheel(value[0], value[1], value[4])
                if not self.is_play:
                    self.logger.info('Playback : STOPPED')
                    break
            self.logger.info('Playback : STOPPED - Event list is finished ')
            self.is_play = False

    def save_playback_list(self):
        self.xml.create_root("root")
        for value in self.playback_list:
            self.xml.create_child("command")
            self.xml.create_element("param", "posX", str(value[0]))
            self.xml.create_element("param", "posY", str(value[1]))
            self.xml.create_element("param", "message", str(value[2]))
            self.xml.create_element("param", "key1", str(value[3]))
            self.xml.create_element("param", "key2", str(value[4]))
            self.xml.create_element("param", "time", str(value[5]))
        self.xml.compose_tree()
        self.xml.save_xml()

    def load_xml_to_playback_list(self):
        path = str(os.getcwd())
        self.playback_list = XmlCreator.merge_files(path, "command", "param")

    def send_tcp_command(self, event_thread, time_out_event, queue_buffer, time_out_empty):
        self.logger.info('START SEND TCP ')
        while True:
            if not self.is_connected:
                self.server = TCPServer.TCPServer()
                self.is_connected = self.server.connect()
                if not self.get_send_tcp_status():
                    break

            event_thread.wait(time_out_event)
            if event_thread.is_set():
                self.logger.debug('New data on the list - ready to be sent by tcp: %s', event_thread.is_set())

                while True:
                    try:
                        value = queue_buffer.get(timeout=time_out_empty)
                        # If timeout, it blocks at most timeout seconds and raises the Empty exception
                        # if no item was available within that time.
                    except Empty:
                        event_thread.clear()
                        queue_buffer.task_done()
                        break
                    else:
                        # if queue is not empty
                        if self.is_connected:
                            data = pickle.dumps(value)
                            self.logger.debug('send_data TCP')
                            self.server.send_data(data)
                            self.logger.debug('Value: %s', value)

                            ack_format = format(value[5], '.5f')
                            is_ack = self.server.wait_for_received(ack_format)
                            if not is_ack:
                                self.logger.error('Timeout ACK')
                            if is_ack:
                                self.logger.debug('Next data')
                        else:
                            break
            else:
                self.logger.debug('Waiting for event to send %s:', event_thread.is_set())

    def send_rs232_command(self, event_thread, time_out_event, queue_buffer, time_out_empty):
        self.logger.info('START SEND RS232 ')
        while True:
            if not self.get_send_rs232_status():
                break
            event_thread.wait(time_out_event)
            if event_thread.is_set():
                self.logger.info('New data on the list - ready to be sent by rs232: %s', event_thread.is_set())

                while True:
                    if not self.get_send_rs232_status():
                        break
                    try:
                        value = queue_buffer.get(timeout=time_out_empty)
                        # If timeout, it blocks at most timeout seconds and raises the Empty exception
                        # if no item was available within that time.

                    except Empty:
                        event_thread.clear()
                        queue_buffer.task_done()
                        break
                    else:
                        if self.send_rs232:
                            if value[1] == 2:
                                self.rsCommand.set_command(value[0], True)
                                self.rsCommand.send_command()
                            # time.sleep(0.001)
                            if value[1] == 3:
                                self.rsCommand.set_command(value[0], False)
                                self.rsCommand.send_command()
                            received = self.rsCommand.read_command()
                            try:
                                str_rec = ''
                                for itm in received:
                                    str_rec += hex(itm)
                                self.logger.info('Received command: %s', str_rec)
                            except Exception as err:
                                self.logger.info('No data receive: ' + str(err))

                        else:
                            break
            else:
                self.logger.debug('Waiting for event to send %s:', event_thread.is_set())


    def do_capture_screen(self):
        capture_screen = CaptureScreen.CaptureScreen()
        capture_screen.set_capture_params()
        (x, y) = self.monitor.get_cursor_position()
        capture_screen.set_cursor_draw(x, y)
        capture_screen.grab_handle()
        capture_screen.create_context()
        capture_screen.create_memory()
        capture_screen.create_bitmap()
        capture_screen.copy_screen_to_memory()
        capture_screen.save_bitmap_to_file()
        capture_screen.free_objects()
        return True
