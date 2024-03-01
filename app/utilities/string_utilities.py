import re


def remove_after_separator(value: str, separator: str):
    """
    Removes the substring after the first occurrence of a given separator in a string.
    """
    new_value = value.partition(separator)[0].strip()
    return new_value


def split_string(s: str):
    """
    Split a string by spaces and commas into a list of strings,
    removing multiple spaces.
    """
    list_string = s.replace(",", " ").strip()
    # remove multiple spaces
    list_string = re.sub(" +", " ", list_string)
    list_string = list_string.split(" ")
    return list_string
