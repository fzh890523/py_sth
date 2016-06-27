# encoding: utf-8

__author__ = 'fzh89'

s = """第2讲 实验零 操作系统实验环境准备

第3讲 系统启动、中断、异常和系统调用

第4讲 实验一 bootloader启动ucore os

第5讲 物理内存管理: 连续内存分配

第6讲 物理内存管理: 非连续内存分配

第7讲 实验二 物理内存管理

第8讲 虚拟存储概念

第9讲 页面置换算法

第10讲 实验三 虚拟内存管理

第11讲 进程与线程

第12讲 进程控制

期中考试 期中考试: 第7周星期一 （2015年4月13日）

第13讲 实验四 内核线程管理

第14讲 实验五 用户进程管理

第15讲 处理机调度

第16讲 实验六 调度器

第17讲 同步互斥

第18讲 信号量和管程

第19讲 实验七 同步互斥

第20讲 死锁和进程通信

第21讲 文件系统

第22讲 实验八 SFS文件系统

第23讲 I/O子系统

期末考试 期末考试: 待定

课程设计报告 待定
"""

l = list(filter(lambda a: True if a else False, s.splitlines()))

for line in l:
    if line[0] != "第":
        print(line)
    else:
        num_str = line[1:line.index("讲")]
        num = int(num_str)
        print("[**%s**](chap_%02d/%02d.md)" % (line, num, num))