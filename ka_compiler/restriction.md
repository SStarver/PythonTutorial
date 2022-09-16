# Introduction To MicroArch

## Parallelism
> Cin = 32
> Cout = 32
> H = 1
> W = 1

> **note**: After split, an output block with (H*W)align8 would be adviced, and maximum hardware efficiency would be meet. However, a block with (H*W) == (3*4) still gains more efficiency than two blocks with shape (2*4) plus (1*4)
> **Reason**: WRAM needs 8 cycles to load all data needed for one calculation

## partial sum
- Ci channel tiling restriction
> Co <= 32  
> H*W <= 64

- conv -> matmul (位域)
> transpose bitfield: hwc -> 1 * c * (hw)


# Introduction To Mem
## FRAM
- **Storage Specification**
> 8 banks per NC  
> bank width: 512 bits  
> bank depth: 128  
> each bank can be read/written at one time  

- **Store pattern: NCHWC32**
> *sizeof(HWC32)* should be aligned to 512 bits (length of one FRAM line)  
> *start_addr_of(HWC32)* should be aligned to 512 bits  
> *C32*: when size is smaller than 32 nodes, C32 should be aligned to C4/C8/C16/C32 according to real size  
> *data node*: float16 -> 2 Byte/node  int8 -> 1 Byte  

## WRAM
- **Storage Specification**
> all NC share 2 banks  
> bank width: 2048 bits  (8 times amplifier in hardware)
> bank depth: 4096  
> each bank can be read/written at one time  

- **Store pattern: CKhKwFC32**
> *C32* is similar to that of FRAM  
> *sizeof(FC32)* should be aligned to 2048 bits (length of one line)  
> *start_addr_of(FC32)* should be aligned to 2048 bits  

## DDR
> start addr of data aligned to 256 B  
> size of data reuqirements	refers to data type(ie. weights -> wram, input -> fram)  

## BRAM: TBD

# A&Q
## Normal	
> A: 如果Cin方向想要不tiling，且C32 != 32时，DMA 需要搬两次？  
> Q: Yes, 当前ISA 只支持HWC32内部tiling, 后续增加支持CHWC32 内部tiling.  
> TBD: N 层面的stride是否需要支持  

> A: conv 等运算都需要传入实际的shape?  
> Q: Yes  

> A: 指令位域中是否要支持对齐前后C32的位域？  
> Q: 不补充，指令中仅传入实际的C32值即可   

> A：Padding 实现方式是？  
> Q: TBD --20220907   

> A: 非对齐部分的数据，软件是否要确保补零？还是可以为随机数，硬件保证不用？  
> 软件只能操作input数据和weight 数据，无法保证中间数据。input数据和weight 数据非对齐部分是否需要补零？  
> Q: TBD  

> A: when gathering from H6W12C4 shape data to get a H3W3C4 data, how does hardware behaves?  
> Q: just extract corresponding data and put them into target memory and do align to it.  

> A: how many nested loops of skip gathering would hardware supported?  

## extensions
> A: 并行度、mac阵列排布、数据对齐约束之间的关系  

> A: 硬件怎么做到使用当前的数据排布（例如 C32 == 4）情况下位域不做信息计算转换直接用的？  


