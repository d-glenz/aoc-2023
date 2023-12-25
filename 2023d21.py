from dataclasses import dataclass, field
import math
from functools import cache
from typing import FrozenSet
import subprocess


def find(field, ch='O'):
    res = set()
    for y,line in enumerate(field.splitlines()):
        for x,el in enumerate(line):
            if el == ch:
                res.add((x,y))
    return res


A="""\
...........
.....###.#.
.###.##..#.
..#.#...#..
....#.#....
.##..S####.
.##..#...#.
.......##..
.##.#.####.
.##..##.##.
..........."""


steps = {
    1: find("""...........
.....###.#.
.###.##..#.
..#.#...#..
....#O#....
.##.O.####.
.##..#...#.
.......##..
.##.#.####.
.##..##.##.
..........."""),
    2: find("""...........
.....###.#.
.###.##..#.
..#.#O..#..
....#.#....
.##O.O####.
.##.O#...#.
.......##..
.##.#.####.
.##..##.##.
..........."""),
    3: find("""...........
.....###.#.
.###.##..#.
..#.#.O.#..
...O#O#....
.##.OS####.
.##O.#...#.
....O..##..
.##.#.####.
.##..##.##.
..........."""),
    6: find("""...........
.....###.#.
.###.##.O#.
.O#O#O.O#..
O.O.#.#.O..
.##O.O####.
.##.O#O..#.
.O.O.O.##..
.##.#.####.
.##O.##.##.
...........""")
}


def gen_positions(pos, width, height, unbounded: bool = False):
    x, y = pos
    if x > 0 or unbounded:
        yield x-1, y
    if x < width - 2 or unbounded:
        yield x+1, y
    if y > 0 or unbounded:
        yield x, y-1
    if y < height - 2 or unbounded:
        yield x, y+1


@cache
def rocks_in_field(rocks: FrozenSet[tuple[int, int]], pos: tuple[int, int], width: int, height: int) -> FrozenSet[tuple[int, int]]:
    x, y = pos
    relative_origin = math.floor(x / width) * width, math.floor(y / height) * height
    return frozenset((x-relative_origin[0], y-relative_origin[1]) for x, y in rocks)


@dataclass
class Field:
    rocks: frozenset[tuple[int, int]]
    starting: tuple[int, int]
    width: int
    height: int
    unbounded: bool = False

    def one_step(self, last_positions):
        res = set()
        for old in last_positions:
            for pos in gen_positions(old, self.width, self.height, unbounded=self.unbounded):
                if pos not in rocks_in_field(self.rocks, pos, self.width, self.height):
                    res.add(pos)
        return list(res)

    def simulate(self, num_steps, test_dict=None):
        last_positions = [self.starting]
        for step in range(num_steps):
            res = self.one_step(last_positions)
            if test_dict is not None and step+1 in test_dict:
                assert set(res) == test_dict[step+1], (
                    f"step {step+1}: missing: {test_dict[step+1] - set(res)}, "
                    f"too much: {set(res) - test_dict[step+1]}")
            last_positions = res

        return last_positions

    @classmethod
    def parse(cls, A, unbounded=False) -> "Field":
        rocks = set()
        starting = -1, -1
        width = 0
        height = 0
        for y, line in enumerate(A.splitlines()):
            for x, el in enumerate(line):
                match el:
                    case '#':
                        rocks.add((x, y))
                    case 'S':
                        starting = x, y
                width = x + 1
            height = y + 1
        return cls(frozenset(rocks), starting, width, height, unbounded=unbounded)


def print_field(last_positions, field, filename):
    all_rocks = set([rock for pos in last_positions for rock in rocks_in_field(field.rocks, pos, field.width, field.height)])
    B = ""
    for y in range(-22, 20):
        for x in range(-22, 33):
            # if (x,y) == field.starting:
            #     B+="S"
            if (x,y) in last_positions:
                B+="O"
            else:
                B+="." if (x,y) not in all_rocks else "#"
        B += "\n"

    with open(filename, 'w+') as f:
        f.write(B)

    p = subprocess.Popen(['less', filename])
    _, _ = p.communicate()


field = Field.parse(A)
res = field.simulate(6, test_dict=steps)
assert len(res) == 16

results = {
    6: 16,
    10: 50,
    50: 1594,
    100: 6536,
    500: 167004,
    1000: 668697,
    5000: 16733044
}
field = Field.parse(A, unbounded=True)
print(f'field: {field.width=}, {field.height=}, {field.starting=}')

last_positions = [field.starting]
for step in range(10):
    last_positions = field.one_step(last_positions)
    if step+1 in results:
        assert len(last_positions) == results[step+1], f'step {step+1} - expected: {results[step+1]}, actual: {len(last_positions)}'


with open('input21.txt') as f:
    A = f.read()

field = Field.parse(A)
res = field.simulate(64)
assert len(res) == 3748
print(f"Solution 1: {len(res)}")
