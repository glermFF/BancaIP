import subprocess
import json
import time
from capture.exception import ThroughputTestFailedError

IPERF3_PORT = 5201

def iperf3_in_namespace(namespace, args):
    return ["ip", "netns", "exec", namespace, "iperf3"] + args

def extract_mbps(iperf3_json):
    bits_per_second = iperf3_json["end"]["sum_received"]["bits_per_second"]
    return round(bits_per_second / 1_000_000, 2)

class ThroughputTester:
    def run_through(self, server_namespace, server_ip, client_namespace, duration_sec=10):
        server = subprocess.Popen(
            iperf3_in_namespace(server_namespace, ["-s", "-1", "-p", str(IPERF3_PORT)]),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        time.sleep(1)

        try:
            client_command = iperf3_in_namespace(
                client_namespace,
                ["-c", server_ip, "-p", str(IPERF3_PORT), "-t", str(duration_sec), "-J"],
            )

            resultado = subprocess.run(
                client_command,
                capture_output=True,
                text=True,
                timeout=duration_sec + 10,
            )

            if resultado.returncode != 0:
                raise ThroughputTestFailedError(resultado.stderr)

            iperf3_json = json.loads(resultado.stdout)
            return {"measured_mbps": extract_mbps(iperf3_json)}
        finally:
            server.wait(timeout=5)