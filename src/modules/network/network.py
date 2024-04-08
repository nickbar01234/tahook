import logging
import socket
from ..serializable import serializer as s

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

# Thought: network only used by clients? since each client will have a network object and
# server will implement its own message passing protocol => since it keeps the list of clients in its own class


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(5.0)  # may raise socket.timeout exception

    def connect(self, ip: str):
        logger.info("Connecting to %s", ip)
        host, port = ip.split(":")
        self.client.connect((host, int(port)))

        if s.decode_connect_response(self.client.recv(2048)):
            logger.info("Connection established.")
        else:
            logger.error("Connection failed to establish.")

    def send_name(self, name):
        try:
            self.client.send(s.encode_name(name))
            if s.decode_name_response(self.client.recv(2048)):
                logger.info("Player's name is updated on the server.")
            else:
                logger.error(
                    "Player's name is not correctly updated on the server.")
                s.decode_name_response(self.client.recv(2048))
        except socket.error as e:
            print(e)

    def send_questions(self, questions):
        return

    def update_progress(self, name, ans):
        return

    def update_leaderboard(self, top5players):
        return

    def finish_game(self, time):
        return
