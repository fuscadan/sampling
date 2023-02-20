from abc import ABC, abstractmethod

from gfs.sample.tree import Leaf, Side, Tree


class Distribution(ABC):
    @abstractmethod
    def leaves(self) -> list[Leaf]:
        pass

    def tree(self) -> Tree:
        return Tree(self.leaves())


class Uniform(Distribution):
    def __init__(self, bit_depth_domain: int) -> None:
        super().__init__()
        self.bit_depth_domain = bit_depth_domain

    def leaves(self) -> list[Leaf]:
        leaf = Leaf(
            multiplicity=0, sides=[Side(endpoint=0, bit_depth=self.bit_depth_domain)]
        )
        return [leaf]


class Linear(Distribution):
    def __init__(self, bit_depth_domain: int, reverse: bool = False) -> None:
        super().__init__()
        self.bit_depth_domain = bit_depth_domain
        self.reverse_int = 0 if reverse else 1

    def leaves(self) -> list[Leaf]:
        leaves: list[Leaf] = list()
        for j in range(0, self.bit_depth_domain):
            for i in range(0, 2 ** (self.bit_depth_domain - j - 1)):
                endpoint = (2**j) * (2 * i + self.reverse_int)
                leaves.append(
                    Leaf(multiplicity=j, sides=[Side(endpoint=endpoint, bit_depth=j)])
                )

        return leaves
