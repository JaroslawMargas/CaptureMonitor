import logging
import pythoncom
import pyHook
from pyHook import GetKeyState, HookConstants
import threading
import string
import MonitorParams
import EventManager

module_logger = logging.getLogger('application.HookEvent')

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


def on_mouse_event(event):
    print 'MessageName:', event.MessageName
    print 'Message:', event.Message
    print 'Time:', event.Time
    print 'Window:', event.Window
    print 'WindowName:', event.WindowName
    print 'Position:', event.Position
    print 'Wheel:', event.Wheel
    print 'Injected:', event.Injected
    print '---'
    return True

    # hook mouse


class HookEvent(object):

    def __init__(self):
        self.logger = logging.getLogger('application.HookEvent')
        self.logger.debug('creating an instance of HookEvent')
        self.hm = pyHook.HookManager()
        self.event_manager = EventManager.EventManager()
        self.monitor = MonitorParams.MonitorParams()
        self.logger.debug('Number of display devices: %s ', str(self.monitor.enum_display_devices()))
        self.logger.debug('Number of physical monitors: %s ', str(self.monitor.get_visible_monitors()))

    def move(self, event):
        self.logger.debug('Mouse event : %s ', event.MessageName)
        if self.event_manager.get_recording_status() or self.event_manager.get_send_tcp_status():
            self.event_manager.fill_buffers(Event_type[event.MessageName], 0, 0)
        return True

    def left_down(self, event):
        self.logger.debug('Mouse event : %s ', event.MessageName)
        if self.event_manager.get_recording_status() or self.event_manager.get_send_tcp_status():
            self.event_manager.fill_buffers(Event_type[event.MessageName], 0, 1)
        if self.event_manager.get_capture_status() and event.MessageName == "mouse left down":
            t = threading.Thread(target=self.event_manager.do_capture_screen)
            t.start()

        return True

    def right_down(self, event):
        self.logger.debug('Mouse event : %s ', event.MessageName)
        if self.event_manager.get_recording_status() or self.event_manager.get_send_tcp_status():
            self.event_manager.fill_buffers(Event_type[event.MessageName], 0, 2)
        if self.event_manager.get_capture_status():
            t = threading.Thread(target=self.event_manager.do_capture_screen)
            t.start()

        return True

    def middle_down(self, event):
        self.logger.debug('Mouse event : %s ', event.MessageName)
        if self.event_manager.get_recording_status() or self.event_manager.get_send_tcp_status():
            self.event_manager.fill_buffers(Event_type[event.MessageName], 0, 4)
        if self.event_manager.get_capture_status():
            t = threading.Thread(target=self.event_manager.do_capture_screen)
            t.start()

        return True

    def wheel(self, event):
        self.logger.debug('Mouse event : %s ', event.MessageName)
        if self.event_manager.get_recording_status() or self.event_manager.get_send_tcp_status():
            self.event_manager.fill_buffers(Event_type[event.MessageName], 0, event.Wheel)

        return True

    def on_keyboard_event(self, event):
        # "ALT+V record event "    
        if GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x56", 16):
            if self.event_manager.get_recording_status():
                if event.MessageName == 'key sys down':
                    # key sys down when ALT+V pressed. Key down if single key
                    # add the last up ALT , before stop recording
                    self.event_manager.fill_buffers(Event_type["key sys up"], 0, 164)
                    self.event_manager.set_stop_recording()
                    self.logger.info('STOP Recording ')
            else:
                if not self.event_manager.get_playback_status():
                    if event.MessageName == 'key sys down':
                        # key sys down when ALT+V pressed. Key down if single key
                        self.event_manager.set_start_recording()
                        self.logger.info('START Recording ')
                else:
                    if event.MessageName == 'key sys down':
                        self.logger.info('If you want record event, please first stop playback ')

        # "ALT+T send value by TCP "
        if GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x54", 16):
            if self.event_manager.get_send_tcp_status():
                if event.MessageName == 'key sys down':
                    self.event_manager.set_stop_send_tcp()
                    self.logger.info('STOP SEND TCP ')
            else:
                if event.MessageName == 'key sys down':
                    self.event_manager.set_start_send_tcp()
                    self.logger.info('START SEND TCP ')

        # "ALT+R send value by RS232 "
        if GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x52", 16):
            if self.event_manager.get_send_rs232_status():
                if event.MessageName == 'key sys down':
                    self.event_manager.set_stop_send_rs232()
                    self.logger.info('STOP SEND RS232 ')
            else:
                if event.MessageName == 'key sys down':
                    self.event_manager.set_start_send_rs232()
                    self.logger.info('START SEND RS232 ')

        # ALT+P  make screenshoot with mouse or key down
        if GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x50", 16):
            if self.event_manager.get_capture_status():
                if event.MessageName == 'key sys down':
                    self.event_manager.set_stop_capture()
                    self.logger.info('STOP SCREEN SHOOT ')
            else:
                if event.MessageName == 'key sys down':
                    self.event_manager.set_start_capture()
                    self.logger.info('START SCREEN SHOOT')

        # "ALT+B play list"
        elif GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x42", 16):
            if self.event_manager.get_playback_status():
                if event.MessageName == 'key sys down':
                    # key sys down when ALT+V pressed. Key down if single key
                    self.event_manager.set_stop_playback()
                    self.logger.info('Playback : STOP playback ')
            else:
                if not self.event_manager.get_recording_status():
                    if event.MessageName == 'key sys down':
                        # key sys down when ALT+V pressed. Key down if single key
                        self.event_manager.set_start_playback()
                        self.logger.info('Playback : PLAY playback ')
                        t = threading.Thread(name='Play list', target=self.event_manager.play_playback_list())
                        t.start()
                else:
                    self.logger.info('If you want play event, please first stop recording ')

        # ALT+S Save current list.
        elif GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x53", 16):
            if not self.event_manager.get_recording_status() and not self.event_manager.get_playback_status():
                if event.MessageName == 'key sys down':
                    self.event_manager.save_playback_list()
                    self.logger.info('Saving List')
            else:
                self.logger.info('If you want save list, please first stop playback and capture ')

        # ALT+L Load merged xml files
        elif GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x4C", 16):
            if not self.event_manager.get_recording_status() and not self.event_manager.get_playback_status():
                if event.MessageName == 'key sys down':
                    self.event_manager.load_xml_to_playback_list()
                    self.logger.info('Merge xml files into the command list')

        # "ALT+N clear recording list"
        elif GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x4e", 16):
            if not self.event_manager.get_recording_status() and not self.event_manager.get_playback_status():
                if event.MessageName == 'key sys down':
                    self.event_manager.clear_playback_list()
                    self.event_manager.clear_tcp_queue()
                    self.event_manager.clear_rs232_queue()
                    self.logger.info('Event List : clear ')
            else:
                self.logger.info('If you want clear list, please first stop playback and capture ')

        elif GetKeyState(HookConstants.VKeyToID('VK_LSHIFT')) and event.KeyID == HookConstants.VKeyToID('VK_SNAPSHOT'):
            # print "Shift+Print screen"
            self.logger.info('KeyboardEvent : Shift+Print screen ')
            if self.event_manager.get_recording_status():
                self.event_manager.fill_buffers(Event_type[event.MessageName], 160, event.KeyID)

        # "CTRL+key"
        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')):
            # if button ctr is DOWN only !!
            # self.logger.info('KeyboardEvent CTRL: %s %s ',event.MessageName, hex(event.KeyID))
            if self.event_manager.get_recording_status():
                if event.Key in string.ascii_uppercase:
                    # if ctrl pressed and The uppercase letters 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    self.event_manager.fill_buffers(Event_type[event.MessageName], 162, event.KeyID)
                if self.event_manager.get_capture_status():
                    self.event_manager.fill_buffers(Event_type[event.MessageName], 0, event.KeyID)
                    t = threading.Thread(target=self.event_manager.do_capture_screen)
                    t.start()
        # Keys
        else:
            if self.event_manager.get_recording_status() or self.event_manager.get_send_tcp_status() or \
                    self.event_manager.get_send_rs232_status():
                self.event_manager.fill_buffers(Event_type[event.MessageName], 0, event.KeyID)
            if event.MessageName == 'key down' and self.event_manager.get_capture_status():
                t = threading.Thread(target=self.event_manager.do_capture_screen)
                t.start()

        return True

    def hook_mouse_and_key(self):
        self.hm.SubscribeMouseMove(self.move)
        self.hm.SubscribeMouseLeftDown(self.left_down)
        self.hm.SubscribeMouseRightDown(self.right_down)
        self.hm.SubscribeMouseMiddleDown(self.middle_down)
        self.hm.SubscribeMouseLeftUp(self.left_down)
        self.hm.SubscribeMouseRightUp(self.right_down)
        self.hm.SubscribeMouseMiddleUp(self.middle_down)
        self.hm.SubscribeMouseWheel(self.wheel)
        #         self.hm.MouseAll = self.on_mouse_event
        self.hm.HookMouse()

        # hook keyboard
        self.hm.KeyDown = self.on_keyboard_event  # watch for all keyboard events
        self.hm.KeyUp = self.on_keyboard_event
        self.hm.HookKeyboard()

        try:
            pythoncom.PumpMessages()
        except KeyboardInterrupt:
            pass

    def un_hook_mouse_and_key(self):
        self.hm.UnhookMouse()
        self.hm.UnhookKeyboard()
