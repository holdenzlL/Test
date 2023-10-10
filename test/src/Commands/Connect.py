from .ICommand import ICommand
from ..States.IUrSm import IUrSm

class Connect(ICommand):
    def __init__(self, receiver: IUrSm, name: str("universal command")):
        self.mReceiver = receiver
        self.mName = name

    def execute(self, *args):
        self.mReceiver.join()
        #self.mReceiver.SetConnectCmdFlag()
        self.mReceiver.run()
