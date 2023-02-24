from itertools import product

from gfs.sample.leaf import Leaf, LeafList, Side


def _line_segment_to_list_of_sides(endpoint: int, length: int) -> list[Side]:
    sides: list[Side] = list()
    if length <= 0:
        return sides
    for i in range(0, length.bit_length()):
        if (length >> i) % 2:
            sides.append(Side(endpoint, bit_depth=i))
            endpoint = endpoint + (1 << i)
    return sides


def _intersect_sides(s1: Side, s2: Side) -> list[Side]:
    s1_left = s1.endpoint
    s1_right = s1.endpoint + (1 << s1.bit_depth)
    s2_left = s2.endpoint
    s2_right = s2.endpoint + (1 << s2.bit_depth)

    s3_left = max([s1_left, s2_left])
    s3_right = min([s1_right, s2_right])
    length = s3_right - s3_left

    return _line_segment_to_list_of_sides(s3_left, length)


def _intersect_leaves(l1: Leaf, l2: Leaf) -> list[Leaf]:
    sides_by_axis: list[list[Side]] = list()
    for i in range(0, len(l1.sides)):
        intersection = _intersect_sides(l1.sides[i], l2.sides[i])
        if len(intersection) == 0:
            return list()
        sides_by_axis.append(intersection)

    leaves: list[Leaf] = list()
    for sides in product(*sides_by_axis):
        mult = l1.multiplicity + l2.multiplicity
        leaves.append(Leaf(multiplicity=mult, sides=list(sides)))

    return leaves


def multiply(leaves_left: LeafList, leaves_right: LeafList) -> LeafList:
    leaf_list: list[Leaf] = list()
    for l1, l2 in product(leaves_left, leaves_right):
        leaf_list.extend(_intersect_leaves(l1, l2))

    return LeafList(leaf_list)
