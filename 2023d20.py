A = """broadcaster -> a, b, c
%a -> b
%b -> c
%c -> inv
&inv -> a"""

A = """broadcaster -> a
%a -> inv, con
&inv -> b
%b -> con
&con -> output"""

A = """%qx -> gz
%tr -> rm
%qr -> kx, jm
%gj -> tx, rj
%lc -> hr
&kx -> zs, br, jd, bj, vg
&kd -> rg
%rm -> pf, ml
%tg -> tq, cp
%cp -> tp, tq
%sx -> qc, pf
&zf -> rg
%jz -> kx, pt
%dt -> tg, tq
%xv -> rj
%vz -> rj, xv
%vn -> vv, tq
%hl -> xt
%qc -> pf
%br -> jz
broadcaster -> sr, cg, dt, zs
%sk -> kx, qr
%xq -> dj
&vg -> rg
%zd -> pf, lc
%hr -> pm
%cg -> qx, rj
%tx -> vz, rj
%qf -> sb
&rj -> gs, sb, qx, qf, gz, hl, cg
%rb -> lz
%ml -> pf, xq
%bj -> jd
&gs -> rg
%sr -> pf, zd
%sb -> gj
&tq -> tp, rb, dt, kd, zt
%tp -> dm
%vv -> tq
%pm -> tr
%dj -> pf, sx
%lz -> vn, tq
%jd -> lx
%qn -> tq, rb
%zs -> kx, bj
&rg -> rx
%pt -> cb, kx
%xt -> ns, rj
%gz -> hl
%zt -> qn
%jm -> kx
%vp -> br, kx
&pf -> tr, hr, zf, sr, xq, pm, lc
%gp -> tq, zt
%dm -> tq, gp
%lx -> kx, vp
%ns -> qf, rj
%cb -> sk, kx"""

from dataclasses import dataclass, field
from typing import Optional
import queue
import tqdm
from math import lcm


RX_PRESSED = -1


@dataclass
class Broadcaster:
    name: str
    output: list[str]
    hq: Optional["DesertMachineHQ"] = None

    def pulse(self, name: str, high: bool):
        assert self.hq is not None
        self.hq.enqueue_pulses([Pulse(self.name, out, high) for out in self.output])


@dataclass
class FlipFlop:
    name: str
    output: list[str]
    hq: Optional["DesertMachineHQ"] = None
    on: bool = False

    def pulse(self, name: str, high: bool):
        # print(f'{name} -{"high" if high else "low"}-> {self.name}')
        if high:
            return

        self.on = not self.on
        assert self.hq is not None
        self.hq.enqueue_pulses([Pulse(self.name, out, self.on) for out in self.output])


@dataclass
class Conjunction:
    name: str
    output: list[str]
    hq: Optional["DesertMachineHQ"] = None
    inputs: list[str] = field(default_factory=list)
    states: dict[str, bool] = field(default_factory=dict)
    print_interval: Optional[dict[str, int]] = field(default_factory=dict)

    def declare_inputs(self, inputs):
        self.inputs = inputs
        for inp in inputs:
            self.states[inp] = False

    def update_state(self, name, high):
        assert self.hq is not None
        if self.print_interval and high:
            self.print_interval[name] = self.hq.btn_ctr
        self.states[name] = high

    def pulse(self, name: str, high: bool):
        self.update_state(name, high)
        assert self.hq is not None
        name = self.name #+ str([str(self.states[i])[0] for i in self.inputs])
        self.hq.enqueue_pulses([Pulse(name, out, any(not self.states[i] for i in self.inputs)) for out in self.output])

@dataclass
class Untyped:
    name: str
    hq: Optional["DesertMachineHQ"] = None

    def pulse(self, name: str, high: bool):
        assert self.hq is not None
        self.hq.process_queue()


@dataclass
class Pulse:
    from_module: str
    to_module: str
    high: bool

    def __repr__(self):
        return f'{self.from_module} -{"high" if self.high else "low"}-> {self.to_module}'

class DesertMachineHQ:
    def __init__(self, data: str) -> None:
        self.modules = {}
        self.pulse_queue = queue.Queue()
        self.inputs = {}
        self.high = 0
        self.low = 0
        self.btn_ctr = 0

        all_outputs = []
        for line in data.splitlines():
            name, _, *other = line.split()
            match name[0]:
                case '%':
                    name = "".join(name[1:])
                    module = FlipFlop(name, "".join(other).split(','), self)
                case '&':
                    name = "".join(name[1:])
                    module = Conjunction(name, "".join(other).split(','), self)
                case _:
                    module = Broadcaster(name, "".join(other).split(','), self)
            self.modules[name] = module

            for out in "".join(other).split(','):
                all_outputs.append((name, out))

        for inp, out in all_outputs:
            if out not in self.modules:
                self.modules[out] = Untyped(out, self)

            if isinstance(self.modules[out], Conjunction):
                if out not in self.inputs:
                    self.inputs[out] = []
                self.inputs[out].append(inp)

        for name, inputs in self.inputs.items():
            self.modules[name].declare_inputs(inputs)

    def enqueue_pulses(self, pulses):
        for pulse in pulses:
            self.pulse_queue.put(pulse)
        self.process_queue()

    def process_queue(self):
        while not self.pulse_queue.empty():
            pulse = self.pulse_queue.get()
            # print(pulse)
            if pulse.high:
                self.high += 1
            else:
                self.low += 1
            self.modules[pulse.to_module].pulse(pulse.from_module, pulse.high)

    def press_button(self):
        self.btn_ctr += 1
        self.enqueue_pulses([Pulse('button', 'broadcaster', False)])

    def stats(self):
        return self.high*self.low


def part1(A):
    hq = DesertMachineHQ(A)
    for _ in range(1000):
        hq.press_button()
    print("Solution 1:", hq.stats())


def part2(A):
    hq = DesertMachineHQ(A)
    rg = next((value for _, value in hq.modules.items() if not isinstance(value, Untyped) and 'rx' in value.output))
    rg.print_interval = {k: -1 for k in rg.inputs}
    for _ in range(10000):
        hq.press_button()
        if all([v!=-1 for _, v in rg.print_interval.items()]):
            break

    print("Solution 2:", lcm(*list(rg.print_interval.values())))


part1(A)
part2(A)
