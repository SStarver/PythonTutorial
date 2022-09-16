# -*- coding: utf-8 -*-
#!/usr/bin/env python3


class Fram:
    def __init__(self):
        self.bank_width = 32  # unit: nodes, corresponding to 512 bits, or line_width
        self.bank_depth = 512
        self.bank_num = 8


class Wram:
    def __init__(self):
        self.bank_width = 128  # unit: nodes, corresponding to 2048 bits
        self.bank_depth = 4096
        self.bank_num = 1


class Desc:
    def __init__(self, axes, starts, ends, steps):
        self.axes = axes
        self.starts = starts
        self.ends = ends
        self.steps = steps
