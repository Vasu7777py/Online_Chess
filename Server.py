
import os
import pandas as pd
import numpy as np
import threading
import time
import socket
import json

from lib.Player import player
from lib import Messages

os.system("cls")

FORMAT = "UTF-8"
HEADER = 128
Lock = threading.Lock()

UserLoginData = None

def Load_user_database():
    global UserLoginData
    if not Server.IS_srever_active():
        return
    path = "database/"
    File = f"{path}/UserBD.xlsx"
    UserLoginData = pd.read_excel(File, sheet_name="LoginInfo", index_col=0)
    # print(UserLoginData)

class Server:
    ID = socket.gethostbyname(socket.gethostname())
    PORT = 5001
    ADDRESS = (ID, PORT)

    Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Socket.bind(ADDRESS)
    Socket.settimeout(1)

    Clients = dict()
    Logs = dict()
    Connections = list()

    State = True

    @classmethod
    def New_Connection(cls):
        try:
            connection, address = cls.Socket.accept()
            try:
                Lock.acquire()
            finally:
                code = time.time()
                client_thread = threading.Thread(target=cls.Regester_Connection, args=(connection, address, code))
                cls.Connections.append((connection, address, code))
                Lock.release()
                client_thread.start()
        except socket.timeout as timeout:
            time.sleep(0.3)

    @classmethod
    def IS_srever_active(cls):
        return cls.State

    @classmethod
    def Regester_Connection(cls, connection: socket.socket, address, code):
        # This is trigered by func new_connection
        # this runs in seperate thread created by the function
        # this func returns northing
        connection.settimeout(1)
        Max_time = 3 * 60
        clock_start = time.time()
        trys = 0
        Max_trys = 5
        connected = False
        while (((time.time() - clock_start) < Max_time) and cls.IS_srever_active() and (trys <= Max_trys) and (not connected)):
            message_len = None
            while ((message_len == None) and ((time.time() - clock_start) < Max_time) and cls.IS_srever_active()):
                try:
                    message_len = (connection.recv(HEADER)).decode(FORMAT)
                except socket.timeout:
                    time.sleep(0.2)

            if ((message_len == None) and (not cls.IS_srever_active() )):
                cls.Close_connection(connection, address, code=code)
                return

            try:
                message_len = int(message_len)
            except ValueError:
                cls.Close_connection(connection, address, code=code)
                return
            finally:
                message = None
                while (message == None):
                    try:
                        message = (connection.recv(message_len)).decode(FORMAT)
                    except socket.timeout:
                        pass
                message = message.replace("\'", "\"")
                data = json.loads(message)
                access, message = cls.Login(data)

                if access:
                    #
                    userid = message["UserId"]
                    name = message["Name"]
                    rank = message["Rank"]
                    ratings = message["Ratings"]
                    cl_message = f"{Messages.Connected}: {message}"
                    cls.Send_Message(connection, cl_message)
                    time.sleep(0.7)
                    client = player(userid, name, rank, ratings, connection, address)
                    connected = True
                    try:
                        Lock.acquire()
                    finally:
                        ID = (address[0], address[1], userid)
                        cls.Clients[str(ID)] = client
                        cls.Connections.remove((connection, address, code))
                        Lock.release()
                        print(f"[REMOVED]: {(address, code)}")
                        client.thread.start()
                else:
                    cl_message = f"{Messages.Error}: {message}"
                    cls.Send_Message(connection, cl_message)
                    trys += 1

    @classmethod
    def Send_Message(cls, connection, message):
        if not isinstance(message, str):
            message = str(message)
        msg = message.encode(FORMAT)
        msg_len = str(len(msg)).encode(FORMAT)
        msg_len = msg_len + (b" " * (HEADER - len(msg_len)))
        connection.send(msg_len)
        time.sleep(0.2)
        connection.send(msg)

    @classmethod
    def Close_connection(cls, connection, address, message=None, code=None, ID=None):
        if message:
            cls.Send_Message(connection, message)
        if code:
            try:
                Lock.acquire()
            finally:
                cls.Connections.remove((connection, address, code))
                Log = {
                    Messages.Command: Messages.PRINT,
                    Messages.Disconnected: address
                }
                cls.Logs[str(code)] = Log
                Lock.release()
                connection.shutdown(socket.SHUT_RDWR)
                connection.close()
        elif ID:
            try:
                Lock.acquire()
            finally:
                client = cls.Clients.pop(ID)
                Log = {
                    Messages.Command: Messages.PRINT,
                    Messages.Disconnected: ID
                }
                cls.Logs[str(ID)] = Log
                Lock.release()
                client.Socket.shutdown(socket.SHUT_RDWR)
                client.Socket.close()
                del client

    @classmethod
    def Login(cls, data: dict):

        def getUserData(UserName):
            try:
                Lock.acquire()
                ID = UserLoginData.loc[UserName, "UserId"]
                Rank = UserLoginData.loc[UserName, "Rank"]
                Ratings = UserLoginData.loc[UserName, "Ratings"]
            finally:
                Lock.release()

            info = {
                "UserId": ID,
                "Name": UserName,
                "Rank": Rank,
                "Ratings": Ratings
            }

            return info

        def getPasscode(UserName):
            error = None
            try:
                Lock.acquire()
                Passcode = UserLoginData.loc[UserName, "Passcode"]
            except KeyError:
                error = Messages._KeyError_
            finally:
                if error:
                    return error, None
                else:
                    return error, Passcode

        print(data)
        """
        data = {
            "UserName": "",
            "Passcode": ""
        }
        """
        error, Pascode = getPasscode(data["UserName"])
        if error:
            access = False
            message = {Messages.Error: Messages.User_Name}
        elif (data["Passcode"] == Pascode):
            access = True
            message = getUserData(data["UserName"])
        else:
            access = False
            message = {Messages.Error: Messages.Passcode}

        return access, message

    @classmethod
    def Clear_Logs(cls):
        print("Logs Cleared")

    @classmethod
    def RUN(cls):
        # Here the listen function opens the socket to others so that
        # client can to the server
        cls.Socket.listen()
        while cls.IS_srever_active():
            try:
                cls.New_Connection()
                cls.Clear_Logs()
            except KeyboardInterrupt:
                print(KeyboardInterrupt)
                cls.Clear_Logs()
                cls.State = False

os.system("title Server")
print(Server.ADDRESS)
print(f"[ONLINE] @ [Ip : <{Server.ID}>, PORT : <{Server.PORT}>]")
Load_user_database()
Server.RUN()
# print(UserLoginData["UserName"])
print("[OFFLINE]")

