# -*- coding: utf-8 -*-
#!/usr/bin/env python3


from typing import Optional
from math import ceil


class Conv:
    def __init__(
        self,
        pattern: str,
        input_shape: list,
        output_shape: list,
        kernel_shape: list,
        pads: list,
        strides: list,
        bias: Optional[list] = None,
        dilation: Optional[list] = None,
    ):
        self.op_type = "Conv"
        self.store_pattern = pattern
        self.inp = input_shape
        self.outp = output_shape
        self.kernel = kernel_shape
        self.pads = pads
        self.strides = strides
        self.bias = bias
        self.dilation = dilation
        self._init_weight_shape(self.store_pattern)

    def _init_weight_shape(self, pattern):
        if pattern == "onnx":
            self.weight = [
                self.outp[1],
                self.inp[1],
                self.kernel[0],
                self.kernel[1],
            ]
        elif pattern == "ka":
            self.weight = [
                self.inp[0],
                self.kernel[0],
                self.kernel[1],
                (self.outp[1] - 1) * 32 + self.outp[4],
                self.inp[4],
            ]
        else:
            raise Exception("{} pattern is not supported!".format(self.store_pattern))

    def ka_to_onnx(self):
        '''nchw_to_nchwc32'''
        self.store_pattern = "onnx"
        pass

    def onnx_to_ka(self, fram_bank_width):
        '''nchwc32_to_nchwc32'''
        if self.store_pattern == "ka":
            return
        self.store_pattern = "ka"
        inp_tmp = [
            self.inp[0],
            self._get_quotient(self.inp[1], fram_bank_width),
            self.inp[2],
            self.inp[3],
            self._get_remainder(self.inp[1], fram_bank_width),
        ]
        outp_tmp = [
            self.outp[0],
            self._get_quotient(self.outp[1], fram_bank_width),
            self.outp[2],
            self.outp[3],
            self._get_remainder(self.outp[1], fram_bank_width),
        ]
        self.inp = inp_tmp
        self.outp = outp_tmp
        self._init_weight_shape("ka")

    def _get_remainder(self, a, b):
        if a % b == 0:
            return b
        return a % b

    def _get_quotient(self, a, b):
        return ceil(a / b)

    def script(self):
        print("@kernel:{}".format(self.kernel))
        print("@pads:{}".format(self.pads))
        print("@strides:{}".format(self.strides))
        print("@bias:{}".format(self.bias))
        print("@dilation:{}".format(self.dilation))
        print("{} {} -> {}".format(self.inp, self.weight, self.outp))
