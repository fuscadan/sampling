from random import randrange

from gfs.sample.leaf import Label, Leaf, LeafList

SAMPLING_MAX_RETRIES = 100000


class Tree:
    def __init__(self, leaves: LeafList) -> None:
        self._n_blocks: int = self._compute_n_blocks(leaves)
        self._depth: int = self._compute_required_depth()
        self._leaves_labeled: dict[Label, Leaf] = self._label_leaves(leaves)

    @property
    def n_blocks(self) -> int:
        return self._n_blocks

    @property
    def depth(self) -> int:
        return self._depth

    @property
    def leaves_labeled(self) -> dict[Label, Leaf]:
        return self._leaves_labeled

    def _compute_n_blocks(self, leaves: LeafList) -> int:
        return sum([leaf.n_blocks for leaf in leaves])

    def _compute_required_depth(self) -> int:
        return self.n_blocks.bit_length()

    def _label_leaves(self, leaves: LeafList) -> dict[Label, Leaf]:
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

    def sample_once(self) -> tuple[int, ...]:
        for n in range(0, SAMPLING_MAX_RETRIES):
            label: Label = Label(randrange(1 << self.depth), self.depth)

            for i in range(0, self.depth):
                label_leaf, label_block = label.pop_left(n_bits=i + 1)
                leaf = self.leaves_labeled.get(label_leaf)
                if leaf is not None:
                    return leaf.get_block_coordinates(label_block)

        raise Exception("Maximum sampling retries exceeded.")

    def sample(self, n_samples: int) -> list[tuple[int, ...]]:
        return [self.sample_once() for i in range(0, n_samples)]
