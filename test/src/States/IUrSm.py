from abc import ABCMeta, abstractmethod

class IUrSm(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def SetNameOfSecNodeUrReceiverThread(self, name):
        ...

    @staticmethod
    @abstractmethod
    def GetNameOfSecNodeUrReceiverThread(self):
        ...

    #@staticmethod
    @abstractmethod
    def run(self):
        ...

    @abstractmethod
    def join(self):
        ...

    @staticmethod
    @abstractmethod
    def SetDoConnectFlag(self):
        ...
    @staticmethod
    @abstractmethod
    def ClearDoConnectFlag(self):
        ...

    @staticmethod
    @abstractmethod
    def IsConnectFlag(self):
        ...
    
    @staticmethod
    @abstractmethod
    def SetDoDisconnectFlag(self):
        ...
    @staticmethod
    @abstractmethod
    def ClearDoDisconnectFlag(self):
        ...

    @staticmethod
    @abstractmethod
    def IsDoDisconnectFlag(self):
        ...

    @staticmethod
    @abstractmethod
    def SetDoSendFlag(self):
        ...

    @staticmethod
    @abstractmethod
    def ClearDoSendFlag(self):
        ...

    @staticmethod
    @abstractmethod
    def IsDoSendFlag(self):
        ...

    @staticmethod
    @abstractmethod
    def SetCmd(self, cmd:str):
        ...

    @staticmethod
    @abstractmethod
    def GetCmd(self) ->str:
        ...

    @staticmethod
    @abstractmethod
    def UpdateUi(self, message:str):
        ...
