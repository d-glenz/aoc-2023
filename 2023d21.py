def find(field, ch='O'):
    res = set()
    for y,line in enumerate(field.splitlines()):
        for x,el in enumerate(line):
            if el == ch:
                res.add((x,y))
    return res


A="""...........
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


def gen_positions(pos, width, height):
    x, y = pos
    if x > 0:
        yield x-1, y
    if x < width - 2:
        yield x+1, y
    if y > 0:
        yield x, y-1
    if y < height - 2:
        yield x, y+1

def one_step(last_positions, rocks):
    res = set()
    for old in last_positions:
        for pos in gen_positions(old, width, height):
            if pos not in rocks:
                res.add(pos)
    return list(res)

def simulate(num_steps, rocks, test_dict=None):
    last_positions = [starting]
    for step in range(num_steps):
        res = one_step(last_positions, rocks)
        if test_dict is not None and step+1 in test_dict:
            assert set(res) == test_dict[step+1], (
                f"step {step+1}: missing: {test_dict[step+1] - set(res)}, "
                f"too much: {set(res) - test_dict[step+1]}")
        last_positions = res


    return last_positions


def parse(A):
    rocks = []
    starting = None, None
    width = 0
    height = 0
    for y, line in enumerate(A.splitlines()):
        for x, el in enumerate(line):
            match el:
                case '#':
                    rocks.append((x, y))
                case 'S':
                    starting = x, y
            width = x + 1
        height = y + 1
    return rocks, starting, width, height


with open('input21.txt') as f:
    A = f.read()

rocks, starting, width, height = parse(A)
res = simulate(64, rocks)  # , test_dict=steps)
print(f"Solution 1: {len(res)}")
