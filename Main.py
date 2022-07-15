# -*- coding: utf-8 -*-


import os
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

import UI


# 资源文件路径转换
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# 初始化
def Intialize():
    self_path = os.getcwd()
    # 资源文件路径转换
    file_json = resource_path(os.path.join("res", "xls_data.json"))
    file_xls = resource_path(os.path.join("res", "result.xls"))
    file_data = resource_path(os.path.join("res", "JFadjust_all.in2"))
    # 资源文件释放
    open(os.path.join(self_path, 'xls_data.json'), 'w', encoding='UTF-8').write(
        open(file_json, 'r', encoding='UTF-8').read())
    open(os.path.join(self_path, 'result.xls'), 'wb').write(open(file_xls, 'rb').read())
    open(os.path.join(self_path, 'JFadjust_all.in2'), 'w', encoding='UTF-8').write(
        open(file_data, 'r', encoding='UTF-8').read())


# 程序入口
if __name__ == '__main__':
    # 初始化
    Intialize()

    app = QApplication(sys.argv)

    MainWindow = QMainWindow()
    ui = UI.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()  # 展示主窗口

    sys.exit(app.exec_())
