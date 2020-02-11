import logging
import serial
import configparser
import time

module_logger = logging.getLogger('application.RS232Serial')


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


def hexString_to_byteArray(hex_str_command):
    # n = 4
    # command = [int(hex_str_command[i:i + n], 16) for i in range(0, len(hex_str_command), n)]
    # for x in command:
    #     self.hex_buffer.append(x)
    # check_sum = get_check_sum(command)
    # self.hex_buffer.append(int(check_sum, 16))
    # return self.hex_buffer
    hex_buffer = bytearray.fromhex(hex_str_command)
    return hex_buffer


class RS232Serial(object):

    def __init__(self):
        self.logger = logging.getLogger('application.RS232Serial')
        self.config = configparser.RawConfigParser()
        self.config.read("rscommand.ini")
        self.buffer = bytearray()
        self.version = bytearray()
        self.hex_buffer = bytearray()

        self.ser = serial.Serial()
        self.ser.port = self.config.get('settings', "port")
        # print(self.ser.port)
        # self.ser.baudrate = self.config.get('settings', "baudrate")
        # self.ser.port = "COM4"
        # self.ser.baudrate = 9600
        self.ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
        self.ser.parity = serial.PARITY_ODD  # set parity check: no parity
        self.ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
        #         self.ser.xonxoff = False     #disable software flow control
        #         self.ser.rtscts = False     #disable hardware (RTS/CTS) flow control
        #         self.ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control

        #         ser.timeout = None          #block read
        self.ser.timeout = int(self.config.get('settings', "timeout"))
        # read() - set timeout to x seconds (float allowed) returns immediately when the
        # requested number of bytes are available, otherwise wait until the timeout expires and return all bytes that
        # were received until then.
        #         ser.xonxoff = False     #disable software flow control
        #         ser.rtscts = False     #disable hardware (RTS/CTS) flow control
        #         ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
        #         ser.writeTimeout = 2     #timeout for write

        try:
            self.ser.open()
            self.logger.debug("Serial port opened: " + self.ser.port)
        except Exception as err:
            self.logger.debug(err)

    def set_command(self, key, key_pressed):
        try:
            command_version = self.config.get('version', 'key_version')

            if key_pressed:
                command_string = self.config.get('key_pressed', key)
            else:
                command_string = self.config.get('key_released', key)

            self.logger.info("Get command and fill buffer: " + str(command_string))
            self.buffer = hexString_to_byteArray(command_string)
            self.logger.info("Buffer to send: " + str(self.buffer))
            self.logger.info("Get command version and fill buffer: " + str(command_version))
            self.version = hexString_to_byteArray(command_version)
            self.logger.info("Buffer to send: " + str(self.version))
            return True

        except Exception as err:
            self.logger.info("No possible set command: " + str(err))

    def send_command(self):

        try:
            self.ser.write(self.version)
            self.logger.info("Send command: " + str(self.version))
            time.sleep(0.001)
            self.ser.write(self.buffer)
            self.logger.info("Send command: " + str(self.buffer))
            return True
        except Exception as err:
            self.logger.debug("No possible send command: " + str(err))
        return True

    def read_command(self):
        try:
            while True:
                c = self.ser.read(14)
                if c:
                    return c
                else:
                    break
        except Exception as err:
            self.logger.debug("No possible read command: " + str(err))


if __name__ == "__main__":
    rs = RS232Serial()
    rs.set_command("0x35", True)
    rs.set_command("0x34", False)
    rs.send_command()
    rs.read_command()
