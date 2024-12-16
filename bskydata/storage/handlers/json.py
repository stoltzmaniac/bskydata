import json
import typing as t


class JsonFileHandler:
    def __init__(self, indent: int = 4, sort_keys: bool = True):
        """
        :param indent: Number of spaces to use for JSON indentation (default is 4).
        :param sort_keys: Whether to sort JSON keys alphabetically (default is True).
        """
        self.indent = indent
        self.sort_keys = sort_keys

    def write_to_file(self, data: t.Any, file_path: str):
        """
        Write JSON data to a specified file.

        :param data: The data to write.
        :param file_path: The file path to write to.
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=self.indent,
                sort_keys=self.sort_keys,
                separators=(',', ': ')  # Add spaces after commas and colons
            )

    def write_to_temp_file(self, data: t.Any) -> str:
        """
        Write JSON data to a temporary file.

        :param data: The data to write.
        :return: Path to the temporary file.
        """
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as temp_file:
            json.dump(
                data,
                temp_file,
                indent=self.indent,
                sort_keys=self.sort_keys,
                separators=(',', ': ')  # Add spaces after commas and colons
            )
            return temp_file.name
