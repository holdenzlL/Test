from pysm import State, Event
import logging
import os
import time
from ..States.IUrSm import IUrSm

class SWaiting4Order(State):
    def __init__(self, name, urSm: IUrSm):
        super().__init__(name)
        self.__SetupLogging()
        self.__mStateCnt = 0
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
        pass

    def __on_exit(self, state, event):
        logging.info("ON Exit State:\"%s\"", state.name)
        logging.info("transition:\"%s\"", event.name)
        pass

    def DoTransition(self, state, event):
        logging.info("ON Doing State:\"%s\"", state.name)
        logging.info("transition:\"%s\"", event.name)
        self.__mNextStatus = ""
        time.sleep(0.5)
        self.__mStateCnt +=1
        logging.info("Cycle nr.:{}".format(self.__mStateCnt))

        if (self.__mUrSm.IsDoDisconnectFlag()):
            self.__mNextStatus = "es10s11"
        if (self.__mUrSm.IsDoSendFlag()):
            self.__mNextStatus = "es10s12"
        else:
            logging.info("#######################################SendFlag  False:{}".format(self.__mUrSm.IsDoSendFlag()))

        if self.__mNextStatus is not "":
            event.state_machine.dispatch(Event(self.__mNextStatus))

    def register_handlers(self):
        self.handlers = {
            "enter": self.__on_enter,
            "exit": self.__on_exit,
        }
    #def register_handlers(self):
    #    self.handlers = {
    #        'my_event': self.handle_my_event,
    #        '&': self.handle_my_event,
    #        frozenset([1, 2]): self.handle_my_event
    #    }
