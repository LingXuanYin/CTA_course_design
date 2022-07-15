# 测量平差课程设计--闭合导线平差
### 2022-7-15

## 快速开始
`./dist/Main.exe`是编译好的可执行文件，仅支持win8.1以上的系统运行

输入数据文件`./res/JFadjust_all.in2`（科傻格式），以及需要平差的闭合导线`T20-T22-T5-T6-T8-T41-T40-T39-T38-T22`，点击平差按钮，就会自动展示闭合导线略图，并将表格保存到`./result.xls`，略图保存到`./sketch.png`

## 通过源文件运行
函数入口在`./Main.py`
直接运行即可

## 自己编译
使用pyinstaller，在命令行中运行：`pyinstaller -F -w -p ./pkg  Main.spec`
`./pkg`中应当包括xlrd、xlutils、xlwt三个python软件包
