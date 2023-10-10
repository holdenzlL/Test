from pysm import State, Event
from ..HAL.UR.IUr import IUr
import logging
import os
from ..States.IUrSm import IUrSm
class SAnalysingResponse(State):
    def __init__(self, name, urSm: IUrSm, concreteSecNodeUr:IUr):
        super().__init__(name)
        self.__SetupLogging()
        self.__mSecNodeUr = concreteSecNodeUr
        self.__mNextStatus = None
        self.__mCnt = 0
        #self.__mSecNodeUrReceivingThread = None
        self.__mUrSm = urSm
        self.__AcceptableResponseList = ["running","Loading program","Starting program", "pong", "SECoP", "changed", "done", "reply", "error"]

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
        self.__mNextStatus = ""
        response_from_receiver = self.__mSecNodeUr.GetLastResponse().lower()
        cmd_from_sender = self.__mUrSm.GetCmd().lower()
        first_word = cmd_from_sender.split(' ', 1)
        acceptance_state = False
        for known_answer in self.__AcceptableResponseList:
            if known_answer.lower() in response_from_receiver:
                acceptance_state = True
                break
        if acceptance_state is True:
            logging.info("Server hat die empfangene Nachricht als valide erkannt.")
            logging.info("Das ist vom Client empfangene Nachricht: {}".format(self.__mUrSm.GetCmd()))
            message = "Analyse hat gezeigt, dass das versendete Kommando \"" + self.__mUrSm.GetCmd() + "\" für UR valide ist."
            self.__mUrSm.UpdateUi(message)
            #TODO: hier kann die weitere Analyse eingefügt werden
            if ("starting program" in response_from_receiver) or ("program running: true" in response_from_receiver) : #TODO check busy string
                self.__mNextStatus = "es14s15"#wait till order is done and sec node is in idle again
            else:
                self.__mNextStatus = "es14s10"
        else:
            message = "Analyse hat gezeigt, dass das versendete Kommando \"" + self.__mUrSm.GetCmd() + "\" für UR unbekannt ist."
            self.__mUrSm.UpdateUi(message)
            self.__mNextStatus = "es14s10"
        if self.__mUrSm.IsDoDisconnectFlag():
            self.__mNextStatus = "es14s11"

        if self.__mNextStatus != "":
            event.state_machine.dispatch(Event(self.__mNextStatus))

    def register_handlers(self):
        self.handlers = {
            "enter": self.__on_enter,
            "exit": self.__on_exit,
        }
