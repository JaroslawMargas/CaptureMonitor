import logging
import pythoncom
import pyHook
from pyHook import GetKeyState, HookConstants
import CaptureScreen
import threading
import time
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
        self.start_time = time.time()
        self.enum = CaptureScreen.CaptureScreen()
        self.logger.debug('Number of display devices: %s ', str(self.enum.enum_display_devices()))
        self.logger.debug('Number of physical monitors: %s ', str(self.enum.get_visible_monitors()))

        self.monitor = MonitorParams.MonitorParams()

    def move(self, event):
        self.logger.debug('Mouse event : %s ', event.MessageName)
        if self.event_manager.get_recording_status():
            self.event_manager.fill_event_list(Event_type[event.MessageName], 0, 0)
        return True

    def left_down(self, event):
        self.logger.debug('Mouse event : %s ', event.MessageName)
        if self.event_manager.get_recording_status():
            self.event_manager.fill_event_list(Event_type[event.MessageName], 0, 1)
            t = threading.Thread(target=self.event_manager.do_capture_screen)
            t.start()

        return True

    def right_down(self, event):
        self.logger.debug('Mouse event : %s ', event.MessageName)
        if self.event_manager.get_recording_status():
            self.event_manager.fill_event_list(Event_type[event.MessageName], 0, 2)
            t = threading.Thread(target=self.event_manager.do_capture_screen)
            t.start()

        return True

    def middle_down(self, event):
        self.logger.debug('Mouse event : %s ', event.MessageName)
        if self.event_manager.get_recording_status():
            self.event_manager.fill_event_list(Event_type[event.MessageName], 0, 4)
            t = threading.Thread(target=self.event_manager.do_capture_screen)
            t.start()

        return True

    def wheel(self, event):
        self.logger.debug('Mouse event : %s ', event.MessageName)
        if self.event_manager.get_recording_status():
            self.event_manager.fill_event_list(Event_type[event.MessageName], 0, event.Wheel)

        return True

    def on_keyboard_event(self, event):
        # "ALT+V record event "    
        if GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x56", 16):
            if self.event_manager.get_recording_status():
                if event.MessageName == 'key sys down':
                    # key sys down when ALT+V pressed. Key down if single key
                    # add the last up ALT , before stop recording
                    self.event_manager.fill_event_list(Event_type["key sys up"], 0, 164)
                    self.event_manager.set_stop_recording()
                    self.logger.info('Capture : STOP Recording ')
            else:
                if not self.event_manager.get_playback_status():
                    if event.MessageName == 'key sys down':
                        # key sys down when ALT+V pressed. Key down if single key
                        self.event_manager.set_start_recording()
                        self.logger.info('Capture : START Recording ')
                        self.start_time = time.time()
                else:
                    self.logger.info('If you want record event, please first stop playback ')

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
                        t = threading.Thread(target=self.event_manager.play_event_list())
                        t.start()
                else:
                    self.logger.info('If you want play event, please first stop recording ')
        # ALT+S Save current list.
        elif GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x53", 16):
            if not self.event_manager.get_recording_status() and not self.event_manager.get_playback_status():
                if event.MessageName == 'key sys down':
                    self.event_manager.save_event_list()
                    self.logger.info('Saving List')
            else:
                self.logger.info('If you want save list, please first stop playback and capture ')
        # ALT+L Load merged xml files
        elif GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x4C", 16):
            if not self.event_manager.get_recording_status() and not self.event_manager.get_playback_status():
                if event.MessageName == 'key sys down':
                    self.event_manager.load_xml_files()
                    self.logger.info('Merge xml files into the command list')
                    # for element in self.event_list:
                    #     print element
        # "ALT+N clear recording list"
        elif GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x4e", 16):
            if not self.event_manager.get_recording_status() and not self.event_manager.get_playback_status():
                if event.MessageName == 'key sys down':
                    self.event_manager.clear_event_list()
                    self.logger.info('Event List : clear ')
            else:
                self.logger.info('If you want clear list, please first stop playback and capture ')

        elif GetKeyState(HookConstants.VKeyToID('VK_LSHIFT')) and event.KeyID == HookConstants.VKeyToID('VK_SNAPSHOT'):
            # print "Shift+Print screen"
            self.logger.info('KeyboardEvent : Shift+Print screen ')
            if self.event_manager.get_recording_status():
                print event.MessageName
                self.event_manager.fill_event_list(Event_type[event.MessageName], 160, event.KeyID)

        # "CTRL+key"
        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')):
            # if button ctr is DOWN only !!
            # self.logger.info('KeyboardEvent CTRL: %s %s ',event.MessageName, hex(event.KeyID))
            if self.event_manager.get_recording_status():
                if event.Key in string.ascii_uppercase:
                    # if ctrl pressed and The uppercase letters 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    self.event_manager.fill_event_list(Event_type[event.MessageName], 162, event.KeyID)
                    t = threading.Thread(target=self.event_manager.do_capture_screen)
                    t.start()
                else:
                    self.event_manager.fill_event_list(Event_type[event.MessageName], 0, event.KeyID)
                    t = threading.Thread(target=self.event_manager.do_capture_screen)
                    t.start()
        # Keys
        else:
            # self.logger.info('KeyboardEvent : %s %s ',event.MessageName, hex(event.KeyID))
            if self.event_manager.get_recording_status():
                if event.MessageName == 'key down':
                    self.event_manager.fill_event_list(Event_type[event.MessageName], 0, event.KeyID)
                    t = threading.Thread(target=self.event_manager.do_capture_screen)
                    t.start()
                else:
                    self.event_manager.fill_event_list(Event_type[event.MessageName], 0, event.KeyID)
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
