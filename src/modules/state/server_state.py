import logging
import threading
from .question_set import QUESTIONS
from ..type.aliases import *
from ..serializable import serializer as s

logger = logging.getLogger()
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)


class ServerState:
    def __init__(self, ip, port):
        self.__addr = (ip, port)

        self.__referee_sockets_lock = threading.Lock()
        self.__referee_sockets = []

        # players states
        self.__player_states_lock = threading.Lock()  # guard both states and top5
        self.__player_states: PlayerStates = {}
        self.__top5players: LeadersBoard = []

        # only main thread should access
        self.__listeners: list[threading.Thread] = []

        # game state / info
        self.__game_starts = threading.Semaphore(0)
        # for now: will be initialized after the playerCount is finalized
        self.__game_ends = None

        # TODO: change later to receive from the referee: default / customized
        self.__questions = []
        self.__questions_lock = threading.Lock()

    def get_server_addr(self):
        return self.__addr

    def add_listener(self, listener):
        self.__listeners.append(listener)

    def add_player(self, psocket: Socket, paddr: Addr, pname: Name, plock: threading.Lock):
        logger.debug("Adding player {%s, %s, %s}", pname, psocket, paddr)

        with self.__player_states_lock:
            self.__player_states[(psocket, paddr)] = (
                pname, [], plock, threading.Semaphore(0))

        logger.info("Added player {%s, %s, %s}",
                    pname, psocket.getsockname(), paddr)

    def remove_player(self, socket_addr: SocketAddr):
        with self.__player_states_lock:
            if socket_addr in self.__player_states:
                del self.__player_states[socket_addr]
        logger.info("Removed connection from %s", socket_addr)

    def player_wait_start_game(self, socket_addr: SocketAddr):
        player = None
        with self.__player_states_lock:
            player = self.__player_states.get(socket_addr, None)
        if player is not None:
            player[-1].acquire()

    def player_signal_start_game(self, socket_addr: SocketAddr):
        with self.__player_states_lock:
            if socket_addr in self.__player_states:
                self.__player_states[socket_addr][-1].release()

    def num_players(self):
        with self.__player_states_lock:
            return len(self.__player_states)

    def update_player_progress(self, socket_addr: SocketAddr, new_progress: PlayerProgress):
        with self.__player_states_lock:
            name, _, lock, game_start_lock = self.__player_states[socket_addr]
            self.__player_states[socket_addr] = name, new_progress, lock, game_start_lock
            logger.info(
                "Player {%s} progress has been updated: %s", name, new_progress)

    # Return the updated top5players if there's a non-trivial update, otherwise return None
    def update_top5(self):
        with self.__player_states_lock:
            name_progress_list = [(n, len(p))
                                  for n, p, l, _ in list(self.__player_states.values())]
            new_top5 = sorted(name_progress_list,
                              key=lambda x: x[1], reverse=True)[:5]
            logger.debug("The new top5 players are %s", new_top5)

            if new_top5 != self.__top5players:
                self.__top5players = new_top5
                return new_top5
            return None

    def get_all_player_names(self) -> list[Name]:
        with self.__player_states_lock:
            players = [n for (n, _, _, _) in list(
                self.__player_states.values())]
            logger.debug("Get all players: %s", players)
            return players

    def get_all_player_sockets_with_locks(self) -> list[tuple[Name, Socket, Lock]]:
        with self.__player_states_lock:
            player_sockets = [(n, s, l) for (s, _), (n, _, l, _)
                              in list(self.__player_states.items())]
            logger.debug("Get all %d player sockets", len(player_sockets))
            return player_sockets

    def get_all_socket_addr(self):
        with self.__player_states_lock:
            return list(self.__player_states.keys())

    def get_socket_addr(self, addr: Addr):
        with self.__player_states_lock:
            return self.__player_states.get(addr, None)

    def get_questions(self):
        with self.__questions_lock:
            return self.__questions

    def add_question(self, new_question):  # for referee
        with self.__questions_lock:
            self.__questions.append(new_question)
            logger.info("Question appended to the set: %s", new_question)

    def set_questions(self, new_questions):
        with self.__questions_lock:
            self.__questions = new_questions

    def choose_question_set(self, idx: int):
        with self.__questions_lock:
            self.__questions = QUESTIONS[idx]

    def wait_game_start(self):
        self.__game_starts.acquire()

    def signal_game_start(self):
        self.__game_starts.release()
