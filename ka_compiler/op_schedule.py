# -*- coding: utf-8 -*-
#!/usr/bin/env python3


from math import ceil, floor
import math
from turtle import width
from ka_operator import Conv
import numpy as np
from mem import Fram
from mem import Wram


class OpSchedule:
    def __init__(self, op_type):
        self.op_type = op_type

    def run(self, *args):
        if self.op_type == "Conv":
            ConvSchedule().run(*args)
            # ConvSchedule().run(args[0], args[1], args[2])


class ConvSchedule:
    def __init__(self):
        self.ka_op = None

    def run(self, conv: Conv, fram: Fram, wram: Wram):
        self.ka_op = conv
        weight_mb = self._get_weight_mb(conv.weight, wram)
        inp_mb = self._get_inp_mb(conv.inp, weight_mb)
        outp_mb = self._get_outp_mb(conv.outp, weight_mb)
        outp_mb = self._update_outp_mb(outp_mb, inp_mb, conv.strides, fram)
        inp_mb = self._infer_input(inp_mb, outp_mb, conv.strides, conv.kernel)
        conv.inp_mb = inp_mb
        conv.outp_mb = outp_mb
        conv.weight_mb = weight_mb
        # inp[1], outp[1] = self._update_in_out()
        # outp[1] = ceil(weight_mb[3] / 32)
        # inp[1] = weight_mb[0]
        # get output nsb
        # nsf = self._pick_nsf(outp)
        # # hack: nsb * nsf == conv.outp
        # nsb = np.floor_divide(outp, nsf).astype(np.int32)
        # # get_output_minimum_block(nsb, depth, width)
        # fsb = self._get_minimum_block_shape(nsb, fram.bank_depth, fram.bank_width)
        # # infer input block_shape
        # input_block = self._infer_input(inp, fsb, conv.strides, conv.kernel)
        # # get_input_minimum_block(input_block, depth, width)
        # input_block_new = self._get_minimum_block_shape(
        #     input_block, fram.bank_depth, fram.bank_width
        # )

        # # get factor
        # # update output_block // hack: input factor update is sufficient
        # factor = np.floor_divide(input_block, input_block_new)
        # msb = np.floor_divide(fsb, factor)
        # input_block_tmp = self._infer_input(inp, msb, conv.strides, conv.kernel)

        # # gen slice para: msb, conv.outp -> gen slice para
        # print("msb: {} nsf: {} input_mb:{}".format(msb, nsf, input_block_tmp))
        # outp_msb_size = (
        #     msb[0] * msb[1] * self._align_32(msb[2] * msb[3] * self._align_c32(msb[4]))
        # )
        # input_mb_size = (
        #     input_block_tmp[0]
        #     * input_block_tmp[1]
        #     * self._align_32(
        #         input_block_tmp[2]
        #         * input_block_tmp[3]
        #         * self._align_c32(input_block_tmp[4])
        #     )
        # )
        # fram_size = fram.bank_depth * fram.bank_width
        # if outp_msb_size > fram_size or input_mb_size > fram_size:
        #     raise Exception(
        #         "outp:{} inp:{} fram:{}".format(outp_msb_size, input_mb_size, fram_size)
        #     )

    def _update_outp_mb(self, outp_mb, inp_mb, strides, fram):
        '''
        Ho * Wo * Strides * Strides * Ci <= Fram_size
        Ho * Wo  * Co <= Fram_size
        Ho <= Ho_
        Wo <= Wo_
        Wo_ % Wo == 0
        Ho * Wo <= Ho_ * Wo_ / 8
        Ho * Wo % 8 == 0 prefered
        '''
        size_available = fram.bank_depth * fram.bank_width
        outp_hw_bound_size = size_available // (
            (outp_mb[1] - 1) * 32 + self._align_c32(outp_mb[4])
        )
        inp_hw_bound_size = size_available // (
            strides[0]
            * strides[1]
            * ((inp_mb[1] - 1) * 32 + self._align_c32(inp_mb[4]))
        )
        bound_size = min(outp_hw_bound_size, inp_hw_bound_size)
        # hack: we can extract a factor of 8 from H * W
        # hack: minimum block is consist of factors from H & W
        # extract a factor of 8 from H * W
        # gen sorted factor list h_factor \ w_factor
        # extract factor, till factor used >= 8
        # check bound condition
        # extract factors, till bound requirement meets
        h_factors = self._descend_factorization(outp_mb[2])
        w_factors = self._descend_factorization(outp_mb[3])
        factor_extracted = 1
        # extract factor >= 8 from H&W
        while factor_extracted < 8 and (h_factors or w_factors):
            idx, factor = self._get_min_factor(h_factors, w_factors)
            factor_extracted = factor_extracted * factor
            outp_mb[idx + 2] = outp_mb[idx + 2] // factor
            if idx == 0:
                h_factors.pop(-1)
            else:
                w_factors.pop(-1)

        if bound_size >= outp_mb[2] * outp_mb[3]:
            return outp_mb

        # extract factors till fit fram
        outp_mb = self._get_bounded_outp(outp_mb, bound_size)
        return outp_mb
        # while (bound_size < outp_mb[2] * outp_mb[3]) and (h_factors or w_factors):
        #     idx, factor = self._get_min_factor(h_factors, w_factors)
        #     outp_mb[idx + 2] = outp_mb[idx + 2] // factor
        #     if idx == 0:
        #         h_factors.pop(-1)
        #     else:
        #         w_factors.pop(-1)

        # if bound_size >= outp_mb[2] * outp_mb[3]:
        #     return outp_mb
        # raise Exception(
        #     "height * weight has spllitted to 1 {} {}".format(h_factors, w_factors)
        # )

    def _get_bounded_outp(self, outp_mb, bound_size):
        height = outp_mb[2]
        weight = outp_mb[3]
        divisior_h = []
        divisior_w = []
        res_pair = [
            1,
            1,
            1,
        ]

        for h in range(1, height + 1):
            if height % h == 0:
                divisior_h.append(h)
        for w in range(1, weight + 1):
            if weight % w == 0:
                divisior_w.append(w)

        for h in divisior_h:
            for w in divisior_w:
                if (h * w) == bound_size:
                    outp_mb[2] = h
                    outp_mb[3] = w
                    return outp_mb
                elif h * w < bound_size and h * w > res_pair[2]:
                    res_pair[0] = h
                    res_pair[1] = w
                    res_pair[2] = h * w
        outp_mb[2] = res_pair[0]
        outp_mb[3] = res_pair[1]
        return outp_mb

    def _descend_factorization(self, val):
        descend_factors = []
        while val > 1:
            for i in range(2, val + 1):
                # for i in range(2, ceil(math.sqrt(val))):
                if val % i == 0:
                    descend_factors.append(i)
                    val = val // i
                    break
            # if i == ceil(math.sqrt(val)) - 1:
            #     descend_factors.append(val)
            #     val = 1

        descend_factors.sort(reverse=True)
        return descend_factors

    def _get_min_factor(self, a_factors, b_factors):
        if a_factors and not b_factors:
            axes = 0
            extracted_factor = a_factors[-1]
        elif not a_factors and b_factors:
            axes = 1
            extracted_factor = b_factors[-1]
        elif a_factors and b_factors:
            if a_factors[-1] <= b_factors[-1]:
                axes = 0
                extracted_factor = a_factors[-1]
            else:
                axes = 1
                extracted_factor = b_factors[-1]
        else:
            raise Exception("Both factor lists are empty")
        return axes, extracted_factor

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
                return np.array(nsf)
        raise Exception("fail to pick nsf for shape {}".format(data_shape))

    def _get_minimum_block_shape(self, block_shape, depth, bank_width):
        c = block_shape[1]
        h = block_shape[2]
        w = block_shape[3]
        c32 = self._align_c32(block_shape[4])

        res = block_shape.copy()
        if ((c - 1) * 32 * h * w + self._align_32(c32 * h * w)) <= depth * bank_width:
            pass
        elif ((c - 1) * 32 * 8 * w + c32 * 8 * w) <= depth * bank_width:
            res[2] = 8 * floor(
                depth * bank_width / ((c - 1) * 32 * 8 * w + c32 * 8 * w)
            )
        elif ((c - 1) * 32 * 8 + c32 * 8) <= depth * bank_width:
            res[2] = 8
            res[3] = depth * bank_width / ((c - 1) * 32 * 8 + c32 * 8)
        else:
            raise Exception("oops")
        return res

    def _align_32(self, size):
        return ceil(size / 32) * 32

    def _align_c32(self, size):
        if size > 32:
            raise Exception("[{}]unsupported size!".format(size))
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
                input_shape[4],
            ]
        )
        return input_mb

    def _get_weight_mb(self, weight, wram):
        '''
        setp 1:cin & cout not split
        step 2:cout split to 32 nodes
        step 3:cin split to 32 nodes
        '''
        weight_mb = weight.copy()
        weight_size = self._get_weight_size(weight_mb, wram.bank_width)
        if weight_size <= wram.bank_depth * wram.bank_width:
            return weight_mb

        if weight_mb[3] > 32:
            weight_mb[3] = 32
            weight_size = self._get_weight_size(weight_mb, wram.bank_width)
            if weight_size <= wram.bank_depth * wram.bank_width:
                return weight_mb

        if weight_mb[0] > 1:
            weight_mb[0] = 1
            weight_mb[4] = 32
            weight_size = self._get_weight_size(weight_mb, wram.bank_width)
            if weight_size <= wram.bank_depth * wram.bank_width:
                return weight_mb

        raise Exception("weight: {} is bounded!".format(weight_mb))

    def _get_outp_mb(self, outp, weight_mb):
        outp_mb = outp.copy()
        outp_mb[1] = ceil(weight_mb[3] / 32)
        outp_mb[4] = self._get_remainder(weight_mb[3], 32)
        return outp_mb

    def _get_remainder(self, a, b):
        # a - floor(a / b)
        if a % b == 0:
            return b
        return a % b

    def _get_quotient(self, a, b):
        return ceil(a / b)

    def _get_inp_mb(self, inp, weight_mb):
        inp_mb = inp.copy()
        inp_mb[1] = weight_mb[0]
        inp_mb[4] = weight_mb[4]
        return inp_mb

    def _get_weight_size(self, weight, align_ment):
        '''
        calc weight size in CKhKwFC32 data format
        wram_width: Bytes
        '''
        return (
            weight[0]
            * weight[1]
            * weight[2]
            * self.align(weight[3] * self._align_c32(weight[4]), align_ment)
        )

    def align(self, size, align_ment):
        if size % align_ment == 0:
            return size
        else:
            return (size // align_ment + 1) * align_ment
