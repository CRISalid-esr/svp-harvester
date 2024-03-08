from attr import dataclass


@dataclass
class HashKey:
    """
    HashKey dataclass to represent what field are hashed for a reference

    :value: The value to hash in the reference
    :sorted: If the order needs to be sorted before hashing
    """

    value: str
    sorted: bool = True
