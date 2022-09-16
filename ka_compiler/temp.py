# conv：

# assumption:
# 1) N == 1 or split to 1


# 2、weight -> wram bound?
# 	a) not bounded
# 		pass
# 	b) bounded
# 		if cout <= 32:
# 			split Cin
# 		else:
# 			split cout to c32:
# 			if still bounded:
# 				split along Cin(schedule to be discussed)
# 				if still bounded:
# 					raise error("unsupported case")
# 				else:
# 					pass
# 			else:
# 				pass

# Output -> fram bound

# input -> fram bound


# output_mb input_mb weight_mb

# Fram(_align_size(output_mb))
# Fram(_align_size(input_mb))
# Wram(_align_size(weight_mb))

# Cin not split
# Cout not split
# Cout >= min(Cout_ori, 32) && Cout C32_align
# Cin >= min(Cin_ori, 32) && Cin C32_align
# factor = output_ori // output_mb:  (factor[H] * factor[W]) mod 8 == 0
# factor[H] * factor[w] mod 64 == 0 ( (HWC32) align free )

# Cout fram bound free
# Cin fram bound free
# Weight bound free

# Cin not split
# Cout not split

# weight C32 align
# Cout C32 align
# Cin C32 align

#  (factor[H] * factor[W]) mod 8 == 0
#  (factor[H] * factor[W]) mod 64 == 0

# input / output / weight

# search(outp, inp, weight)
from http.client import HTTP_VERSION_NOT_SUPPORTED
from math import ceil
from turtle import circle, width
from ka_operator import Conv
from mem import Fram
from mem import Wram

fram = Fram()
conv1 = Conv(
    "onnx",
    [1, 3, 384, 704],
    [1, 64, 192, 352],
    [7, 7],
    [3, 3, 3, 3],
    [2, 2],
)
conv1.onnx_to_ka(fram.bank_width)
input = conv1.inp
output = conv1.outp
weight = conv1.weight


def res_search(conv1, fram, Wram):
    for cout in range(1, conv1.outp[1]):
        for cin in range(1, conv1.inp[1]):
            for height in range(1, conv1.outp[2]):
                for width in range(1, conv1.outp[3]):
                    # Cout fram bound free
                    # Cin fram bound free
                    # Weight bound free
                    pass


# cout : [min(cout_c32, 32), (c - 1) * 32 + cout_c32]
# cin : [min(cin_c32, 32), (c - 1) * 32 + cin_c32]
# (cin / 32) * kh * kw * align(cout * align_c32(cin % 32)) <= wram
# size_input(NCHWC32) <= fram
# size_output(NCHWC32) <= fram

# get cout/cin/weight minimum_block
# gen slices
#

# MB :
height = 32
width = 32
chan_i = 32
chan_o = 32
chan_i_32 = 32
chan_o_32 = 32


def gen_data_slices():
    h_remain = 0
    w_remain = 0
    cin_remain = 0
    cout_remain = 0

    # recomand to divide W into several equal parts
    # divide h into several parts plus a remainder
    while h_remain:
        while w_remain:
            # NC tag
            # if shape_cur(hw) != shape_old(hw) or nc_cur == NC_MAX: nc_cur = 0, level += 1  else nc_cur + = 1
            while cout_remain:
                # gen_outp_slice
                while cin_remain:
                    # gen_weight_slice
                    # gen_input_slice
                    pass


def demo(outp_mb, outp):
    c_inp = 0
    c_outp = 0
    h_outp = 0
    w_outp = 0

    for h in range(0, h_outp):
        for w in range(0, w_outp):
            for co in range(0, c_outp):
                for ci in range(0, c_inp):
                    pass


def convert_c32_to_c(c, c32) -> int:
    return (c - 1) * 32 + c32


class slice_data:
    def __init__(self, nc):
        self.nc = nc


def test(outp_mb, inp_mb, outp, inp):
    ho_num = ceil(outp[2] / outp_mb[2])
    wo_num = ceil(outp[3] / outp_mb[3])
    co_num = ceil(
        convert_c32_to_c(outp[1], outp[4]) / convert_c32_to_c(outp_mb[1], outp_mb[4])
    )
    ci_num = ceil(
        convert_c32_to_c(inp[1], inp[4]) / convert_c32_to_c(inp_mb[1], inp_mb[4])
    )
    # if shape_cur(hw) != shape_old(hw) or nc_cur == NC_MAX: nc_cur = 0, level += 1  else nc_cur + = 1

    nc_cur = 0
    slice_list = []
    # h_blk = outp_mb[2]
    # w_blk = outp_mb[3]
    # h_blk_his = outp_mb[2]
    # w_blk_his = outp_mb[3]
    for h_idx in range(0, ho_num):
        for w_idx in range(0, wo_num):
            nc_cur += 1 if nc_cur < 7 else 0
            if (
                (h_idx == ho_num - 1)
                and (w_idx == 0)
                and outp_mb[2] != outp[2] - h_idx * outp_mb[2]
            ):  # and hblk != hblk_his
                nc_cur = 0
            # slice_list.append(slice_data(nc_cur))
            for co_idx in range(0, co_num):
                for ci_idx in range(0, ci_num):
                    slice_data = gen_data_slice(ci_blk, co_blk, h_blk, w_blk, nc_cur)
