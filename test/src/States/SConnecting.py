from pysm import State, Event
from ..HAL.UR.IUr import IUr
import logging
import os
import threading
import time
from .IUrSm import IUrSm
class SConnecting(State):
    def __init__(self, name, urSm: IUrSm, concreteSecNodeUr: IUr):
        super().__init__(name)
        self.__SetupLogging()
        self.__mSecNodeUr = concreteSecNodeUr
        self.__mNextStatus = None
        self.__mCnt = 0
        self.__mSecNodeUrReceivingDaemonThread = None
        self.__mUrSm = urSm


    def __SetupLogging(self):
        log_file = os.path.join(os.path.dirname(__file__), "client_log.log")
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            handlers=[
                                logging.FileHandler(log_file),
                                logging.StreamHandler()
                            ])

    def __on_enter(self, state, event):
        logging.info("ON Enter State:\"%s\"", state.name)
        logging.info("transition:\"%s\"", event.name)
        pass

    def __on_exit(self, state, event):
        logging.info("ON Exit State:\"%s\"", state.name)
        logging.info("transition:\"%s\"", event.name)
        pass

    def DoTransition(self, state, event):
        logging.info("ON Doing State:\"%s\"", state.name)
        logging.info("transition:\"%s\"", event.name)
        self.__mNextStatus = ""
        if self.__mSecNodeUr.Connect(hostname="192.168.162.128", port=29999): #TODO: This part is dirty and must be redesigned
        #in case secnode is running on host system: 172.30.176.1 is the vEthernet (WSL) IP

        #if self.__mSecNodeUr.Connect(hostname="127.0.0.1", port=50055):
        #if self.__mSecNodeUr.Connect(hostname="localhost", port=10770):
        #if self.__mSecNodeUr.Connect(hostname="ifg-PLATZHALTER.ifg.kit.edu", port=10770):
            logging.info("Connection to server ESTABLISHED")
            self.__mNextStatus = "es01s1"
            self.__mSecNodeUrReceivingDaemonThread = threading.Thread(target=self.__RunSecNodeUrReceivingAsAThread)
            self.__mSecNodeUrReceivingDaemonThread.daemon = True
            self.__mSecNodeUrReceivingDaemonThread.setName("__mSecNodeUrReceivingDaemonThread")
            self.__mUrSm.SetNameOfSecNodeUrReceiverThread(self.__mSecNodeUrReceivingDaemonThread.getName())
            self.__mSecNodeUrReceivingDaemonThread.start()
        else:
            logging.info("Connection to server FAILED")
            self.__mNextStatus = "es01s02"

        self.__mUrSm.ClearDoConnectFlag()

        if self.__mNextStatus is not "":
            event.state_machine.dispatch(Event(self.__mNextStatus))

    def register_handlers(self):
        self.handlers = {
            "enter": self.__on_enter,
            "exit": self.__on_exit,
        }

    def __RunSecNodeUrReceivingAsAThread(self):
        logging.info("__RunSecNodeUrReceivingAsAThread")
        while self.__mSecNodeUr and self.__mSecNodeUr.IsConnected():
            logging.info("Sec Node Ur Receiving messages call within a thread")
            #with self.__mSecNodeUr:
            self.__mSecNodeUr.ReceiveMessages()

            time.sleep(0.5)  # max 0.5 secs with in receive_messages() wait for meassages loop
