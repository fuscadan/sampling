from random import randrange
from typing import NamedTuple, Self

SAMPLING_MAX_RETRIES = 100000


class Label(NamedTuple):
    value: int

    def pop_bits(self, n_bits: int) -> tuple[Self, Self]:
        left = self.value >> n_bits
        right = self.value - (left << n_bits)
        return Label(left), Label(right)


class Side(NamedTuple):
    endpoint: int
    bit_depth: int

    def get_coordinate(self, shift: Label) -> int:
        return self.endpoint + shift.value


class Leaf(NamedTuple):
    multiplicity: int
    sides: list[Side]

    @property
    def bit_depth(self) -> int:
        return sum([side.bit_depth for side in self.sides]) + self.multiplicity

    @property
    def n_blocks(self) -> int:
        return 1 << self.bit_depth

    def get_block_coordinates(self, label_block: Label) -> tuple[int, ...]:
        coordinate_list: list[int] = list()
        for side in self.sides:
            label_block, shift = label_block.pop_bits(n_bits=side.bit_depth)
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
        leaves_by_bit_depth: dict[int, list[Leaf]] = dict()
        for leaf in leaves:
            if isinstance(leaves_by_bit_depth.get(leaf.bit_depth), list):
                leaves_by_bit_depth[leaf.bit_depth].append(leaf)
            else:
                leaves_by_bit_depth[leaf.bit_depth] = [leaf]

        leaves_labeled: dict[Label, Leaf] = dict()
        value: int = 0
        bit_depths_present = list(leaves_by_bit_depth.keys())
        bit_depths_present.sort(reverse=True)
        for i in range(len(bit_depths_present) - 1):
            for leaf in leaves_by_bit_depth[bit_depths_present[i]]:
                leaves_labeled[Label(value)] = leaf
                value += 1
            value = value << bit_depths_present[i] - bit_depths_present[i + 1]
        for leaf in leaves_by_bit_depth[bit_depths_present[-1]]:
            leaves_labeled[Label(value)] = leaf
            value += 1

        return leaves_labeled

    def _sample_once(self) -> tuple[int, ...]:
        for n in range(0, SAMPLING_MAX_RETRIES):
            label: Label = Label(randrange(1 << self.depth))

            for i in range(self.depth, 0, -1):
                label_leaf, label_block = label.pop_bits(n_bits=i - 1)
                leaf = self.leaves_labeled.get(label_leaf)
                if leaf is not None:
                    return leaf.get_block_coordinates(label_block)

        raise Exception("Maximum sampling retries exceeded.")

    def sample(self, n_samples: int) -> list[tuple[int, ...]]:
        return [self._sample_once() for i in range(0, n_samples)]
