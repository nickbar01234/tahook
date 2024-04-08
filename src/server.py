import logging
import socket
import threading
import sys
from modules import serializer as s
from modules.question.multiple_choice_question_builder import MultipleChoiceQuestionBuilder
from modules.solution.multiple_choice_solution_builder import MultipleChoiceSolutionBuilder


logger = logging.getLogger()
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

# Mock the set of questions TODO: remove once we have an actual set of questions
questions = [
    MultipleChoiceQuestionBuilder()
    .add_question("What's Tony's last name ----")
    .add_option("Doan")
    .add_option("Xu")
    .add_option("Huang")
    .add_solution(MultipleChoiceSolutionBuilder().add_solution("Huang").build())
    .build()
    ]

class Server:
    def __init__(self, ip, port):
        self.addr = (ip, port)
        self.playerCount = 0
        self.playerSockets = {}  # {socket: (addr, name)}
        self.playerState = {}
        self.playerLocks = {}
        self.questions = []
        self.top5players = []
        self.top5playersLock = threading.Lock()

    #  Start the server and wait for client connection
    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(self.addr)
        server_socket.listen()
        logger.info("Server started, listening on %s:%s",
                    self.addr[0], self.addr[1])

        while True:
            player_socket, player_addr = server_socket.accept()
            player_socket.send(s.encode_connect_success())
            logger.info(f"""New connection from {
                            player_addr}, {self.playerCount}""")

            player_listener = threading.Thread(
                target=self.player_listener, args=(player_socket, player_addr))
            player_listener.start()

    # For each listener's thread to receive message form a specific player
    def player_listener(self, player_socket, player_addr):
        try:
            logger.info(
                f"Listener thread started to listen from {player_addr}")
            # finalize establishing connection
            player_name = s.decode_name(player_socket.recv(2048)) # may raise InvalidMessage exception
            logger.info(f"Player's name from {player_addr} is {player_name}")
            self.playerSockets[player_socket] = (player_addr, player_name)
            self.playerCount += 1
            player_socket.send(s.encode_name_response())

            # TODO: Distribution questions - do i need to wait for a signal from the referee?
            player_socket.send(s.encode_questions(questions))

            # TODO: Handling player's status update
            while True:
                data = player_socket.recv(2048)
                if not data:
                    break
                logger.info(f"Receive: {data}")  # binary
                # TODO: some processing to update the state and compute top5
                self.update_leaderboard()
        except:
            logger.error(f"Lost the connection with {player_addr}")
        finally:
            if player_socket in self.playerSockets:
                del self.playerSockets[player_socket]
            player_socket.close()

    # Message protocol for the server to send updates of leaders board to players and referee
    def update_leaderboard(self):
        message = s.encode_leadersboard(self.top5players)
        for player_socket, (player_addr, player_name) in self.playerSockets.items():
            try:
                player_socket.sendall(message)
            except:
                sys.stderr.write(f"Failed to send to {player_addr}")


if __name__ == "__main__":
    IP = socket.gethostbyname(socket.gethostname())
    PORT = 5555
    Server(IP, PORT).start()
