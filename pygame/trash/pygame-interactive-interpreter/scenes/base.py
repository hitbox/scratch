from abc import ABC
from abc import abstractmethod

class BaseScene(ABC):
    """
    Scenes are run by an engine.
    """

    @abstractmethod
    def enter(self):
        pass

    @abstractmethod
    def exit(self):
        pass

    @abstractmethod
    def update(self, events):
        """
        Called every frame.
        """
