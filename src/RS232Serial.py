import logging
import serial

module_logger = logging.getLogger('application.RS232Serial')

button_pressed = {
    "0x70" : (0x40, 0x05, 0xCF, 0x00, 0x08, 0x80),
    "0x71" : (0x40, 0x05, 0xCF, 0x00, 0x10, 0x80),
    "0x72" : (0x40, 0x05, 0xCF, 0x00, 0x18, 0x80),
    "0x73" : (0x40, 0x05, 0xCF, 0x00, 0x20, 0x80),
    "0x74" : (0x40, 0x05, 0xCF, 0x00, 0x28, 0x80),
    "0x75" : (0x40, 0x05, 0xCF, 0x00, 0x30, 0x80),
    "0x76" : (0x40, 0x05, 0xCF, 0x00, 0x38, 0x80),
    "0x77" : (0x40, 0x05, 0xCF, 0x00, 0x43, 0x80),
}

button_released = {
    "0x70" : (0x40, 0x05, 0xCF, 0x00, 0x08, 0x00),
    "0x71" : (0x40, 0x05, 0xCF, 0x00, 0x10, 0x00),
    "0x72" : (0x40, 0x05, 0xCF, 0x00, 0x18, 0x00),
    "0x73" : (0x40, 0x05, 0xCF, 0x00, 0x20, 0x00),
    "0x74" : (0x40, 0x05, 0xCF, 0x00, 0x28, 0x00),
    "0x75" : (0x40, 0x05, 0xCF, 0x00, 0x30, 0x00),
    "0x76" : (0x40, 0x05, 0xCF, 0x00, 0x38, 0x00),
    "0x77" : (0x40, 0x05, 0xCF, 0x00, 0x43, 0x00),
}

version = bytearray()
version.append(0x40)
version.append(0x05)
version.append(0xD7)
version.append(0x01)
version.append(0x01)
version.append(0x09)
version.append(0xE2)


def scan_ports() :
    available = []
    for i in range(256) :
        try :
            s = serial.Serial('COM' + str(i))
            available.append(s.portstr)
            s.close()  # explicit close 'cause of delayed GC in java
        except Exception as err :
            self.logger.debug("serial issue: " + str(err))
    return available


def hex_string_to_dec(hex_input) :
    dec = int(hex_input, 16)
    return dec


def dec_to_hex_string(data) :
    hex_data = hex(data)
    return hex_data


def get_check_sum(data) :
    i_check = 0x00
    for i in range(data[1] - 1) :
        i_check += (data[2 + i])
    check_sum = hex(i_check & 0xFF)
    return check_sum


class RS232Serial(object) :

    def __init__(self) :
        self.logger = logging.getLogger('application.RS232Serial')
        self.stopSendRead = True
        self.sendRequest = False
        self.buffer = bytearray()

        self.ser = serial.Serial()
        self.ser.port = "COM1"
        self.ser.baudrate = 38400
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

        try :
            self.ser.open()
        except Exception as err :
            self.logger.debug(err)

    def set_command(self, key, key_pressed) :
        try:
            hex_buffer = bytearray()
            if key_pressed :
                command = button_pressed[key]
                check_sum = get_check_sum(button_pressed[key])
            else:
                command = button_released[key]
                check_sum = get_check_sum(button_released[key])
            for x in command :
                hex_buffer.append(x)
                hex_buffer.append(int(check_sum, 16))
                self.buffer = hex_buffer
            return True
        except Exception as err :
            self.logger.debug("No possible set command" + str(err))
            return False

    def send_command(self) :
        out = ''
        try :
            # while self.ser.inWaiting() > 0:
            out += self.ser.read()
            if out != '' :
                # print hex(int(out.encode('hex'), 16))
                # if(hex(int(out.encode('hex'), 16)) == '0x4002d6d6'):
                self.ser.write(version)
                # time.sleep(0.001)
                self.ser.write(self.buffer)
        except Exception as err :
            self.logger.debug(err)
        return True
