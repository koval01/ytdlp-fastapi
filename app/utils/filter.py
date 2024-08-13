from typing import Any


class Filter:
    @staticmethod
    def filter_by_key_value(data: list[dict], key: str, values: list[Any]) -> list[dict]:
        """
        Filter a list of dictionaries based on a key-value pair.

        :param data: List of dictionaries to filter
        :param key: The key to check in each dictionary
        :param values: The values to match for the specified key
        :return: Filtered list of dictionaries
        """
        return [item for item in data if item.get(key) in values]
