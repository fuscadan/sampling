from gfs.sample.leaf import Leaf, LeafList, Side


def constant(domain_bit_depth: int) -> LeafList:
    leaf = Leaf(multiplicity=0, sides=[Side(endpoint=0, bit_depth=domain_bit_depth)])
    return LeafList([leaf])


def linear(domain_bit_depth: int, reverse: bool = False) -> LeafList:
    reverse_int = 0 if reverse else 1
    leaf_list: list[Leaf] = list()
    for j in range(0, domain_bit_depth):
        for i in range(0, 2 ** (domain_bit_depth - j - 1)):
            endpoint = (2**j) * (2 * i + reverse_int)
            leaf_list.append(
                Leaf(multiplicity=j, sides=[Side(endpoint=endpoint, bit_depth=j)])
            )

    return LeafList(leaf_list)
