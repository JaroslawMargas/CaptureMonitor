import win32api
import win32gui
import win32con
import logging

module_logger = logging.getLogger('application.MonitorParams')


class MonitorParams(object):

    def __init__(self):
        self.logger = logging.getLogger('application.HookEvent')

    def get_cursor_position(self):
        flags, handle, (x, y) = win32gui.GetCursorInfo()
        coordinates = (x, y)
        self.logger.debug('Monitor detection, width: %s ', str(coordinates))
        return coordinates

    def get_monitor_params(self):
        monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromPoint(win32api.GetCursorPos()))
        # self.logger.debug('Monitor info,: %s ', str(monitor_info))

        width_offset = monitor_info.get('Monitor')[0]
        all_width = monitor_info.get('Monitor')[2]
        width = all_width - width_offset

        self.logger.debug('Monitor detection, width: %s ', str(width))

        height_offset = monitor_info.get('Monitor')[1]
        all_height = monitor_info.get('Monitor')[3]
        height = all_height - height_offset

        self.logger.debug('Monitor detection, height: %s ', str(height))

        params_list = [width, height, width_offset, height_offset]
        return params_list

    def enum_display_devices(self):
        i = 0
        while True:
            try:
                device = win32api.EnumDisplayDevices(None, i)
                self.logger.debug('Count [%d] Device: %s DeviceName(%s) ', i, device.DeviceString, device.DeviceName)
                i += 1
            except Exception as ex:
                self.logger.info('exception: %s', ex.message)
                break
            return i

    # this function gets only visible monitors (not  virtual)
    def get_visible_monitors(self, ):
        i = 0
        try:
            i = win32api.GetSystemMetrics(win32con.SM_CMONITORS)
        except Exception as ex:
            self.logger.debug('exception: %s', ex.message)
        return i
