from dataclasses import dataclass
import tqdm
import copy

A = """1,0,1~1,2,1
0,0,2~2,0,2
0,2,3~2,2,3
0,0,4~0,2,4
2,0,5~2,2,5
0,1,6~2,1,6
1,1,8~1,1,9"""

@dataclass
class Point:
    x: int
    y: int
    z: int

    def __repr__(self):
        return f"[{self.x} {self.y} {self.z}]"

@dataclass
class Brick:
    start: Point
    end: Point

    @property
    def volume(self):
        if self.start == self.end:
            return 1

        return (
            (abs(self.start.x - self.end.x) + 1) *
            (abs(self.start.y - self.end.y) + 1) *
            (abs(self.start.z - self.end.z) + 1)
        )

    @property
    def on_ground(self):
        return any(p.z == 1 for p in (self.start, self.end))

    def blocked_in_z(self, other):
        if all([p.z > q.z for p in (other.start, other.end) for q in (self.start, self.end)]):
            return False

        if any(other.start.x <= x <= other.end.x for x in range(self.start.x, self.end.x+1)):
            return any(other.start.y <= y <= other.end.y for y in range(self.start.y, self.end.y+1))
        return False

    def supports(self, other):
        return other.blocked_in_z(self) and min([other.start.z, other.end.z]) - max([self.start.z, self.end.z]) == 1

    def move_z(self, z_low):
        diff = min(self.start.z, self.end.z) - z_low
        self.start.z -= diff
        self.end.z -= diff


def parse_bricks(A, lt26 = True):
    abc = [chr(ord('A')+i) for i in range(26)]
    res = {}
    all_names = [a+b+c for a in abc for b in abc for c in abc] if not lt26 else abc
    for name, line in zip(all_names, A.splitlines()):
        start, end = line.split('~')
        brick = Brick(Point(*map(int, start.split(','))), Point(*map(int, end.split(','))))
        res[name] = brick
    return res


ex1 = """2,2,2~2,2,2"""
ex2 = """\
0,0,10~1,0,10
0,0,10~0,1,10"""
ex3 = """0,0,1~0,0,10"""
ex4="""5,5,1~5,6,1"""
ex5="""0,2,1~0,2,5"""
ex6="""3,3,2~3,3,3"""

assert parse_bricks(ex1)['A'].volume == 1
assert all(b.volume == 2 for _, b in parse_bricks(ex2).items())
assert parse_bricks(ex3)['A'].volume == 10
assert parse_bricks(ex4)['A'].on_ground
assert parse_bricks(ex5)['A'].on_ground
assert not parse_bricks(ex6)['A'].on_ground

class BrickStack:
    def __init__(self, bricks: dict[str, Brick]):
        self.data = bricks

    def __getitem__(self, k):
        return self.data[k]

    def unsupported(self, key, excluded=None):
        if self.data[key].on_ground:
            return False

        if excluded is None:
            excluded = set([key])
        else:
            excluded.update([key])

        bricks = [o for k, o in self.data.items() if k not in excluded and self[key].blocked_in_z(o)]

        # if key is not blocked_in_z by any other brick
        if not bricks:
            return True
        
        new_z = max([max([o.start.z, o.end.z]) for o in bricks]) + 1
        lowest_in_z = min(self[key].start.z, self[key].end.z)
        assert lowest_in_z - new_z >= 0, f"[{key}] {lowest_in_z=} < {new_z=}"
        diff = lowest_in_z - new_z

        return diff > 0

    def chain_reaction(self, key):
        U = set([key])
        while True:
            t = []
            for key2 in self.data.keys():
                if self.unsupported(key2, copy.copy(U)) and key2 not in U:
                    t.append(key2)
            if not t:
                break
            U.update(t)
        return U - set([key])

    def move_downward(self):
        obstacles = []
        for _, brick in sorted(self.data.items(),
                               key=lambda b: min(b[1].start.z, b[1].end.z)):
            if not brick.on_ground:
                if obstacles and any([o for o in obstacles if brick.blocked_in_z(o)]):
                    new_z = max([max([o.start.z, o.end.z]) for o in obstacles if brick.blocked_in_z(o)]) + 1
                else:
                    new_z = 1
                brick.move_z(new_z)
            obstacles.append(brick)

    def can_be_disintegrated(self, key):
        supports = [brick for _, brick in self.data.items() if self.data[key].supports(brick)]
        if not supports:
            return True
        return all([len([b for b in self.data.values() if b.supports(brick)]) > 1 for brick in supports])

    def __repr__(self):
        max_x = max([p.x for brick in self.data.values() for p in (brick.start, brick.end)])
        max_z = max([p.z for brick in self.data.values() for p in (brick.start, brick.end)])
        S = "".join([str(x) for x in range(max_x+1)]) + "\n"
        for z in range(max_z, -1, -1):
            row = ""
            for x in range(max_x+1):
                selected = [k for k,b in self.data.items() if b.start.x <= x <= b.end.x and b.start.z <= z <= b.end.z]
                row += "." if not selected else ("?" if len(selected) > 1 else selected[0])
            S += row + f" {z} \n"

        return S

    def __format__(self, fstr):
        direction = fstr[0]
        padding = int(fstr[1]) if len(fstr) > 1 else 1
        max_x = max([p.x for brick in self.data.values() for p in (brick.start, brick.end)])
        max_y = max([p.y for brick in self.data.values() for p in (brick.start, brick.end)])
        max_z = max([p.z for brick in self.data.values() for p in (brick.start, brick.end)])
        S = (
            ("".join([f'{y:{padding}}' for y in range(max_y+1)]) + "\n") if direction == "y" else
            ("".join([f'{x:{padding}}' for x in range(max_x+1)]) + "\n")
        )
        for z in range(max_z, -1, -1):
            row = ""
            for t in range((max_y+1) if direction == "y" else (max_x+1)):
                if direction == "x":
                    selected = [k for k,b in self.data.items() if b.start.x <= t <= b.end.x and b.start.z <= z <= b.end.z]
                else:
                    selected = [k for k,b in self.data.items() if b.start.y <= t <= b.end.y and b.start.z <= z <= b.end.z]
                row += ("."*padding) if not selected else (("?"*padding) if len(selected) > 1 else selected[0])
            S += row + f" {z} \n"

        return S

def part1(stack):
    R = 0
    for name, _ in stack.data.items():
        if stack.can_be_disintegrated(name):
            #print(f'Brick {name} can be disintegrated')
            R += 1
        # else:
        #     print(f'Brick {name} cannot be disintegrated')

    # print(f'{stack:y3}')
    print(f"Solution 1: {R}")


stack = BrickStack(parse_bricks(A))
assert stack['B'].blocked_in_z(stack['A'])
assert stack['C'].blocked_in_z(stack['A'])
assert stack['D'].blocked_in_z(stack['B'])
assert stack['E'].blocked_in_z(stack['B'])
assert stack['D'].blocked_in_z(stack['C'])
assert stack['E'].blocked_in_z(stack['C'])
assert stack['F'].blocked_in_z(stack['D'])
assert stack['F'].blocked_in_z(stack['E'])
assert stack['G'].blocked_in_z(stack['F'])
assert not any(b.blocked_in_z(stack['G']) for k, b in stack.data.items() if k != 'G')

assert stack['A'].supports(stack['B'])
assert stack['F'].blocked_in_z(stack['A'])
assert not stack['A'].supports(stack['F'])



stack.move_downward()
assert sum([1 for name, _ in stack.data.items() if stack.unsupported(name)]) == 0
assert stack['C'].start.z == 2
assert stack['C'].end.z == 2
assert stack['F'].start.z == 4
assert stack['F'].end.z == 4


print(f'{stack:y}')
assert stack.unsupported('B', {'A'}), 'if A is gone, B should be unsupported'
assert stack.unsupported('C', {'A'}), 'if A is gone, C should be unsupported'
assert stack.unsupported('D', {'A', 'B', 'C'}), 'if A, B, and C are gone, D should be unsupported'
assert stack.unsupported('E', {'A', 'B', 'C'}), 'if A, B, and C are gone, E should be unsupported' 
assert stack.unsupported('F', {'A', 'B', 'C', 'D', 'E'}), 'if A, B, C, D, and E are gone, F should be unsupported'  
assert stack.unsupported('G', {'A', 'B', 'C', 'D', 'E', 'F'}), 'if A, B, C, D, and E are gone, G should be unsupported'  
assert set(stack.chain_reaction('B')) == set()

assert set(stack.chain_reaction('A')) == set(['B', 'C', 'D', 'E', 'F', 'G'])
assert sum([len(stack.chain_reaction(key)) for key in stack.data.keys()])  == 7

# print()
# print(f'{stack:x}')
# 
with open('input22.txt') as f:
    A = f.read()

stack = BrickStack(parse_bricks(A, lt26=False))
stack.move_downward()

part1(stack)

S = 0
for key in tqdm.tqdm(stack.data.keys()):
    S+=len(stack.chain_reaction(key))

print(f"Solution 2: {S}")
