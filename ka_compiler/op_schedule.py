# -*- coding: utf-8 -*-
#!/usr/bin/env python3


from math import ceil, floor
from temp.ka_operator import Conv
import numpy as np

from temp.mem import Fram


class OpSchedule:
    def __init__(self, op_type):
        if op_type == "Conv":
            return ConvSchedule


class ConvSchedule:
    def __init__(self):
        self.ka_op = None

    def run(self, conv: Conv, fram: Fram):
        self.ka_op = conv
        # get output nsb
        nsf = self._pick_nsf(conv.outp)
        # hack: nsb * nsf == conv.outp
        nsb = np.floor_divide(conv.outp, nsf)
        # get_output_minimum_block(nsb, depth, width)
        fsb = self._get_minimum_block_shape(nsb, fram.bank_depth, fram.bank_depth)
        # infer input block_shape
        input_block = self._infer_input(conv.inp, fsb, conv.strides, conv.kernel)
        # get_input_minimum_block(input_block, depth, width)
        input_block_new = self._get_minimum_block_shape(
            input_block, fram.bank_depth, fram.bank_depth
        )

        # get factor
        # update output_block // hack: input factor update is sufficient
        factor = floor(input_block / input_block_new)
        msb = fsb / factor
        return msb

    def _pick_nsf(self, data_shape: np.array) -> np.array:
        # hack: 8 NC, four split choices in order
        nsf_factory = [
            [1, 1, 1, 8, 1],
            [1, 1, 2, 4, 1],
            [1, 1, 4, 2, 1],
            [1, 1, 8, 1, 1],
        ]
        for nsf in nsf_factory:
            if np.mod(data_shape, nsf).any():
                continue
            else:
                return nsf
        raise Exception("fail to pick nsf for shape {}".format(data_shape))

    def _get_minimum_block_shape(self, block_shape, depth, bank_width):
        c = block_shape[1]
        h = block_shape[2]
        w = block_shape[3]
        c32 = self._align_c32(block_shape[4])

        if ((c - 1) * 32 * h * w + self._align_32(c32 * h * w)) <= depth * bank_width:
            res = block_shape.copy()
        elif ((c - 1) * 32 * 8 * w + c32 * 8 * w) <= depth * bank_width:
            res = block_shape.copy()
            res[2] = 8 * floor(
                depth * bank_width / ((c - 1) * 32 * 8 * w + c32 * 8 * w)
            )
        elif ((c - 1) * 32 * 8 + c32 * 8) <= depth * bank_width:
            res = block_shape.copy()
            res[2] = 8
            res[3] = depth * bank_width / ((c - 1) * 32 * 8 + c32 * 8)
        else:
            raise Exception("oops")
        return res

    def _align_32(size):
        return ceil(size / 32) * 32

    def _align_c32(size):
        if size >= 32:
            raise Exception("unsupported size!")
        elif size > 16:
            return 32
        elif size > 8:
            return 16
        elif size > 4:
            return 8
        else:
            return 4

    def _infer_input(self, input_shape, output_mb, strides, kernel):
        # padding already
        input_mb = np.array(
            [
                input_shape[0],
                input_shape[1],
                (output_mb[2] - 1) * strides[0] + kernel[0],
                (output_mb[3] - 1) * strides[1] + kernel[1],
                input_shape[3],
            ]
        )
        return input_mb
