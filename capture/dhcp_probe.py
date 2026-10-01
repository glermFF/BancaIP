import random
import time
from scapy.all import Ether, IP, UDP, BOOTP, DHCP, sendp, AsyncSniffer, get_if_hwaddr
from capture.exception import DeviceNotRespondingError


def get_dhcp_message_type(packet):
    for option in packet[DHCP].options:
        if option[0] == "message-type":
            return option[1]
    return None


class DhcpProbe:
    def __init__(self, interface):
        self.interface = interface

    def discover(self, timeout_sec=10):
        station_mac = get_if_hwaddr(self.interface)
        transaction_id = random.randint(1, 0xFFFFFFFF)

        discover_packet = (
            Ether(dst="ff:ff:ff:ff:ff:ff") /
            IP(src="0.0.0.0", dst="255.255.255.255") /
            UDP(sport=68, dport=67) /
            BOOTP(chaddr=station_mac, xid=transaction_id, flags=0x8000) /
            DHCP(options=[("message-type", "discover"), "end"])
        )

        sniffer = AsyncSniffer(iface=self.interface, filter="udp and (port 67 or port 68)")
        sniffer.start()

        sendp(discover_packet, iface=self.interface, verbose=False)
        time.sleep(timeout_sec)
        sniffer.stop()

        for packet in sniffer.results:
            is_offer = packet.haslayer(DHCP) and get_dhcp_message_type(packet) == 2
            is_our_request = packet.haslayer(BOOTP) and packet[BOOTP].xid == transaction_id

            if is_offer and is_our_request:
                return {"mac": packet[Ether].src, "ip": packet[IP].src}

        raise DeviceNotRespondingError("Nenhuma oferta DHCP recebida na interface " + self.interface)