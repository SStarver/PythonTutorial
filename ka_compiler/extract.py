#!/usr/bin/env python3]

import onnx
from onnx import utils

onnx_file = "my_model.onnx"
out_name = "./my_model_extract.onnx"
mymodel = onnx.load(onnx_file)
mygraph = mymodel.graph
utils.extract_model(
    input_path=onnx_file,
    output_path=out_name,
    input_names=["conv_x", "conv_w"],
    output_names=["conv_y"],
    check_model=False,
)
