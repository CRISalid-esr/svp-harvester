import re
import unicodedata


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


def normalize_string(s: str):
    """
    Normalize a string by replacing spaces by underscores and accents by their non-accented
    version whith unicodedata.normalize, and lowercasing the string.
    """
    s = s or ""
    s = s.replace(" ", "_")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("utf-8")
    s = s.lower()
    return s
