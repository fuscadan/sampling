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

    def reduce_multiplicity(self) -> None:
        min_multiplicity: int = min([leaf.multiplicity for leaf in self])
        for leaf in self:
            leaf.multiplicity -= min_multiplicity

    @staticmethod
    def _can_combine_on_side(leaf_1: Leaf, leaf_2: Leaf, axis: int) -> bool:
        if leaf_1.bit_depth != leaf_2.bit_depth:
            return False

        l1_l_endpoint = leaf_1.sides[axis].endpoint
        l1_r_endpoint = l1_l_endpoint + (1 << leaf_1.sides[axis].bit_depth)
        l2_l_endpoint = leaf_2.sides[axis].endpoint
        l2_r_endpoint = l2_l_endpoint + (1 << leaf_2.sides[axis].bit_depth)

        if (l1_l_endpoint != l2_r_endpoint) and (l1_r_endpoint != l2_l_endpoint):
            return False

        for i in [j for j in range(len(leaf_1.sides)) if j != axis]:
            if leaf_1.sides[i] != leaf_2.sides[i]:
                return False

        return True

    @staticmethod
    def _combine_pair_on_side(leaf_1: Leaf, leaf_2: Leaf, axis: int) -> None:
        l1_l_endpoint = leaf_1.sides[axis].endpoint
        l2_l_endpoint = leaf_2.sides[axis].endpoint
        l2_r_endpoint = l2_l_endpoint + (1 << leaf_2.sides[axis].bit_depth)

        if l1_l_endpoint == l2_r_endpoint:
            endpoint = l2_l_endpoint
        else:
            endpoint = l1_l_endpoint

        bit_depth = leaf_1.sides[axis].bit_depth + 1
        leaf_1.sides[axis] = Side(endpoint=endpoint, bit_depth=bit_depth)

    def combine_on_side(self, axis: int) -> None:
        to_pop: list[int] = list()
        for i, leaf_1 in enumerate(self):
            if i in to_pop:
                continue
            for j, leaf_2 in enumerate(self[(i + 1) :]):
                if not self._can_combine_on_side(
                    leaf_1=leaf_1, leaf_2=leaf_2, axis=axis
                ):
                    continue
                self._combine_pair_on_side(leaf_1=leaf_1, leaf_2=leaf_2, axis=axis)
                to_pop.append(i + 1 + j)
                break

        to_pop.sort(reverse=True)
        for i in to_pop:
            _ = self.pop(i)

    @staticmethod
    def _can_combine_on_multiplicity(leaf_1: Leaf, leaf_2: Leaf) -> bool:
        if leaf_1.bit_depth != leaf_2.bit_depth:
            return False

        for i in range(len(leaf_1.sides)):
            if leaf_1.sides[i] != leaf_2.sides[i]:
                return False

        return True

    def combine_on_multiplicity(self) -> None:
        to_pop: list[int] = list()
        for i, leaf_1 in enumerate(self):
            if i in to_pop:
                continue
            for j, leaf_2 in enumerate(self[(i + 1) :]):
                if not self._can_combine_on_multiplicity(leaf_1=leaf_1, leaf_2=leaf_2):
                    continue
                leaf_1.multiplicity += 1
                to_pop.append(i + 1 + j)
                break

        to_pop.sort(reverse=True)
        for i in to_pop:
            _ = self.pop(i)

    def combine(self) -> None:
        if len(self) == 0:
            return None

        for i in range(MAX_COMBINE_ATTEMPTS):
            length_leaves_epic = len(self)
            for j in range(MAX_COMBINE_ATTEMPTS):
                length_leaves: int = len(self)
                self.combine_on_multiplicity()
                if len(self) == length_leaves:
                    break

            for axis in range(len(self[0].sides)):
                for j in range(MAX_COMBINE_ATTEMPTS):
                    length_leaves: int = len(self)
                    self.combine_on_side(axis)
                    if len(self) == length_leaves:
                        break

            if len(self) == length_leaves_epic:
                break
