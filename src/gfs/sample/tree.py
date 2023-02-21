from random import randrange
from typing import NamedTuple, Self

SAMPLING_MAX_RETRIES = 100000


class Label(NamedTuple):
    value: int
    bit_depth: int

    @property
    def binary(self) -> str:
        unpadded_string = bin(self.value).split("b")[1]
        leading_zeros = "0" * (self.bit_depth - len(unpadded_string))
        return leading_zeros + unpadded_string

    def pop_right(self, n_bits: int) -> tuple[Self, Self]:
        left = self.value >> n_bits
        right = self.value - (left << n_bits)
        return Label(left, self.bit_depth - n_bits), Label(right, n_bits)

    def pop_left(self, n_bits: int) -> tuple[Self, Self]:
        left = self.value >> self.bit_depth - n_bits
        right = self.value - (left << self.bit_depth - n_bits)
        return Label(left, n_bits), Label(right, self.bit_depth - n_bits)


class Side(NamedTuple):
    endpoint: int
    bit_depth: int

    def get_coordinate(self, shift: Label) -> int:
        return self.endpoint + shift.value


class Leaf:
    def __init__(self, multiplicity: int, sides: list[Side]) -> None:
        self.multiplicity = multiplicity
        self.sides = sides

    def __repr__(self) -> str:
        return f"Leaf(multiplicity={self.multiplicity}, sides={self.sides})"

    @property
    def bit_depth(self) -> int:
        return sum([side.bit_depth for side in self.sides]) + self.multiplicity

    @property
    def n_blocks(self) -> int:
        return 1 << self.bit_depth

    def get_block_coordinates(self, label_block: Label) -> tuple[int, ...]:
        coordinate_list: list[int] = list()
        for side in self.sides:
            shift, label_block = label_block.pop_left(n_bits=side.bit_depth)
            coordinate_list.append(side.get_coordinate(shift))
        return tuple(coordinate_list)


class Tree:
    def __init__(self, leaves: list[Leaf]) -> None:
        self._depth: int = self._compute_required_depth(leaves)
        self._leaves_labeled: dict[Label, Leaf] = self._label_leaves(leaves)

    @property
    def depth(self) -> int:
        return self._depth

    @property
    def leaves_labeled(self) -> dict[Label, Leaf]:
        return self._leaves_labeled

    def _compute_required_depth(self, leaves: list[Leaf]) -> int:
        n_total_blocks = sum([leaf.n_blocks for leaf in leaves])
        return n_total_blocks.bit_length()

    def _label_leaves(self, leaves: list[Leaf]) -> dict[Label, Leaf]:
        leaves.sort(key=lambda leaf: leaf.bit_depth, reverse=True)

        leaves_labeled: dict[Label, Leaf] = dict()
        last_bit_depth_leaf: int = self.depth
        last_label: int = -1
        for leaf in leaves:
            bit_depth_leaf = leaf.bit_depth
            bit_depth_label = self.depth - bit_depth_leaf
            label = (last_label + 1) << (last_bit_depth_leaf - bit_depth_leaf)
            leaves_labeled[Label(label, bit_depth_label)] = leaf
            last_bit_depth_leaf = bit_depth_leaf
            last_label = label

        return leaves_labeled

    def _sample_once(self) -> tuple[int, ...]:
        for n in range(0, SAMPLING_MAX_RETRIES):
            label: Label = Label(randrange(1 << self.depth), self.depth)

            for i in range(0, self.depth):
                label_leaf, label_block = label.pop_left(n_bits=i + 1)
                leaf = self.leaves_labeled.get(label_leaf)
                if leaf is not None:
                    return leaf.get_block_coordinates(label_block)

        raise Exception("Maximum sampling retries exceeded.")

    def sample(self, n_samples: int) -> list[tuple[int, ...]]:
        return [self._sample_once() for i in range(0, n_samples)]

    def histogram(self, n_samples: int) -> dict[tuple[int, ...], int]:
        histogram: dict[tuple[int, ...], int] = dict()
        for i in range(0, n_samples):
            sample = self._sample_once()
            if isinstance(histogram.get(sample), int):
                histogram[sample] += 1
            else:
                histogram[sample] = 1

        return histogram
