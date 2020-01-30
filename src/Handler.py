from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
from pynput import keyboard

import logging
import threading
import MonitorParams
import EventManager
import Virtual_Kode

module_logger = logging.getLogger('application.Handler')

COMBINATION = [[keyboard.Key.alt_l, keyboard.KeyCode(char='v')],
               [keyboard.Key.alt_l, keyboard.KeyCode(char='b')],
               [keyboard.Key.alt_l, keyboard.KeyCode(char='n')]]

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

    # keyboard
    def on_press(self, key):
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
                str_key += hex(x) + " "
            self.logger.info("Pressed:" + str_key)
            if any([key in COMBO for COMBO in COMBINATION]):
                current.append(key)
                if any(all(k in current for k in COMBO) for COMBO in COMBINATION):
                    str_key_combination = ''
                    for x in current:
                        for k in Virtual_Kode.VK_CODE[str(x).replace("'", "")]:
                            if k !=0:
                                str_key_combination += hex(k) + " "
                    self.logger.info("Pressed:" + str_key_combination)
        except KeyError:
            self.logger.info("Combination not allowed")

    def on_release(self, key):
        try:
            key_string = str(key)
            key_string = key_string.replace("'", "")
            # self.logger.info(Virtual_Kode.VK_CODE[key_string])
            str_key = ""
            for x in Virtual_Kode.VK_CODE[key_string]:
                str_key += hex(x) + " "
            self.logger.info("Released:" + str_key)
            current.clear()
        except KeyError:
            self.logger.debug("Key not allowed")

    def on_move(self, x, y):
        self.logger.info('Mouse moved at ({0}, {1})'.format(x, y, ))
        if self.event_manager.get_recording_status() or self.event_manager.get_send_tcp_status():
            self.event_manager.fill_buffers(Event_type['mouse move'], 0, 0)

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.logger.info('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))
            if self.event_manager.get_recording_status() or self.event_manager.get_send_tcp_status():
                if button == "Button.left":
                    self.event_manager.fill_buffers(Event_type["mouse left down"], 0, 1)
                if button == "Button.right":
                    self.event_manager.fill_buffers(Event_type["mouse right down"], 0, 1)

            if self.event_manager.get_capture_status() and button == "Button.left":
                t = threading.Thread(target=self.event_manager.do_capture_screen)
                t.start()

        else:
            self.logger.info('Mouse released at ({0}, {1}) with {2}'.format(x, y, button))

    def on_scroll(self, x, y, dx, dy):
        print('Mouse scrolled at ({0}, {1})({2}, {3})'.format(x, y, dx, dy))

    def make_hand(self):
        with MouseListener(on_click=self.on_click, on_scroll=self.on_scroll) as self.listener:
            with KeyboardListener(on_press=self.on_press, on_release=self.on_release) as self.listener:
                self.listener.join()

    def stop_handling(self):
        self.listener.stop()
