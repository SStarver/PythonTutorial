# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import numpy as np
from queue import Queue


def convert_c32_to_c(c, c32) -> int:
    return (c - 1) * 32 + c32


def get_nc_idx(nc_idx_old, idx, idx_old, factor, flag):
    if (idx[0] == factor[0] - 1) and idx[1] == 0 and flag:
        return 0
    if idx_old == None:
        return 0
    if idx_old[0] != idx[0] or idx_old[1] != idx[1]:
        return (nc_idx_old + 1) % 8


def get_psum(inp_c_idx, inp_c_num):
    if inp_c_num == 1:
        return 0
    elif inp_c_idx == 0:
        return 1
    elif inp_c_idx == inp_c_num - 1:
        return 2
    else:
        return 3


def test_1(outp_mb, inp_mb, outp, inp):
    '''assumption: outp[3] % outp_mb[3] == 0'''
    shape_ori = np.array(
        [
            outp[2],
            outp[3],
            convert_c32_to_c(outp[1], outp[4]),
            convert_c32_to_c(inp[1], inp[4]),
        ]
    )
    shape_mb = np.array(
        [
            outp_mb[2],
            outp_mb[3],
            convert_c32_to_c(outp_mb[1], outp_mb[4]),
            convert_c32_to_c(inp_mb[1], inp_mb[4]),
        ]
    )

    factor = np.ceil(np.divide(shape_ori, shape_mb)).astype(np.int32)
    print(factor)
    ndidx = np.ndindex(tuple(factor))
    ql = [[] for i in range(8)]
    # ql = [Queue() for i in range(8)]
    # 第几个nc 怎么计算？
    # partial sum tagging？
    # Co 要在同一个NC 做
    q_padding_flag = False
    if shape_ori[0] % shape_mb[0] != 0:
        q_padding_flag = True
    nc_idx = 0
    idx_old = None
    for idx in ndidx:
        # nc_idx = get_nc_idx(idx, factor, q_padding_flag)
        nc_idx = get_nc_idx(nc_idx, idx, idx_old, factor, q_padding_flag)
        psum = get_psum(idx[3], factor[3])
        ka_slice = slice_node(idx, nc_idx, psum)
        # ql[nc_idx].put(ka_slice)
        ql[nc_idx].append(ka_slice)
        if (idx[0] == factor[0] - 2) and idx[1] == factor[1] - 1 and q_padding_flag:
            for nc in range(nc_idx + 1, 8):
                ql[nc].append(slice_node(idx, nc_idx, psum, True))
            # nc_idx = 0
        idx_old = idx
    print(len(ql))
    for nc_ in range(8):
        print("****nc: %d****" % nc_)
        # while not ql[nc_].empty():
        #     print(ql[nc_].get())
        for node in ql[nc_]:
            print(node)
    task = parse(ql)
    return task


class slice_node:
    def __init__(self, idx, nc_idx, psum, type=False):
        self.none_type = type
        self.idx = idx  # HWCoCi block index
        self.nc_idx = nc_idx
        self.psum = (
            psum  # 0-direct conv/ 1-partial sum start / 2-partial sum / 3-partial end
        )

    def __str__(self) -> str:
        s = ""
        s += "{} {} {} {}".format(self.nc_idx, self.none_type, self.psum, self.idx)
        return s


def parse(slice_list: list[list]):
    nc_num = len(slice_list)
    # check if length of every queue equals to each other
    for slice in slice_list:
        if len(slice) != len(slice_list[0]):
            print("oops!")

    # take in one slice from every list to form a task
    # todo: two dimension slice design???
    task = [[]]
    for i in range(len(slice_list[0])):
        for nc in range(nc_num):
            task[i].append(slice_list[nc][i])
    return task


def gen_ir_list(task_stream: list[list[slice_node]]):
    cur_task = None
    f = None
    for task in task_stream:
        old_task = cur_task
        cur_task = task
        gen_ir_list_for_one_task(
            f,
            cur_task,
            old_task,
        )
    # check current task to last task to determine if weight need to be reloaded
    # go through slices in current task and gen dma input conv and dma output instructions


def gen_ir_list_for_one_task():
    pass


# weight 在什么阶段进行拆分并分配地址？
# DMA weight ddr -> wram
