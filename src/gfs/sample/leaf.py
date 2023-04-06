from typing import NamedTuple, Self

MAX_COMBINE_ATTEMPTS = 100


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
            shift, label_block = label_block.pop_left(n_bits=side.bit_depth)
            coordinate_list.append(side.get_coordinate(shift))
        return tuple(coordinate_list)


class LeafList(list[Leaf]):
    def extend_domain(self, bit_depth: int, axis: int | None = None) -> None:
        if axis is None:
            axis = len(self)
        for leaf in self:
            leaf.sides.insert(axis, Side(endpoint=0, bit_depth=bit_depth))

    def restrict(self, value: int, axis: int) -> None:
        to_pop: list[int] = list()
        for i, leaf in enumerate(self):
            side = leaf.sides[axis]
            if value in range(side.endpoint, side.endpoint + (1 << side.bit_depth)):
                _ = leaf.sides.pop(axis)
            else:
                to_pop.append(i)

        to_pop.reverse()
        for i in to_pop:
            _ = self.pop(i)

    def drop_small(self, bit_depth: int) -> None:
        to_pop: list[int] = [
            i for i in range(len(self)) if self[i].bit_depth <= bit_depth
        ]
        to_pop.reverse()
        for i in to_pop:
            _ = self.pop(i)


def reduce_multiplicity(leaves: LeafList) -> LeafList:
    min_multiplicity: int = min([leaf.multiplicity for leaf in leaves])
    return LeafList(
        [Leaf(leaf.multiplicity - min_multiplicity, leaf.sides) for leaf in leaves]
    )


def combine_on_multiplicity(leaves: LeafList) -> LeafList:
    to_increase: list[int] = list()
    to_pop: list[int] = list()
    for i, leaf_1 in enumerate(leaves):
        if i in to_pop:
            continue
        for j, leaf_2 in enumerate(leaves[(i + 1) :]):
            if leaf_1 == leaf_2:
                to_increase.append(i)
                to_pop.append(i + 1 + j)
                break

    combined_leaves: LeafList = LeafList()
    for i, leaf in enumerate(leaves):
        if i in to_pop:
            continue
        if i in to_increase:
            combined_leaves.append(Leaf(leaf.multiplicity + 1, leaf.sides))
            continue
        combined_leaves.append(Leaf(leaf.multiplicity, leaf.sides))

    return combined_leaves
