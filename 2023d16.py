A=r""".|...\....
|.-.\.....
.....|-...
........|.
..........
.........\
..../.\\..
.-.-/..|..
.|....-|.\
..//.|...."""

class Field:
    def __init__(self, data):
        self.data=data
        self.lasers=[Laser(data)]
        
    def update(self):
        while len(self.lasers)>0:
            for l in self.lasers:
                l.update()
            yield " "
        
class Laser:
    def __init__(self, data):
        self.b=[list(r) for r in data.splitlines()]
        self.pos=0,0
        self.dir=1,0
        self.visited=set([self.pos])
        
    def update(self):
        self.pos=(self.pos[0]+self.dir[0],
                  self.pos[1]+self.dir[1])
        if self.pos[0]<0 or self.pos[1]<0 or self.pos[1]>=len(self.data) or self.pos[1]>=len(self.b[0]):
            raise StopIteration
        self.visited.add(self.pos)
        yield self.b[self.pos[1]][self.pos[0]]


f=Field(A)
for ch in f.update():
    print(ch, f)
    break