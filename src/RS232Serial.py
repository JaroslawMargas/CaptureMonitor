import logging
import serial
import ConfigParser
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


def get_check_sum(data):
    i_check = 0x00
    for i in range(data[1] - 1):
        i_check += (data[2 + i])
    check_sum = hex(i_check & 0xFF)
    # remove 0x from hex
    # check_sum = str('%x' % tmp)
    return check_sum


class RS232Serial(object):

    def __init__(self):
        self.logger = logging.getLogger('application.RS232Serial')
        self.config = ConfigParser.RawConfigParser()
        self.config.read("rscommand.ini")
        self.buffer = bytearray()
        self.version = bytearray()
        self.hex_buffer = bytearray()

        self.ser = serial.Serial()
        self.ser.port = self.config.get('settings', "port")
        self.ser.baudrate = self.config.get('settings', "baudrate")
        # self.ser.port = "COM1"
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

    def fill_buffer(self, hex_str_command):
        n = 4
        command = [int(hex_str_command[i:i + n], 16) for i in range(0, len(hex_str_command), n)]
        for x in command:
            self.hex_buffer.append(x)
        check_sum = get_check_sum(command)
        self.hex_buffer.append(int(check_sum, 16))
        return self.hex_buffer

    def set_command(self, key, key_pressed):
        try:
            command_version = self.config.get('version', 'key_version')

            if key_pressed:
                command_string = self.config.get('key_pressed', key)
            else:
                command_string = self.config.get('key_released', key)

            self.logger.debug("Get command and fill buffer: " + str(command_string))
            self.buffer = self.fill_buffer(command_string)
            self.logger.debug("Get command version and fill buffer: " + str(command_version))
            self.version = self.fill_buffer(command_version)
            return True

        except Exception as err:
            self.logger.debug("No possible set command: " + str(err.message))

    def send_command(self):
        self.logger.debug("Send command: ")
        try:
            self.ser.write(self.version)
            time.sleep(0.001)
            self.ser.write(self.buffer)
            return True
        except Exception as err:
            self.logger.debug("No possible send command: " + str(err.message))
        return True

    def read_command(self):
        try:
            received_string = ''
            while True:
                c = self.ser.read(1)
                if c:
                    received_string += str(hex(int(c.encode('hex'), 16)))
                else:
                    break
            # print(received_string)
            return received_string
        except Exception as err:
            self.logger.debug("No possible read command: " + str(err.message))


if __name__ == "__main__":
    rs = RS232Serial()
    rs.set_command("0x31", True)
    rs.send_command()
    time.sleep(0.001)
    rs.read_command()
