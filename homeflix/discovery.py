"""Lets the Homeflix TV app find this server on the home network, so nobody has to type its address.

The app broadcasts DISCOVER_QUERY to DISCOVERY_PORT over UDP; every Homeflix server on the network answers it
with its port and computer name. The app takes the address from the answer's sender, so it still finds the
server after the router gives the computer a new address.
"""
import json
import socket
import threading

DISCOVERY_PORT = 5099
DISCOVER_QUERY = b'HOMEFLIX_DISCOVER'


def _answer_loop(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(('', DISCOVERY_PORT))
    except OSError as e:
        print(f"Ağda bulunma kapalı (UDP {DISCOVERY_PORT} kullanılamıyor: {e})")
        return
    reply = json.dumps({'app': 'homeflix', 'port': port, 'name': socket.gethostname()}).encode()
    while True:
        try:
            data, addr = sock.recvfrom(512)
            if data.strip() == DISCOVER_QUERY:
                sock.sendto(reply, addr)
        except OSError:
            pass


def start(port):
    threading.Thread(target=_answer_loop, args=(port,), daemon=True).start()
