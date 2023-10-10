from abc import ABCMeta, abstractmethod

class ICommand(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def execute(*args):
        ...