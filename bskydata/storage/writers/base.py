import typing as t
from abc import ABC, abstractmethod


class DataWriter(ABC):
    @abstractmethod
    def write(self, data: t.Any, destination: str = None, **kwargs):
        """
        Write data to a destination.
        
        :param data: The data to write.
        :param destination: Optional dynamic destination (e.g., file name, database table).
        :param kwargs: Additional parameters for customization.
        """
        pass
