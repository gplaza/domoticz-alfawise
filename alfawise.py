#!/usr/bin/env python
#v.1.0.0
import Domoticz
import socket
import select

class Alfawise:
    """
     TODO : Find some method to read properties from the device

    """

    POWER = 'comm6'
    POWER_OFF = '0'
    POWER_ON = '1'

    SPEED = 'comm103'
    OFF = '0'
    LOW = '1'
    HIGH = '2'

    TIMER = 'comm102'
    ONE_HOUR = '1'
    THREE_HOURS = '3'
    SIX_HOURS = '6'

    EFFECT = 'comm104'
    GRADIENT = '2'
    FLASH = '3'
    QUIET = '1'

    COLOR = 'comm101'

    OPTION_POWER = 'sa_ctrl'
    OPTION_SPEED = 'h_rank'
    OPTION_TIMER = 'countdown'
    OPTION_EFFECT = 'l_mode'
    OPTION_COLOR = 'l_color'

    def __init__(self, mac, ip='255.255.255.255'):
        self.ip = ip
        self.mac = mac
        self.port = 10002
        self.saved_color = "FFFFFF"
        self.property = dict.fromkeys([self.OPTION_POWER, self.OPTION_COLOR,
                                       self.OPTION_EFFECT, self.OPTION_TIMER,
                                       self.OPTION_SPEED])
        # Test if device is available by pinging it
        #if not self._is_device_reachable(ip):
        #    Domoticz.Debug ("Alfawaise device can't be reached using this ip :" + ip)

    def is_fan_on(self):
        return self.property[self.OPTION_SPEED] != self.OFF

    def is_fan_off(self):
        return self.property[self.OPTION_SPEED] == self.OFF

    def is_light_on(self):
        return self.property[self.OPTION_COLOR] is not None

    def is_light_off(self):
        return self.property[self.OPTION_COLOR] is None

    def is_on(self):
        return self.property[self.OPTION_POWER] == self.POWER_ON

    def is_off(self):
        return self.property[self.OPTION_POWER] == self.POWER_OFF

    def get_property(self, property_name):
        try:
            return self.property[property_name]
        except KeyError:
            print("This property '{}' is not available".format(property_name))
            return None

    def get_all_properties(self):
        return self.property

    def set_rgb_color(self, hexvalue):
        """
            Set the color of the device using hex code.

            :param haxvalue: Color value in hexadecimal code

            :type hexvalue: str
        """
        # Input validation
        # schema = Schema({'hexvalue': str})
        # schema({'hexvalue': hexvalue})
        # Send command
        self._send_command(self.COLOR, self.OPTION_COLOR, hexvalue)
        # Update property
        self.property[self.OPTION_COLOR] = hexvalue
        self.saved_color = hexvalue

    def turn_on(self):
        """
            This method is used to switch on the device
        """
        # Check state
        if 1:
            # Send command
            self._send_command(self.POWER, self.OPTION_POWER, self.POWER_ON)
            # Update property
            self.property[self.OPTION_POWER] = self.POWER_ON

    def turn_off(self):
        """
            This method is used to switch off the device
        """
        # Check state
        if 1:
            # Send command
            self._send_command(self.POWER, self.OPTION_POWER, self.POWER_OFF)
            # Update property
            self.property[self.OPTION_POWER] = self.POWER_OFF

    def toggle(self):
        """
            This method is used to toggle the device
        """
        # Update property
        if self.is_on():
            self.turn_off()
        elif self.is_off():
            self.turn_on()

    def turn_fan_on(self, speed=None):
        """
            This method is used to switch on the fan (mist)
        """
        # Update property
        if (speed is None):
            self.property[self.OPTION_SPEED] = self.LOW
        else:
            self.property[self.OPTION_SPEED] = speed
        # Send command
        self._send_command(self.SPEED, self.OPTION_SPEED, self.property[self.OPTION_SPEED])

    def turn_fan_off(self):
        """
            This method is used to switch off the fan (mist)
        """
        # Send command
        self._send_command(self.SPEED, self.OPTION_SPEED, self.OFF)
        # Update property
        self.property[self.OPTION_SPEED] = self.OFF

    def toggle_fan(self):
        """
            This method is used to toggle the fan (mist)
        """
        # Update property
        if self.is_fan_on():
            self.turn_fan_off()
        elif self.is_off():
            self.turn_fan_on()

    def turn_light_on(self, color=None):
        """
            This method is used to switch on the light
        """
        # Update property
        if (color is None):
            self.property[self.OPTION_COLOR] = self.saved_color
        else:
            self.property[self.OPTION_SPEED] = color
        # Send command
        self._send_command(self.COLOR, self.OPTION_COLOR, self.property[self.OPTION_COLOR])

    def turn_light_off(self):
        """
            This method is used to switch off the light
        """
        # Send command
        self._send_command(self.COLOR, self.OPTION_COLOR, "000000")
        # Update property
        self.property[self.OPTION_COLOR] = None

    def toggle_light(self):
        """
            This method is used to toggle the light
        """
        # Update property
        if self.is_light_on():
            self.turn_light_off()
        elif self.is_light_off():
            self.turn_light_on()

    def read(self):
        bufferSize = 1024        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        command = bytes('{"command":"comm100","password":"1234","deviceid":' + self.mac + ',"modelid":"sj07","phoneid":"020000000000","userid":""}',
                        'UTF-8')
        sock.sendto(command, (self.ip, 10002))
        command = bytes('{"command":"comm1003","deviceid":""' + self.mac + '","modelid":"sj07","phoneid":"020000000000","userid":""}',
                        'UTF-8')
        sock.sendto(command, (self.ip, 10002))
        result = select.select([sock], [], [])
        msg = result[0][0].recv(bufferSize)
        print(msg)
        sock.close()


    def _send_command(self, command_type, command_name, command_value):
        
        bufferSize = 1024
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        command = bytes('{"command":"' + command_type + '", "' + command_name + '":"' + command_value + '","deviceid":"' + self.mac + '","modelid":"sj07","phoneid":"020000000000","userid":""}',
                        'UTF-8')
        sock.sendto(command, (self.ip, 10002))
        sock.close()

    #def _is_device_reachable(self, hostname):
    #    response = os.system("ping -c 1 " + hostname)
        # and then check the response...
    #    if response == 0:
    #        return True
    #    else:
    #        return False