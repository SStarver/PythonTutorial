#!/usr/bin/env python3


import onnx
from onnx import helper
from onnx import AttributeProto, TensorProto, GraphProto
import numpy as np

# The protobuf definition can be found here:
# https://github.com/onnx/onnx/blob/main/onnx/onnx.proto


conv_x = helper.make_tensor_value_info('conv_x', TensorProto.INT16, [1, 1, 16, 16])
conv_y = helper.make_tensor_value_info('conv_y', TensorProto.INT16, [1, 1, 16, 16])
conv_w = helper.make_tensor(
    'conv_w',
    TensorProto.INT16,
    [1, 1, 3, 3],
    np.array([[[0, 1, 0], [1, 2, 1], [1, 3, 1]]], dtype=np.int16),
)

conv_node = onnx.helper.make_node(
    "Conv",
    inputs=["conv_x", "conv_w"],
    outputs=["conv_y"],
    kernel_shape=[3, 3],
    # Default values for other attributes: strides=[1, 1], dilations=[1, 1], groups=1
    pads=[1, 1, 1, 1],
)

# Create second input (ValueInfoProto)
# Pads = helper.make_tensor_value_info('Pads', TensorProto.INT64, [4])

# Create one output (ValueInfoProto)
Y = helper.make_tensor_value_info('Y', TensorProto.INT16, [1, 1, 16, 16])

# Create a node (NodeProto)
Relu_node = helper.make_node(
    'Relu',  # node name
    ['conv_y'],  # inputs
    ['Y'],  # outputs
    # mode='constant',  # Attributes
)


# Create the graph (GraphProto)
graph_def = helper.make_graph(
    [conv_node, Relu_node],
    "test-model",
    [conv_x],
    [Y],
    [conv_w],
)

# Create the model (ModelProto)
model_def = helper.make_model(graph_def, producer_name='onnx-example')

print('The producer_name in model: {}\n'.format(model_def.producer_name))
print('The graph in model:\n{}'.format(model_def.graph))
onnx.checker.check_model(model_def)
print('The model is checked!')
onnx.save_model(model_def, "my_model.onnx")
