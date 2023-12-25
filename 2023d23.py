from dataclasses import dataclass, field
from typing import Optional, Union
import re

A = """\
#.#####################
#.......#########...###
#######.#########.#.###
###.....#.>.>.###.#.###
###v#####.#v#.###.#.###
###.>...#.#.#.....#...#
###v###.#.#.#########.#
###...#.#.#.......#...#
#####.#.#.#######.#.###
#.....#.#.#.......#...#
#.#####.#.#.#########v#
#.#...#...#...###...>.#
#.#.#v#######v###.###v#
#...#.>.#...>.>.#.###.#
#####v#.#.###v#.#.###.#
#.....#...#...#.#.#...#
#.#########.###.#.#.###
#...###...#...#...#.###
###.###.#.###v#####v###
#...#...#.#.>.>.#.>.###
#.###.###.#.###.#.#v###
#.....###...###...#...#
#####################.#"""

@dataclass
class Field:
    data: list[list[str]]
    current_leafs: list["Node"] = field(default_factory=list)

    def __post_init__(self):
        self.by_coord = {(x,y):el for y, row in enumerate(self.data) for x, el in enumerate(row)}
        self.height = len(self.data)
        self.width = len(self.data[0])

    def __getitem__(self, key: tuple[int, int]):
        assert isinstance(key, tuple)
        return self.by_coord[key]

    def neighbors(self, key, filter=None):
        x, y = key
        res = {}
        if self[key] in '<>v^':
            match self[key]:
                case '<':
                    res = {(x-1, y): self.by_coord[(x-1, y)]}
                case '>':
                    res = {(x+1, y): self.by_coord[(x+1, y)]}
                case '^':
                    res = {(x, y-1): self.by_coord[(x, y-1)]}
                case _:
                    res = {(x, y+1): self.by_coord[(x, y+1)]}
        else:
            if x > 0:  # left
                if self.by_coord[(x-1, y)] != '>':
                    res[(x-1, y)] = self.by_coord[(x-1, y)]
            if y > 0:  # top
                if self.by_coord[(x, y-1)] != 'v':
                    res[(x, y-1)] = self.by_coord[(x, y-1)]
            if x < self.width - 1:  # right
                if self.by_coord[(x+1, y)]  != '<':
                    res[(x+1, y)] = self.by_coord[(x+1, y)]
            if y < self.height - 1:  # bottom
                if self.by_coord[(x, y+1)] != '^':
                    res[(x, y+1)] = self.by_coord[(x, y+1)]
        if filter is not None:
            return {k:v for k,v in res.items() if v in filter}
        return res

    def __repr__(self):
        return "\n".join(["".join([
            el if (x,y) not in [l.coord for l in self.current_leafs]
            else 'O' for x, el in enumerate(row)
        ]) for y, row in enumerate(self.data)])

@dataclass
class Range1D:
    start: int
    end: int
    other: int
    across_x: bool

    def is_adjacent(self, other):
        x, y = other
        if self.across_x:
            if y != self.other:
                return False
            return x == self.start - 1 or x == self.end + 1
        if x != self.other:
            return False
        return y == self.start - 1 or y == self.end + 1

    def amend(self, other):
        t = other[0] if self.across_x else other[1]
        self.start = min(t, self.start)
        self.end = max(t, self.end)

    def __contains__(self, other):
        if self.across_x:
            if other[1] != self.other:
                return False
            return self.start <= other[0] <= self.end
        if other[0] != self.other:
            return False
        return self.start <= other[1] <= self.end


@dataclass
class Parents:
    individual: set[tuple[int, int]] = field(default_factory=set)
    ranges: set[Range1D] = field(default_factory=set)

    def __contains__(self, other):
        assert isinstance(other, tuple)
        if other in self.individual:
            return True
        return any(other in r for r in self.ranges)

    def __or__(self, other):
        new = Parents(self.individual, self.ranges)
        new.add(other)
        return new

    def add(self, other):
        for _range in self.ranges:
            if _range.is_adjacent(other):
                _range.amend(other)
                break
        else:
            for x, y in self.individual:
                if x == other.x and y in (other.y - 1, other.y + 1):
                    r = Range1D(start=min(y, other.y), end=max(y, other.y), other=x, across_x=False)
                    self.individual.remove((x,y))
                    self.ranges.add(r)
                    break
                if y == other.y and x in (other.x - 1, other.x + 1):
                    r = Range1D(start=min(x, other.x), end=max(x, other.x), other=y, across_x=True)
                    self.individual.remove((x,y))
                    self.ranges.add(r)
                    break

@dataclass
class Node:
    coord: tuple[int, int]
    length: int
    parent: Optional["Node"] = None
    # parents: Parents = field(default_factory=Parents)
    parents: set[tuple[int, int]] = field(default_factory=set)

    def __repr__(self):
        return f'Node{{coord={self.coord}, length={self.length}}}'


def solve(A):
    f = Field([list(row) for row in A.splitlines()])
    S = (1, 0)
    E = (f.width-2, f.height-1)

    root = Node(S, 0)
    path_lengths = []
    f.current_leafs = [root]
    while f.current_leafs:
        new_leafs = []
        for node in f.current_leafs:
            potential = {coord:v for coord,v in f.neighbors(node.coord, filter='<>v^.').items() if coord not in node.parents}
            match len(potential):
                case 1:
                    node.parents.add(node.coord)
                    node.coord = list(potential.keys())[0]
                    node.length += 1
                    if node.coord == E:
                        path_lengths.append(node.length)
                    else:
                        new_leafs.append(node)
                case 0:
                    ...
                case _:
                    for coord, _ in potential.items():
                        child = Node(coord, node.length+1, node, node.parents | {node.coord})
                        if coord == E:
                            path_lengths.append(child.length)
                        else:
                            new_leafs.append(child)
        f.current_leafs = new_leafs

    return max(path_lengths)


with open('input23.txt') as f:
    A = f.read()

print(f"Solution 1: {solve(A)}")
#print(f"Solution 2: {solve(re.sub('[<>^v]', '.', A))}")
