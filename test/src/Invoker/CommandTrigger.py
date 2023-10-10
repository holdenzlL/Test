import logging
from ..Commands.ICommand import ICommand

from flask import session
from flask_socketio import emit, join_room, leave_room
#from ..app import CustomManager
from flask_socketio import SocketIO

class CommandTrigger:
    def __init__(
            self,
            socketio: SocketIO,
            cmdConnect:ICommand,
            cmdDisconnect: ICommand,
            cmdSendCommand: ICommand,
            #cmdLoadCommand: ICommand,
            #cmdUnloadCommand: ICommand,
            #cmdGetVersion: ICommand,
            #cmdGetHome: ICommand,
            #cmdGetPos1: ICommand

    ):
        self.mSocketIo = socketio
        self.mCmdConnect = cmdConnect
        self.mCmdDisconnect = cmdDisconnect
        self.mCmdSendCommand = cmdSendCommand
        #self.mCmdLoad = cmdLoadCommand
        #self.mCmdLoad = cmdUnloadCommand

        #self.mCmdGetVersion = cmdGetVersion
        #self.mCmdGetHome = cmdGetHome
        #self.mCmdGetPos1 = cmdGetPos1
        self.mSocketIo.on_event('connect_to_server', self.ConnectToServer, namespace='/')
        self.mSocketIo.on_event('disconnect_from_server', self.DisconnectFromServer, namespace='/')
        self.mSocketIo.on_event('send_command_to_sec_node_ur_server', self.SendCommandToSecNodeUr, namespace='/')
        #socketio.on_event('send_command_to_sec_node_ur_server', self.SendCommandToSecNodeUr, namespace='/')
        #socketio.on_event('send_command_to_sec_node_ur_server', self.SendCommandToSecNodeUr, namespace='/')


        #self.ConnectToServer = socketio.on('connect_to_server')(self._ConnectToServer)

    #@staticmethod
    def ConnectToServer(self, data):
        print("------------------------------------------------")
        print(data['who'])
        self.mCmdConnect.execute()

    def DisconnectFromServer(self, data):
        print(data['who'])
        self.mCmdDisconnect.execute()

    def SendCommandToSecNodeUr(self, data):
        print(data['who'], data['cmd'])
        self.mCmdSendCommand.execute(data['cmd'])


