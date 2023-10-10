from pysm import State, Event
from ..HAL.UR.IUr import IUr
import logging
import os
import threading
from ..States.IUrSm import IUrSm
class SDisconnecting(State):
    def __init__(self, name, urSm:IUrSm, concreteSecNodeUr:IUr):
        super().__init__(name)
        self.__SetupLogging()
        self.__mSecNodeUr = concreteSecNodeUr
        self.__mNextStatus = None
        self.__mCnt = 0
        #self.__mSecNodeUrReceivingThread = None
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
        message = state.name
        self.__mUrSm.UpdateUi(message)

    def __on_exit(self, state, event):
        logging.info("ON Exit State:\"%s\"", state.name)
        logging.info("transition:\"%s\"", event.name)
        pass

    def DoTransition(self, state, event):
        logging.info("ON Doing State:\"%s\"", state.name)
        logging.info("transition:\"%s\"", event.name)
        self.__mNextStatus = "es02sExit"
        if self.__mSecNodeUr.IsConnected():
            self.__mSecNodeUr.DoDisconnect()
            receiver_thread = self.__mUrSm.GetNameOfSecNodeUrReceiverThread()
            thread = threading.enumerate()
            for t in thread:
                if t in thread:
                    if t.getName() == receiver_thread:
                        t.join()

            self.__mUrSm.ClearDoDisconnectFlag()
            logging.info("Verbindung zum Server trennen")
        else:
            logging.info("Bereits Verbindung zum Server getrennt")

        if self.__mNextStatus is not "":
            event.state_machine.dispatch(Event(self.__mNextStatus))

    def register_handlers(self):
        self.handlers = {
            "enter": self.__on_enter,
            "exit": self.__on_exit,
        }