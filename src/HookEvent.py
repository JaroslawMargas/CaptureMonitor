# an example of tracking activities
import win32api
import win32gui
import pythoncom
import pyHook
from pyHook import GetKeyState, HookConstants
import CaptureScreen


class HookEvent():
    
    def __init__ (self):
        self.handle = None # handle
        self.hm = pyHook.HookManager()
        self.enum = CaptureScreen.CaptureScreen()
        print "Numer of display devices: " +str(self.enum.enumDisplayDevices())
        print "Numer of physical monitors: " +str(self.enum.enumVisibleMonitors())
            
    def getCursorPosition(self):
        self.flags, self.handle, (x,y) = win32gui.GetCursorInfo()
        return (x,y)
 
    def identyfyMonitorParams(self):
        print win32api.GetMonitorInfo(win32api.MonitorFromPoint(win32api.GetCursorPos()))
        # Monitor': (1920, 0, 3200, 1024)
        # second monitor wight  =3200 -first monitor wight 1920 = 1280 
        monitorInfo = win32api.GetMonitorInfo(win32api.MonitorFromPoint(win32api.GetCursorPos()))
        
        self.widthOffset = monitorInfo.get('Monitor')[0]
        self.all_width = monitorInfo.get('Monitor')[2]
        self.width = self.all_width-self.widthOffset
        print "width " +str(self.width)
        
        self.hightOffset = monitorInfo.get('Monitor')[1]
        self.all_hight = monitorInfo.get('Monitor')[3]
        self.height = self.all_hight-self.hightOffset
        
        print "width " +str(self.height)
        
        #this function set member _width, _hight 
        
    def doCaptureScreen(self):
        captureScreen = CaptureScreen.CaptureScreen()
        captureScreen.setCaptureParams(self.width,self.height,self.widthOffset,self.hightOffset)
        captureScreen.grabAHandle()
        captureScreen.determineSizeMonitors()
        captureScreen.createContext()
        captureScreen.createMemory()
        # it take a monitor resolution after clicking and create proper bitmaps 
        captureScreen.createBitmap()
        captureScreen.copyScreenToMemory()
        captureScreen.saveBitmapToFile()
        captureScreen.freeObjects()
    

    def left_down(self,event):
        self.identyfyMonitorParams()
        print event.MessageName
        (x,y) = self.getCursorPosition()
        self.doCaptureScreen()
        print x,y
        return True 
    
    def right_down(self,event):
        self.identyfyMonitorParams()
        print event.MessageName
        (x,y) = self.getCursorPosition()
        self.doCaptureScreen()
        print x,y
        return True    
    
    def middle_down(self,event):
        self.identyfyMonitorParams()
        print event.MessageName
        (x,y) = self.getCursorPosition()
        self.doCaptureScreen()
        print x,y
        return True
         
    def wheel(self,event):
        self.identyfyMonitorParams()
        print event.Wheel
        (x,y) = self.getCursorPosition()
        self.doCaptureScreen()
        print x,y
        return True
    
    def onKeyboardEvent(self,event):
        #print chr(event.Ascii)WM_KEYUPWM_KEYUPWM_KEYUPWM_KEYUP
        if GetKeyState(HookConstants.VKeyToID('VK_LSHIFT')) and event.KeyID == HookConstants.VKeyToID('VK_SNAPSHOT'):
            print "Shitf+Print screen"
        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and event.KeyID == 67:
            print "ctrl+C"
        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and event.KeyID == 86:
            print "ctrl+V"
        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and event.KeyID == 83:
            print "ctrl+S"
        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and event.KeyID == 65:
            print "ctrl+A"
        else:
            print "event id " + str(event.KeyID)
            self.identyfyMonitorParams()
            print event.MessageName
            (x,y) = self.getCursorPosition()
            #self.doCaptureScreen()
        #print HookConstants.IDToName(event.KeyID) # RETURNS FROM kEYID NAME OF KEY.
        return True
    
    # hook mouse
    def hookMouseAndKey(self):
        self.hm.SubscribeMouseLeftDown(self.left_down)
        self.hm.SubscribeMouseRightDown(self.right_down)
        self.hm.SubscribeMouseMiddleDown(self.middle_down)
        self.hm.SubscribeMouseLeftUp(self.left_down)
        self.hm.SubscribeMouseRightUp(self.right_down)
        self.hm.SubscribeMouseMiddleUp(self.middle_down)
        self.hm.SubscribeMouseWheel(self.wheel)
        self.hm.HookMouse()
        
        #hook keyboard
        self.hm.KeyDown = self.onKeyboardEvent # watch for all keyboard events
        #hm.KeyUp = onKeyboardEvent
        self.hm.HookKeyboard()
        
        while True:
            try:
                while True:
                    pythoncom.PumpWaitingMessages()
            except KeyboardInterrupt:
                pass
# pythoncom.PumpMessages()
        
    def unHookMouseAndKey(self):    
        self.hm.UnhookMouse()
        self.hm.UnHookKeyboard()
        