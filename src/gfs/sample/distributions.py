from abc import ABC, abstractmethod

from gfs.sample.leaf import Leaf, LeafList, Side
from gfs.sample.tree import Tree


class Distribution(ABC):
    def __init__(self, domain_bit_depth: int) -> None:
        self.domain_bit_depth = domain_bit_depth

    @abstractmethod
    def leaves(self) -> LeafList:
        pass

    def tree(self) -> Tree:
        return Tree(self.leaves())


class Uniform(Distribution):
    def __init__(self, domain_bit_depth: int) -> None:
        super().__init__(domain_bit_depth)

    def leaves(self) -> LeafList:
        leaf = Leaf(
            multiplicity=0, sides=[Side(endpoint=0, bit_depth=self.domain_bit_depth)]
        )
        return LeafList([leaf])


class Linear(Distribution):
    def __init__(self, domain_bit_depth: int, reverse: bool = False) -> None:
        super().__init__(domain_bit_depth)
        self.reverse_int = 0 if reverse else 1

    def leaves(self) -> LeafList:
        leaf_list: list[Leaf] = list()
        for j in range(0, self.domain_bit_depth):
            for i in range(0, 2 ** (self.domain_bit_depth - j - 1)):
                endpoint = (2**j) * (2 * i + self.reverse_int)
                leaf_list.append(
                    Leaf(multiplicity=j, sides=[Side(endpoint=endpoint, bit_depth=j)])
                )

        return LeafList(leaf_list)
