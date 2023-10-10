# Generated by sila2.code_generator; sila2.__version__: 0.10.4
from __future__ import annotations

from typing import TYPE_CHECKING

import socketio.server
from sila2.server import MetadataDict

from ..generated.ursilainterface import SayHello_Responses, UrSilaInterfaceBase


if TYPE_CHECKING:
    from ..server import Server
import socketio

class UrSilaInterfaceImpl(UrSilaInterfaceBase):
    def __init__(self, parent_server: Server) -> None:
        super().__init__(parent_server=parent_server)
        self.mEmit = None
        self.mInvoker = None
    def UpdateInvoker(self, obj):
        self.mInvoker = obj
        print("###################################################################################################  INVOKER ########################")

    def get_StartYear(self, *, metadata: MetadataDict) -> int:
        raise NotImplementedError  # TODO

    def SayHello(self, Name: str, *, metadata: MetadataDict) -> SayHello_Responses:
        try:
            #socketio.Client.server.Server.
            print("******************************************            mSocketIoServer: {}".format(self.mInvoker))
            connect_response = self.mInvoker.SendCommandToSecNodeUr({'who': 'SILA UI', 'cmd': Name})
            #print("SILA SERVER SENDS EMIT: ------ emit with cmd={} and namespace=/".format(Name))
            #connect_response = self.mInvoker.emit('send_command_to_sec_node_ur_server',
            #                                      {'who': 'SILA CLIENT', 'cmd': Name},
            #                                      brooadcast=True)  # , namespace='/')
            #self.mEmit.emit('send_command_to_sec_node_ur_server', {'who': 'SILA CLIENT', 'cmd': Name})  # , namespace='/')
            #self.mEmit('update_text', {'text': "MESSAGE FROM SILA SERVER/CLIENT"})
            #self.mEmit.emit('update_text', {'text': "MESSAGE FROM SILA SERVER/CLIENT"})
            #self.mEmit.emit('update_text', {'text': "MESSAGE FROM SILA SERVER/CLIENT"})
            print("******************************************            mSocketIoServer: {}".format(self.mInvoker))
            print("******************************************            response: {}".format(connect_response))
        except:
            print("App Client:{}" .format(self.mEmit))
            print("###################################################################################################")

        return SayHello_Responses("invoker with command send \"running\" triggered")