
import pygame
import time
import os
import socket
import threading

from .lib import UI

SERVER_IP = socket.gethostbyname(socket.gethostname())
PORT = 5001

FORMAT = "UTF-8"
HEADER = 128

Lock = threading.Lock()

class Account:

    Accounts = list()
    ActiveAccount = None

    @classmethod
    def NumberOfAccounts(cls):
        try:
            Lock.acquire()
        finally:
            NumberOfAcc = len(cls.Accounts)
            Lock.release()
        return NumberOfAcc

    @classmethod
    def SetActiveAccount(cls, account):
        try:
            Lock.acquire()
        finally:
            cls.ActiveAccount = account
            Lock.release()

    @classmethod
    def RemoveActiveAccount(cls):
        try:
            Lock.acquire()
        finally:
            cls.ActiveAccount = None
            Lock.release()

    def __init__(self, _id_, name, Socket, address):
        pass
