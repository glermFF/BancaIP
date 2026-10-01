import time
from capture.exception import LinkNotUpError


def read_sysfs(interface, filename):
    path = "/sys/class/net/" + interface + "/" + filename
    file = open(path)
    value = file.read().strip()
    file.close()
    return value

class LinkMonitor:
    def __init__(self, interface):
        self.interface = interface

    def is_link_up(self):
        state = read_sysfs(self.interface, "operstate")
        return state == "up"

    def get_speed_mbps(self):
        try:
            return int(read_sysfs(self.interface, "speed"))
        except (OSError, ValueError):
            return None

    def get_duplex(self):
        try:
            return read_sysfs(self.interface, "duplex")
        except OSError:
            return None

    def wait_for_link_up(self, timeout_sec=10):
        start = time.time()

        while time.time() - start < timeout_sec:
            if self.is_link_up():
                link_info = {}
                link_info["up"] = True
                link_info["speed_mbps"] = self.get_speed_mbps()
                link_info["duplex"] = self.get_duplex()
                return link_info

            time.sleep(0.5)

        raise LinkNotUpError("Link não subiu em " + self.interface + " dentro de " + str(timeout_sec) + " segundos")