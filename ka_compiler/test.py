# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from math import ceil, floor
from mem import Fram
import numpy as np


def align_32(size):
    return ceil(size / 32) * 32


output_shape = np.array([1, 2, 192, 352, 32], dtype=int)
nsf = np.array([1, 1, 4, 2, 1], dtype=int)
nsb = np.divide(output_shape, nsf).astype(np.int32)
print(nsb)
fram = Fram()


def _get_minimum_block_shape(block_shape, depth, bank_width):
    c = block_shape[1]
    h = block_shape[2]
    w = block_shape[3]
    c32 = block_shape[4]
    # case1: all h*w*c can be filled
    # mb = data_shape
    if ((c - 1) * 32 * h * w + align_32(c32 * h * w)) <= depth * bank_width:
        res = block_shape.copy()
    # case2: hline * bank_num * w * c can be filled
    # mb = [data_shape[0], hline * bank_num, data_shape[2], data_shape[3]]
    elif ((c - 1) * 32 * 8 * w + c32 * 8 * w) <= depth * bank_width:
        res = block_shape.copy()
        res[2] = 8 * floor(depth * bank_width / ((c - 1) * 32 * 8 * w + c32 * 8 * w))
    # case3: single hline can't be filled. Wlin * c can be filled
    # mb = [data_shape[0], bank_num, Wline, data_shape[3]]
    elif ((c - 1) * 32 * 8 + c32 * 8) <= depth * bank_width:
        res = block_shape.copy()
        res[2] = 8
        res[3] = depth * bank_width / ((c - 1) * 32 * 8 + c32 * 8)
    # otherwise: exception
    else:
        raise Exception("oops")
    return res
