"""Lets the Homeflix TV app find this server on the home network without anyone typing its address.

The app sends one UDP broadcast, "HOMEFLIX?", to DISCOVERY_PORT. Every Homeflix server on the network answers the
sender with "HOMEFLIX <web port> <computer name>", and the app opens http://<answering address>:<web port>.
Nothing is sent unless asked, so this costs nothing while nobody is looking.
"""
import socket
import threading

DISCOVERY_PORT = 5099
QUESTION = b'HOMEFLIX?'


def answer_loop(web_port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', DISCOVERY_PORT))
    except OSError as e:
        print(f"Ağda bulunma kapalı (UDP {DISCOVERY_PORT} açılamadı): {e}")
        return
    reply = f"HOMEFLIX {web_port} {socket.gethostname()}".encode('utf-8', 'replace')[:200]
    while True:
        try:
            data, addr = sock.recvfrom(64)
            if data.strip() == QUESTION:
                sock.sendto(reply, addr)
        except OSError:
            continue


def start(web_port):
    threading.Thread(target=answer_loop, args=(web_port,), daemon=True, name="discovery").start()
