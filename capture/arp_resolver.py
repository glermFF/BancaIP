from scapy.all import Ether, ARP, srp
from capture.exception import DeviceNotRespondingError

class ArpResolver:
    def __init__(self, interface):
        self.interface = interface

    def resolve_mac(self, target_ip, timeout_sec=5):
        request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip)
        answered, unanswered = srp(request, iface=self.interface, timeout=timeout_sec, verbose=False)

        if len(answered) == 0:
            raise DeviceNotRespondingError("Sem resposta ARP de " + target_ip + " na interface " + self.interface)

        sent_packet, received_packet = answered[0]
        return received_packet.hwsrc