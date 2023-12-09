from functools import reduce

A="""Time:      7  15   30
Distance:  9  40  200"""

A="""Time:        56     97     77     93
Distance:   499   2210   1097   1440"""

T, D = A.splitlines()

records = {}
for time, dist in zip(T.split()[1:], D.split()[1:]):
    records[int(time)] = int(dist)
   
print(records)

def calc(records):
    all_wins=[]
    for time, record in records.items():
        wins=0
        for speed in range(time+1):
            dist = (time - speed) * speed
            # print(f"race {time=}, charge time={speed}, {dist=}")
            if dist > record:
                wins+=1
        all_wins.append(wins)
   
    # print(all_wins)
    product=lambda x: reduce(lambda x, y: y*x, x)
    return product(all_wins)
   
print("answer 1",calc(records))

records = {} 
records[int("".join(T.split()[1:]))] = int("".join(D.split()[1:])) 
print("answer 2",calc(records))