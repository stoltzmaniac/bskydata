import typing as t
from pathlib import Path
from bskydata.storage.base import DataWriter, JsonFileHandler


class LocalJsonFileWriter(DataWriter):
    def __init__(self, default_file: str = None, indent: int = 4, sort_keys: bool = True):
        """
        :param default_file: Default file name if none is provided dynamically.
        :param indent: Number of spaces to use for indentation (default is 4).
        :param sort_keys: Whether to sort keys alphabetically (default is True).
        """
        self.default_file = default_file
        self.json_handler = JsonFileHandler(indent=indent, sort_keys=sort_keys)

    def write(self, data: t.Any, destination: str = None, **kwargs):
        """
        Write data to a JSON file with pretty printing.
        
        :param data: The data to write.
        :param destination: File name to write to (overrides default).
        :param kwargs: Additional options like 'indent' for pretty printing.
        """
        file_name = destination or self.default_file
        if not file_name:
            raise ValueError("No destination file specified for JsonFileWriter.")
        
        # Ensure the destination directory exists
        Path(file_name).parent.mkdir(parents=True, exist_ok=True)
        
        # Delegate JSON writing to JsonFileHandler
        self.json_handler.write_to_file(data, file_name)
