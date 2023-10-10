from pysm import State, Event, StateMachine
import logging
import os
import threading
#from typing import override

from ..States.SConnecting import SConnecting
from ..States.SDisconnecting import SDisconnecting
from ..States.SWaiting4Order import SWaiting4Order
from ..States.SWaiting4Response import SWaiting4Response
from ..States.SAnalysingResponse import SAnalysingResponse
from ..States.SWaiting4OrderDone import SWaiting4OrderDone
from ..States.SSendingCmd import SSendingCmd
from ..HAL.UR.DriverUr import DriverUr
from ..States.IUrSm import IUrSm

from flask_socketio import SocketIO, emit

class UrSm(IUrSm, threading.Thread, object):
    #def __init__(self, name="SecNodeSmThread", socketIO2UI: SocketIO=None, emit: emit=None):
    def __init__(self, emit: emit, name="SecNodeSmThread"):
        threading.Thread.__init__(self, name=name)
        self._mStopThreadEvent = threading.Event()
        self._mSleepPeriod = 0.3
        #self.mSocketIO2UI = socketIO2UI
        #self.mSocketIO2UI.on_event('update_text', self.UpdateUi, namespace='/')
        ##self.mSocketIO2UI.on_event('config_ui_elements', self.UpdateUi, namespace='/')
        self.mEmit = emit
        self.__SetupLogging()
        self.mDriverUrSecNode = DriverUr()

        self.__mSm = self.__GetStateMashine()

        #self.__mUrSmThread = None
        self.__mNameOfSecNodeReceivingDaemonThread = None
        self.__mDoDisconnectFlag = False
        self.__mDoConnectFlag = False
        self.__mDoSendingFlag = False
        self.__mCmd = "status"
        # Convert MB to bytes
        desired_stack_size_mb = 500
        desired_stack_size_bytes = desired_stack_size_mb * 1024 * 1024

        # Set the stack size for new threads
        threading.stack_size(desired_stack_size_bytes)

        #self.mSocketIo = socketio

    def __SetupLogging(self):
        log_file = os.path.join(os.path.dirname(__file__), "client_log.log")
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(filename)s - %(levelname)s: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            handlers=[
                                logging.FileHandler(log_file),
                                logging.StreamHandler()
                            ])

    def __GetStateMashine(self):
        state_machine = StateMachine("SecNodeStateMachine")
        s0 = StateMachine("s0")
        s01 = SConnecting("s01 - State SConnecting", self, self.mDriverUrSecNode)
        s1 = StateMachine("s1")
        s10 = SWaiting4Order("s10 - State SWaiting4Order", self)
        s02 = SDisconnecting("s02 - State SDisconnecting", self, self.mDriverUrSecNode)
        s12 = SSendingCmd("s12 - State SSendingCmd", self, self.mDriverUrSecNode)
        s13 = SWaiting4Response("s13 - State SWaiting4Response", self, self.mDriverUrSecNode)
        s14 = SAnalysingResponse("s14 - State SAnalysingResponse", self, self.mDriverUrSecNode)
        s15 = SWaiting4OrderDone("s15 - State SWaiting4OrderDone", self, self.mDriverUrSecNode)
        sExit = State("sExit") # pseudo state

        state_machine.add_state(s0, initial=True)
        s0.add_state(s01, initial=True)
        s0.add_state(s02)

        state_machine.add_state(s1)
        s1.add_state(s10, initial=True)
        s1.add_state(s12)
        s1.add_state(s13)
        s1.add_state(s14)
        s1.add_state(s15)
        #add here other states
        #s1.add

        s1.add_state(sExit)  # pseudo state

        s0.add_transition(s01, None, events=["es01"], action=s01.DoTransition)
        s0.add_transition(s01, s1, events=["es01s1"])
        s0.add_transition(s01, s02, events=["es01s02"])

        s1.add_transition(s10, None, events=["es10"], action=s10.DoTransition)
        s1.add_transition(s10, sExit, events=["es10sExit"])
        s1.add_transition(s10, s02, events=["es10s02"])
        s1.add_transition(s10, s12, events=["es10s12"])

        s0.add_transition(s02, None, events=["es02"], action=s02.DoTransition)
        #s1.add_transition(s02, s12, events=["es11s12"])
        s0.add_transition(s02, sExit, events=["es02sExit"])

        s1.add_transition(s12, None, events=["es12"], action=s12.DoTransition)
        s1.add_transition(s12, s02, events=["es12s02"])
        s1.add_transition(s12, sExit, events=["es12sExit"])
        s1.add_transition(s12, s13, events=["es12s13"])

        s1.add_transition(s13, None, events=["es13"], action=s13.DoTransition)
        s1.add_transition(s13, s02, events=["es13s02"])
        s1.add_transition(s13, s14, events=["es13s14"])
        s1.add_transition(s13, sExit, events=["es13sExit"])

        s1.add_transition(s14, None, events=["es14"], action=s14.DoTransition)
        s1.add_transition(s14, s10, events=["es14s10"])
        s1.add_transition(s14, s02, events=["es14s02"])
        s1.add_transition(s14, s15, events=["es14s15"])
        s1.add_transition(s14, sExit, events=["es14sExit"])
        # s1.add_transition(s13, s1xx, events=["es12s1xxx"]) #e.g. verifying response

        s1.add_transition(s15, None, events=["es15"], action=s15.DoTransition)
        s1.add_transition(s15, s10, events=["es15s10"])
        s1.add_transition(s15, s12, events=["es15s12"])
        s1.add_transition(s15, s02, events=["es15s02"])
        #s1.add_transition(s15, sExit, events=["es15sExit"]) # no direkt exit only from state Disconnecting (s02)
        # s1.add_transition(s15, s1xx, events=["es15s1xxx"]) #e.g. verifying response


        external_states = [s0, s01, s02, s1, s10, s12, s13, s14, s15, sExit]

        for state in external_states:
            state.register_handlers()

        state_machine.initialize()
        return state_machine

    def run(self):
        self.SetDoConnectFlag()
        self.__mSm.initialize()#Falls Thread restartet wird
        while not self._mStopThreadEvent.isSet():
            state = self.__RunSecNodeSm()
            if state == "sExit":
                break
            self._mStopThreadEvent.wait(self._mSleepPeriod)

    def join(self, timeout=None):
        """ Stop the thread. """
        self._mStopThreadEvent.clear()
        if self.is_alive() is True:
            self._mStopThreadEvent.set()
            threading.Thread.join(self, timeout)


    def __RunSecNodeSm(self):
        first_word = self.__mSm.leaf_state.name.split(' ', 1)
        # TODO: qickNdirty-------------------
        message = first_word
        self.UpdateUi(message)
        #TODO: end --------------------------
        state_dispatch_parameter = "e" + first_word[0]
        self.__mSm.dispatch(Event(state_dispatch_parameter))
        return self.__mSm.leaf_state.name

    def SetNameOfSecNodeUrReceiverThread(self, name):
        self.__mNameOfSecNodeReceivingDaemonThread = name

    def GetNameOfSecNodeUrReceiverThread(self):
        return self.__mNameOfSecNodeReceivingDaemonThread

    def SetDoConnectFlag(self):
        logging.info("Connect Flag gesetzt.")
        self.__mDoConnectFlag = True

    def ClearDoConnectFlag(self):
        logging.info("Disconnect Flag gelöscht.")
        self.__mDoConnectFlag = False

    def IsConnectFlag(self):
        return self.__mDoConnectFlag
    
    def SetDoDisconnectFlag(self):
        logging.info("Disconnect Flag gesetzt.")
        self.__mDoDisconnectFlag = True

    def ClearDoDisconnectFlag(self):
        logging.info("Disconnect Flag gelöscht.")
        self.__mDoDisconnectFlag = False

    def IsDoDisconnectFlag(self):
        return self.__mDoDisconnectFlag

    def SetDoSendFlag(self):
        logging.info("Sendflag gesetzt. Kommando: {} soll versendet werden".format(self.__mCmd))
        logging.info("++++++++++++++++++++++++++++++++++++++++++++ SetDoSendFlag Address of self = {}".format(id(self)))
        #logging.info("++++++++++++++++++++++++++++++++++++++++++++self-Object:{}".format(self.GetNameOfSecNodeUrReceiverThread()))
        self.__mDoSendingFlag = True

    def ClearDoSendFlag(self):
        logging.info("Sendflag gelöscht.")
        logging.info("++++++++++++++++++++++++++++++++++++++++++++ ClearDoSendFlag Address of self = {}".format(id(self)))
        #logging.info("++++++++++++++++++++++++++++++++++++++++++++self-Object:{}".format(self.GetNameOfSecNodeUrReceiverThread()))

        self.__mDoSendingFlag = False

    def IsDoSendFlag(self):
        logging.info("++++++++++++++++++++++++++++++++++++++++++++IsDoSendFlag Address of self = {}".format(id(self)))
        #logging.info("++++++++++++++++++++++++++++++++++++++++++++self-Object:{}".format(self.GetNameOfSecNodeUrReceiverThread()))
        return self.__mDoSendingFlag

    def SetCmd(self, cmd:str):
        logging.info("Kommando: {} soll versendet werden".format(cmd))
        self.__mCmd = cmd

    def GetCmd(self) ->str:
        return self.__mCmd

    #def __GetUiSocketIO(self):
    #    return self.mSocketIo

    def UpdateUi(self, message:str):
        #self.__GetUiSocketIO().emit('update_text', {'text': message})
        #print("****************************************** UrSm SOCKETIO: {}".format(self.mSocketIO2UI))
        #self.mSocketIO2UI.emit('update_text', {'text': message})
        self.mEmit('update_text', {'text': message})
        #emit('update_text', {'text': message})
