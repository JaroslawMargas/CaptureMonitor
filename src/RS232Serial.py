import logging
import serial
import ConfigParser

module_logger = logging.getLogger('application.RS232Serial')

version = bytearray()
version.append(0x40)
version.append(0x05)
version.append(0xD7)
version.append(0x01)
version.append(0x01)
version.append(0x09)
version.append(0xE2)


def scan_ports():
    available = []
    for i in range(256):
        try:
            s = serial.Serial('COM' + str(i))
            available.append(s.portstr)
            s.close()  # explicit close 'cause of delayed GC in java
        except Exception as err:
            module_logger.debug("serial issue: " + str(err))
    return available


def get_check_sum(data):
    i_check = 0x00
    for i in range(data[1] - 1):
        i_check += (data[2 + i])
    check_sum = hex(i_check & 0xFF)
    module_logger.debug("checksum: " + str(check_sum))
    return check_sum


class RS232Serial(object):

    def __init__(self):
        self.logger = logging.getLogger('application.RS232Serial')
        self.config = ConfigParser.RawConfigParser()
        self.config.read("rscommand.ini")
        self.buffer = bytearray()

        self.ser = serial.Serial()
        self.ser.port = self.config.get('settings', "port")
        self.ser.baudrate = self.config.get('settings', "baudrate")
        self.ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
        self.ser.parity = serial.PARITY_ODD  # set parity check: no parity
        self.ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
        #         self.ser.xonxoff = False     #disable software flow control
        #         self.ser.rtscts = False     #disable hardware (RTS/CTS) flow control
        #         self.ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control

        #         ser.timeout = None          #block read
        #         ser.timeout = 1            #non-block read
        #         ser.xonxoff = False     #disable software flow control
        #         ser.rtscts = False     #disable hardware (RTS/CTS) flow control
        #         ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
        #         ser.writeTimeout = 2     #timeout for write

        try:
            self.ser.open()
        except Exception as err:
            self.logger.debug(err)

    def set_command(self, key, key_pressed):

        try:
            hex_buffer = bytearray()
            if key_pressed:
                # command = button_pressed[key]

                # command string convert to list each 4 value ex. 0x40
                command_string = self.config.get('key_pressed', key)
                self.logger.debug("Get pressed command: " + str(command_string))
                n = 4
                command = [int(command_string[i:i + n], 16) for i in range(0, len(command_string), n)]
                self.logger.debug("command RS232: " + str(command))

                check_sum = get_check_sum(command)
            # else released
            else:
                # command = button_released[key]

                # command string convert to list each 4 value ex. 0x40
                command_string = self.config.get('key_released', key)
                self.logger.debug("Get released command: " + str(command_string))
                n = 4
                command = [int(command_string[i:i + n], 16) for i in range(0, len(command_string), n)]
                self.logger.debug("command RS232: " + str(command))

                check_sum = get_check_sum(command)

            for x in command:
                hex_buffer.append(x)
                hex_buffer.append(int(check_sum, 16))
                self.buffer = hex_buffer
            return True
        except Exception as err:
            self.logger.debug("No possible set command: " + str(err))
            return False

    def send_command(self):
        out = ''
        try:
            # while self.ser.inWaiting() > 0:
            out += self.ser.read()
            if out != '':
                # print hex(int(out.encode('hex'), 16))
                # if(hex(int(out.encode('hex'), 16)) == '0x4002d6d6'):
                self.ser.write(version)
                # time.sleep(0.001)
                self.ser.write(self.buffer)
        except Exception as err:
            self.logger.debug(err)
        return True
