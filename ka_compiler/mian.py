# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import onnx
from ka_operator import Conv
from mem import Fram
from op_schedule import OpSchedule


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
    conv1 = Conv(
        "onnx",
        [1, 3, 384, 704],
        [1, 64, 192, 352],
        [7, 7],
        [3, 3, 3, 3],
        [2, 2],
    )
    conv1.onnx_to_ka(fram.bank_width)
    conv1.script()
    conv1.msb = OpSchedule(conv1.op_type).run(conv1)


def update():
    pass


def get_splitted_block(ori_block: list, ori_factor: list, fram: Fram):
    pass
    # output_bound = True
    # input_bound = True
    # while output_bound or input_bound:

    #     # split_factor

    #     # update output_bound
    #     # update input_bound

    #     if output_bound:
    #         ori_block, ori_factor = update(ori_block, ori_factor)


if __name__ == "__main__":
    main()
