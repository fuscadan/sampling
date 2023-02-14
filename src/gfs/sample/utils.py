from os import urandom


def randint(n_bits) -> int:
    """
    slower but possibly better random number generation compared to random.randrange
    """
    n_bytes = (n_bits // 9) + 1
    return int.from_bytes(urandom(n_bytes)) >> 3
