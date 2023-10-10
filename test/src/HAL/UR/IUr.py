from abc import ABCMeta, abstractmethod

class IUr(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def Connect(self, hostname, port):
        ...

    @staticmethod
    @abstractmethod
    def DoDisconnect(self):
        ...

    @staticmethod
    @abstractmethod
    def SendCommand(self, command):
        ...

    @staticmethod
    @abstractmethod
    def IsConnected(self):
        ...

    @staticmethod
    @abstractmethod
    def IsDisconnected(self):
        ...

    @staticmethod
    @abstractmethod
    def ResetReceivedMessages(self):
        ...

    @staticmethod
    @abstractmethod
    def GetReceivedMessages(self):
        ...

    @staticmethod
    @abstractmethod
    def ReceiveMessages(self):
        ...

    @staticmethod
    @abstractmethod
    def GetLastResponse(self) -> str:
        ...
