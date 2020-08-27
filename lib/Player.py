
import pandas as pd
import time
import threading
import socket

class player:
    def __init__(self, _id_, name, rank, ratings, Socket, Address):
        self.id = _id_
        self.name = name
        self.rank = rank
        self.ratings = ratings

        self.Socket = Socket
        self.Address = Address

        self.thread = threading.Thread(target=self.run, args=())

    def get_player_info(self):
        info = {
            "ID": self.id,
            "Name": self.name,
            "Rank": self.rank,
            "Ratings": self.ratings
        }

        return info

    def __repr__(self):
        return str(self.get_player_info())

    def run(self):
        time.sleep(20)
        self.Socket.shutdown(1)
        self.Socket.close()




