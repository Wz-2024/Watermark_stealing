## 参考文献：<a href="http://arxiv.org/abs/2402.19361">Watermark Stealing in LLM</a>
本repo的大部分代码来自上述文献，这里说明一些代码运行中可能存在的一些问题，
## 1.环境搭建
这里参考原仓库提供的说明文档。需要说明的是，`xform`可以不装。原作者在`bash`文件中写入了这个`pip install -U flash-attn --no-build-isolation`。但是这个库直接这样下载是不太可能成功的，您需要下载预编译`whl`文件，然后把它安装到当前环境中。
## 2.执行流详解
这里请参考笔者的这份文档：
https://fcn67dvu0kd4.feishu.cn/docx/GPQUdYViMoWbIMxWBZYcYiqVnWF?from=from_copylink <br>
我从文章的理解开始，一直讲到运行得到的最终效果，非常全面
## 3.讨论
首先说明，这篇文献作为`ICML-2024`，提出的方法非常牛，时间开销和计算资源开销都很小(video memory<30G,<20h).<br>
并且提出了水印窃取和水印擦除并没有存在权衡的关系。利用`dipper`模型后，擦除效果更是远高于SOTA。<br>
笔者认为一点小缺陷是远项目的代码组织有点混乱，调用关系难以理清，在上述的执行流文档中理清了关系，但是耗费了好几天的时间。