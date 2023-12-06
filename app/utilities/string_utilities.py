
def remove_after_separator(value: str, separator: str):
    """
    Removes the substring after the first occurrence of a given separator in a string.
    """
    new_value = value.partition(separator)[0].strip()
    return new_value
