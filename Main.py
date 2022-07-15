import os
import sys


import UI
from PyQt5.QtWidgets import QApplication, QWidget,QMainWindow
#资源文件路径转换
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def Intialize():
    self_path=os.getcwd()
    file_json = resource_path(os.path.join("res", "xls_data.json"))
    file_xls = resource_path(os.path.join("res", "result.xls"))
    file_data=resource_path(os.path.join("res","JFadjust_all.in2"))
    open(os.path.join(self_path,'xls_data.json'),'w',encoding='UTF-8').write(open(file_json,'r',encoding='UTF-8').read())
    open(os.path.join(self_path,'result.xls'),'wb').write(open(file_xls,'rb').read())
    open(os.path.join(self_path,'JFadjust_all.in2'),'w',encoding='UTF-8').write(open(file_data,'r',encoding='UTF-8').read())

if __name__ == '__main__':
    Intialize()
    app = QApplication(sys.argv)

    MainWindow = QMainWindow()
    ui = UI.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    sys.exit(app.exec_())

