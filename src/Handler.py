from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
from pynput import keyboard

import logging
import threading
import MonitorParams
import EventManager
import Virtual_Kode

module_logger = logging.getLogger('application.Handler')

# Define special keys as Combination
COMBINATION = [[keyboard.Key.alt_l, keyboard.KeyCode(char='v')],  # make record
               [keyboard.Key.alt_l, keyboard.KeyCode(char='b')],  # make playback
               [keyboard.Key.alt_l, keyboard.KeyCode(char='n')],  # make clear list
               [keyboard.Key.alt_l, keyboard.KeyCode(char='t')],  # start/stop sending by tcp_ip
               [keyboard.Key.alt_l, keyboard.KeyCode(char='r')],  # start/stop sending by rs232
               [keyboard.Key.alt_l, keyboard.KeyCode(char='p')],  # start/stop making capture from monitor
               [keyboard.Key.alt_l, keyboard.KeyCode(char='s')],  # save sequence to xml
               [keyboard.Key.alt_l, keyboard.KeyCode(char='l')]]  # load sequence to xml

current = list()

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


class Handler(object):

    def __init__(self):
        self.logger = logging.getLogger('application.Handler')
        self.logger.debug('creating an instance of Handler')
        self.event_manager = EventManager.EventManager()
        self.monitor = MonitorParams.MonitorParams()
        self.logger.debug('Number of display devices: %s ', str(self.monitor.enum_display_devices()))
        self.logger.debug('Number of physical monitors: %s ', str(self.monitor.get_visible_monitors()))

        self.stop_play_thread = False
        self.t_play = None

    def record(self, button_pressed):
        if self.event_manager.get_recording_status():
            if button_pressed:
                # key sys down when ALT+V pressed. Key down if single key
                # add the last up ALT , before stop recording
                self.event_manager.fill_buffers(Event_type["key sys up"], 0, 164)
                self.event_manager.set_stop_recording()
                self.logger.info('STOP Recording ')
        else:
            if not self.event_manager.get_playback_status():
                if button_pressed:
                    # key sys down when ALT+V pressed. Key down if single key
                    self.event_manager.set_start_recording()
                    self.logger.info('START Recording ')
            else:
                if button_pressed:
                    self.logger.info('If you want record event, please first stop playback ')

    def play(self, button_pressed):
        if self.event_manager.get_playback_status():
            if button_pressed:
                # key sys down when ALT+V pressed. Key down if single key
                self.event_manager.set_stop_playback()
                self.stop_play_thread = False
                self.logger.info('Playback : STOP playback ')
                self.t_play.join()
        else:
            if not self.event_manager.get_recording_status():
                if button_pressed:
                    # key sys down when ALT+V pressed. Key down if single key
                    self.event_manager.set_start_playback()
                    self.stop_play_thread = True
                    self.logger.info('Playback : PLAY playback ')
                    self.t_play = threading.Thread(name='Play list', target=self.event_manager.play_playback_list,
                                                   args=(self.stop_play_thread,))
                    self.t_play.start()
            else:
                self.logger.info('If you want play event, please first stop recording ')

    def save(self, button_pressed):
        if not self.event_manager.get_recording_status() and not self.event_manager.get_playback_status():
            if button_pressed:
                self.event_manager.save_playback_list()
                self.logger.info('Saving List')
        else:
            self.logger.info('If you want save list, please first stop playback and capture ')

    def load(self, button_down):
        if not self.event_manager.get_recording_status() and not self.event_manager.get_playback_status():
            if button_down:
                self.event_manager.load_xml_to_playback_list()
                self.logger.info('Merge xml files into the command list')

    def clear(self, button_down):
        if not self.event_manager.get_recording_status() and not self.event_manager.get_playback_status():
            if button_down:
                self.event_manager.clear_playback_list()
                self.event_manager.clear_tcp_queue()
                self.event_manager.clear_rs232_queue()
                self.logger.info('Event List : clear ')
        else:
            self.logger.info('If you want clear list, please first stop playback and capture ')

    def send_tcp(self, button_down):
        if button_down:
            if not self.event_manager.get_send_tcp_status():
                self.event_manager.set_start_send_tcp()
            else:
                self.event_manager.set_stop_send_tcp()

    def send_rs232(self, button_down):
        if self.event_manager.get_send_rs232_status():
            if button_down:
                self.event_manager.set_stop_send_rs232()
        else:
            if button_down:
                self.event_manager.set_start_send_rs232()

    def make_capture(self, button_down):
        if self.event_manager.get_capture_status():
            if button_down:
                self.event_manager.set_stop_capture()
                self.logger.info('STOP SCREEN SHOOT ')
        else:
            if button_down:
                self.event_manager.set_start_capture()
                self.logger.info('START SCREEN SHOOT')

    # keyboard
    def key_press(self, key):
        try:
            # "a" return 'a' as KeyKode
            # Convert to string and remove '
            # Get hex value from map KeyKode_to_hex value
            # CTRL+C return '\x03' and map KeyCode return tuple as (hex ctrl, hex key)
            key_string = str(key)
            key_string = key_string.replace("'", "")
            # self.logger.info(Virtual_Kode.VK_CODE[key_string])
            str_key = ""
            for x in Virtual_Kode.VK_CODE[key_string]:
                if x != 0:
                    str_key += hex(x)

            self.logger.info("Pressed:" + str_key)
            key1, key2 = Virtual_Kode.VK_CODE[key_string]

            if self.event_manager.get_recording_status() or self.event_manager.get_send_rs232_status():
                self.logger.info("Fill buffer while recording:" + str(key))
                self.event_manager.fill_buffers(Event_type["key down"], key1, key2)

            # make Capture from each key pressed
            if self.event_manager.get_capture_status():
                t = threading.Thread(target=self.event_manager.do_capture_screen)
                t.start()

            if any([key in COMBO for COMBO in COMBINATION]):
                current.append(key)
                str_key_combination = ''
                if any(all(k in current for k in COMBO) for COMBO in COMBINATION):
                    for x in current:
                        for k in Virtual_Kode.VK_CODE[str(x).replace("'", "")]:
                            if k != 0:
                                str_key_combination += hex(k)
                            self.logger.info("Pressed combination:" + str_key_combination)
                            if str_key_combination == "0x5d0x56":
                                self.record(True)
                            if str_key_combination == "0x5d0x54":
                                self.send_tcp(True)
                            if str_key_combination == "0x5d0x52":
                                self.send_rs232(True)
                            if str_key_combination == "0x5d0x42":
                                self.play(True)
                            if str_key_combination == "0x5d0x50":
                                self.make_capture(True)
                            if str_key_combination == "0x5d0x4c":
                                self.load(True)
                            if str_key_combination == "0x5d0x53":
                                self.save(True)
                            if str_key_combination == "0x5d0x4e":
                                self.clear(True)

        except KeyError:
            self.logger.info("Combination is not allowed")

    def key_release(self, key):
        try:
            key_string = str(key)
            key_string = key_string.replace("'", "")
            # self.logger.info(Virtual_Kode.VK_CODE[key_string])
            str_key = ""
            for x in Virtual_Kode.VK_CODE[key_string]:
                if x != 0:
                    str_key += hex(x)
            self.logger.info("Released:" + str_key)

            key1, key2 = Virtual_Kode.VK_CODE[key_string]
            if self.event_manager.get_recording_status():
                self.logger.info("Fill buffer while recording:" + str(key))
                self.event_manager.fill_buffers(Event_type["key up"], key1, key2)
            current.clear()

        except KeyError:
            self.logger.debug("Key not allowed")

    def mouse_move(self, x, y):
        self.logger.info('Mouse moved at ({0}, {1})'.format(x, y, ))
        if self.event_manager.get_recording_status() or self.event_manager.get_send_tcp_status():
            self.event_manager.fill_buffers(Event_type['mouse move'], 0, 0)

    def mouse_click(self, x, y, button, pressed):
        if pressed:
            self.logger.info('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))
            if self.event_manager.get_recording_status() or self.event_manager.get_send_tcp_status():
                if str(button) == "Button.left":
                    self.event_manager.fill_buffers(Event_type["mouse left down"], 0, 1)
                if str(button) == "Button.right":
                    self.event_manager.fill_buffers(Event_type["mouse right down"], 0, 1)

            if self.event_manager.get_capture_status():
                t = threading.Thread(target=self.event_manager.do_capture_screen)
                t.start()

        else:
            self.logger.info('Mouse released at ({0}, {1}) with {2}'.format(x, y, button))
            if self.event_manager.get_recording_status() or self.event_manager.get_send_tcp_status():
                if str(button) == "Button.left":
                    self.event_manager.fill_buffers(Event_type["mouse left up"], 0, 1)
                if str(button) == "Button.right":
                    self.event_manager.fill_buffers(Event_type["mouse right up"], 0, 1)

    def mouse_scroll(self, x, y, dx, dy):
        self.logger.info('Mouse scrolled at ({0}, {1}) ({2}, {3})'.format(x, y, dx, dy))
        if self.event_manager.get_recording_status() or self.event_manager.get_send_tcp_status():
            self.event_manager.fill_buffers(Event_type["mouse wheel"], 0, dy)

    def hook_mouse_and_key(self):
        with MouseListener(on_click=self.mouse_click,
                           on_scroll=self.mouse_scroll,
                           on_move=self.mouse_move
        ) as self.listener:
            with KeyboardListener(on_press=self.key_press, on_release=self.key_release) as self.listener:
                self.listener.join()

    def stop_handling(self):
        self.listener.stop()
