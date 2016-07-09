import socket
import struct
from .telegram import Telegram
from .address import Address
from .devices import devices_
from .globals import Globals

class Multicast:
    MCAST_GRP = '224.0.23.12'
    MCAST_PORT = 3671

    def __init__(self):
        pass

    def send(self, telegram):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        if(Globals.get_own_ip()):
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(Globals.get_own_ip()))

        sock.sendto(telegram.str(), (self.MCAST_GRP, self.MCAST_PORT))

    def recv(self, callback = None):
        print("Starting daemon...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", self.MCAST_PORT))

        if(Globals.get_own_ip()):
            sock.setsockopt(socket.IPPROTO_IP,
                                 socket.IP_ADD_MEMBERSHIP,
                                 socket.inet_aton(self.MCAST_GRP) +
                                 socket.inet_aton(Globals.get_own_ip()))
        else:
            mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_GRP), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)

        while True:
            telegram_data = sock.recv(10240)
            if telegram_data:
                telegram = Telegram()
                telegram.read(telegram_data)

                #telegram.dump()

                if telegram.sender == Globals.get_own_address():
                    #print("Ignoring own telegram")
                    pass

                else:
                    device = devices_.device_by_group_address(telegram.group_address)
                    device.process(telegram)

                    if ( callback ):
                        callback(device,telegram)
