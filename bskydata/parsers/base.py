from abc import ABC, abstractmethod
from typing import Dict, Any


class DataParser(ABC):
    """
    Abstract base class for all parsers.
    Defines the interface for parsing data dictionaries.
    """

    @abstractmethod
    def parse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the given dictionary and return the parsed data.

        Args:
            data (Dict[str, Any]): The input data dictionary to be parsed.

        Returns:
            Dict[str, Any]: The parsed data in a structured format.
        """
        pass

