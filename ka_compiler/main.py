# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import onnx
from mem import Wram
from ka_operator import Conv
from mem import Fram
from op_schedule import OpSchedule
import test


def main():
    '''Just deal with onnx with one layer'''
    # onnx_file = "demo.onnx"
    # model = onnx.load(onnx_file)
    # mymodel = onnx.shape_inference.infer_shapes(model)

    # Turn operator into self-defined IR
    # Preprocess: convert data format to NCHWC32 for Fram or CKhKwFC32 for Wram
    # do splitting, and gen sliced op
    # insert dma instructions
    fram = Fram()
    wram = Wram()
    conv2 = Conv(
        "onnx",
        [1, 3, 384, 704],
        [1, 64, 192, 352],
        [7, 7],
        [3, 3, 3, 3],
        [2, 2],
    )
    conv1 = Conv(
        "onnx",
        [1, 64, 96, 176],
        [1, 64, 96, 176],
        [3, 3],
        [1, 1, 1, 1],
        [1, 1],
    )
    conv1.onnx_to_ka(fram.bank_width)
    OpSchedule(conv1.op_type).run(conv1, fram, wram)
    conv1.script()
    # task_stream: task1[NC0 NC1 ... NCn-1] task2 task3
    task_stream = test.test_1(conv1.outp_mb, conv1.inp_mb, conv1.outp, conv1.inp)
    test.gen_ir_list(task_stream)


if __name__ == "__main__":
    main()
