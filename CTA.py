import json
import math
import os

import matplotlib.pyplot as plt
import xlrd
import xlutils.copy


class CTA():
    def __init__(self, path: str):
        self.data, self.points_known = self.Data_read(path)
        self.deg_src, self.deg_balanced = {}, {}

    def ang_dec(self, ang: str):
        # 度分秒转小数
        if ang == '0':  # 排除0值
            return 0
        ang = ang.split('.')
        deg = ang[0]
        minute = ang[1][0:2]
        second = ang[1][2:len(ang[1])]
        return int(deg) + int(minute) / 60 + int(second) / 3600

    def rad_ang(self, rad):
        # 弧度转角度
        return rad * (180 / math.pi)

    def Data_read(self, path: str):
        # 数据读取
        line = open(path, 'r', encoding='utf-8').readlines()  # 分行读入数据
        line = line[1:len(line) - 1]  # 去除第一行
        _line = []
        # print(line)
        points_known = {}  # 初始化已知点列表
        datas = {}  # 初始化观测数据
        for l in line:
            _line.append(l.strip('\n'))  # 去除分行符
        buf = _line[0:13]  # 读已知点数据
        # 已知点数据结构：{点名:{'x':x坐标,'y':y坐标}}
        for l in buf:
            if l != '':
                l = l.split(',')
                points_known[l[0]] = {'x': float(l[1]), 'y': float(l[2])}
        buf = _line[13:len(_line)]
        _line = []
        for l in buf:
            if l != '':
                _line.append(l)
        node = None
        # datas数据结构：{点1:{关系点1:{'L':角度观测值,'S':距离观测值},关系点2:{...}},点2:{...}}
        for l in _line:
            if ',' not in l:
                node = l
            else:
                l = l.split(',')
                if node not in datas.keys():  # 不存在则新增数据节点
                    datas[node] = {}
                if l[0] not in datas[node].keys():  # 不存在则新增数据节点
                    datas[node][l[0]] = {}
                if l[1] not in datas[node][l[0]].keys():  # 不存在则新增数据节点(末端节点必定是新的)
                    if l[1] == 'L':  # 如果为角度则转为小数表示
                        datas[node][l[0]][l[1]] = self.ang_dec(l[2])  # 转化为小数赋值
                    else:
                        datas[node][l[0]][l[1]] = float(l[2])  # 直接赋值
        return datas, points_known  # 返回已知点和数据的字典

    def cal_deg_closingerror(self):
        # 计算角度闭合差
        _r = [self.route[len(self.route) - 2]] + self.route[1:]
        i = 1
        _deg = 0
        sum_closingdeg = 0
        while i < len(self.route) - 1:
            r = _r[i]
            _deg = self.data[r][_r[i - 1]]['L'] - self.data[r][_r[i + 1]]['L']
            if _deg < 0:
                _deg += 360
            self.deg_src[r] = _deg
            sum_closingdeg += _deg
            i += 1
        _dif = sum_closingdeg - (self.n - 2) * 180
        self.deg_closingerror = _dif
        # print(_dif)
        return _dif

    def cal_deg_closingerror_limited(self):
        # 计算角度闭合差限差
        _lim = int(40 * math.sqrt(self.n)) / 10000
        _lim = self.ang_dec(str(_lim))

        self.deg_limited = _lim
        if self.deg_closingerror > self.deg_limited:
            self.deg_over_limited = True
        else:
            self.deg_over_limited = False
        return self.deg_limited

    def balance_deg_closingerror(self):
        # 角度闭合差平差
        _dif = self.deg_closingerror
        bal_V = (0 - _dif) / self.n
        for deg in self.deg_src.keys():
            self.deg_balanced[deg] = self.deg_src[deg] + bal_V
        return self.deg_balanced

    def cal_deg_azimuth(self):
        # 通过已知点计算后视导线的方位角
        p1 = self.points_known[self.route[0]]
        p2 = self.points_known[self.route[1]]
        _deg_azi_backview = math.atan2((p2['y'] - p1['y']), (p2['x'] - p1['x']))
        _deg_azi_backview = self.rad_ang(_deg_azi_backview)
        if _deg_azi_backview < 0:
            _deg_azi_backview += 360
        self.deg_azi_backview = _deg_azi_backview

        # print(self.deg_azi_backview)
        # 计算第一条导线的方位角
        _d = self.data[self.route[1]][self.route[0]]['L'] - self.data[self.route[1]][self.route[2]]['L']
        if _d < 0: _d = 0 - _d
        if self.route[0] == 'T15':
            _deg = self.deg_azi_backview - _d + 180
        else:
            _deg = self.deg_azi_backview + _d - 180

        while _deg > 360:
            _deg = _deg - 360
        while _deg < 0:
            _deg = _deg + 360
        # 方位角数组数据结构：dict={导线起点名：方位角度}
        self.deg_azi = {self.route[1]: _deg}
        # print(_deg)
        # print(self.deg_balanced)
        i = 2
        while True:  # 正推路线
            node = self.route[i]
            # 因为路线全是顺时针，直接判断内角度数决定左右角
            if self.deg_balanced[node] > 180:  # 左角
                _deg = self.deg_azi[self.route[i - 1]] - self.deg_balanced[self.route[i]]
                # print(node)
                # print('left')
            elif self.deg_balanced[node] < 180:  # 右角
                _deg = self.deg_azi[self.route[i - 1]] - self.deg_balanced[self.route[i]]
                # print(node)
                # print('right')

            if _deg > 180:
                _deg = _deg - 180
            elif _deg < 180:
                _deg = _deg + 180

            while _deg > 360:
                _deg = _deg - 360
            while _deg < 0:
                _deg = _deg + 360
            self.deg_azi[node] = _deg

            if i == len(self.route) - 2:
                break
            else:
                i += 1

    def cal_pos_delta(self):
        # 推算坐标增量
        self.pos_delta = {}
        for node in self.deg_azi.keys():
            _len = self.data[node][self.route[self.route.index(node) + 1]]['S']
            _deg = math.radians(self.deg_azi[node])
            _delta = {'x': (_len * math.cos(_deg)), 'y': (_len * math.sin(_deg))}
            self.pos_delta[node] = _delta
        # print(self.pos_delta)

    def cal_pos_closingerror(self):
        # 计算坐标闭合差
        _closing_error = {'Fx': 0, 'Fy': 0, 'F': 0, 'K': 0, 'Vx': 0, 'Vy': 0}
        for node in self.pos_delta.keys():
            _closing_error['Fx'] +=  self.pos_delta[node]['x']
            _closing_error['Fy'] +=  self.pos_delta[node]['y']
        _closing_error['F'] = math.sqrt(math.pow(_closing_error['Fx'], 2) + math.pow(_closing_error['Fy'], 2))

        _len = {}
        _len_sum = 0
        i = 1
        while i < len(self.route) - 1:
            _len[self.route[i]] = self.data[self.route[i]][self.route[i + 1]]['S']
            _len_sum += _len[self.route[i]]
            i += 1
        _closing_error['K'] = _closing_error['F'] / _len_sum
        _closing_error['Vx'] = (0-_closing_error['Fx']) / _len_sum
        _closing_error['Vy'] = (0-_closing_error['Fy']) / _len_sum

        self.route_len = _len
        self.pos_closingerror = _closing_error

        # print(self.pos_closingerror)

    def balance_pos_closingerror(self):
        # 坐标闭合差平差

        self.pos_balance = {self.route[0]: self.points_known[self.route[0]],
                            self.route[1]: self.points_known[self.route[1]]}
        self.pos_balance[self.route[0]]['if_known'] = True
        self.pos_balance[self.route[1]]['if_known'] = True
        _pos_V = {}
        for node in self.route_len.keys():
            _pos_V[node] = {'x': self.route_len[node] * self.pos_closingerror['Vx'],
                            'y': self.route_len[node] * self.pos_closingerror['Vy']}
        i = 2
        while i < len(self.route) - 1:
            # print(self.route[i])
            # print(self.pos_delta[self.route[i-1]])

            self.pos_balance[self.route[i]] = {
                'x': self.pos_balance[self.route[i - 1]]['x'] + self.pos_delta[self.route[i - 1]]['x'] +
                     _pos_V[self.route[i]]['x'],
                'y': self.pos_balance[self.route[i - 1]]['y'] + self.pos_delta[self.route[i - 1]]['y'] +
                     _pos_V[self.route[i]]['y'],
                'if_known': False}
            # print(self.pos_balance[self.route[i]])
            i += 1
        self.pos_V=_pos_V
        self.pos_result = self.pos_balance
        # print(self.pos_balance)

    def calculate(self, route: str):  # 计算主流程，输入闭合导线
        self.route = route.split('-')
        self.n = len(self.route) - 2
        self.cal_deg_closingerror()
        self.cal_deg_closingerror_limited()
        self.balance_deg_closingerror()
        self.cal_deg_azimuth()
        self.cal_pos_delta()
        self.cal_pos_closingerror()
        self.balance_pos_closingerror()
    def mk_XSL(self):
        #初始化表格
        path=os.path.join(os.getcwd(),'result.xls')
        json_s=open(os.path.join(os.getcwd(),'xls_data.json'),'r',encoding='UTF-8').read()
        rb=xlrd.open_workbook(path)
        wb=xlutils.copy.copy(rb)
        ws=wb.get_sheet(0)
        xls_initdata=json.loads(json_s)
        for data in xls_initdata.keys():
            _x=int(data.split(',')[0])-1
            _y=int(data.split(',')[1])-1
            _d=xls_initdata[data]
            ws.write(_x,_y,_d)

        #写入点号以及对应数据
        for node in self.route:
            if node==self.route[0]:
                pass
            else:
                #写入点号数据
                _x=2*self.route.index(node)
                _y=0
                _d=node
                ws.write(_x,_y,_d)
                #最后一列点号
                _y=11
                ws.write(_x,_y,_d)
        #写入转折角，改正后转折角
        _route=self.route[2:len(self.route)]
        for node in _route:
            _x = 2 * _route.index(node)+4
            _y = 1
            _d = self.deg_src[node]
            ws.write(_x, _y, _d)
            _y=2
            _d=self.deg_balanced[node]
            ws.write(_x, _y, _d)
        _route=self.route[1:len(self.route)]
        #写入方向角
        print(_route)
        for node in _route:

            _x = 2 * _route.index(node)+3
            _y = 3
            _d = self.deg_azi[node]
            ws.write(_x, _y, _d)
            #写入边长
            _y=4
            _d=self.route_len[node]
            ws.write(_x, _y, _d)
            #写入坐标增量，先x再y
            _y=5
            _d=self.pos_delta[node]['x']
            ws.write(_x, _y, _d)
            _y=6
            _d=self.pos_delta[node]['y']
            ws.write(_x, _y, _d)
            #写入改正后坐标
            _y=7
            _d=self.pos_delta[node]['x']+self.pos_V[node]['x']
            ws.write(_x, _y, _d)
            _y=8
            _d=self.pos_delta[node]['y']+self.pos_V[node]['y']
            ws.write(_x, _y, _d)

            #写入结果坐标
            _x = 2 * _route.index(node)+2

            _y=9
            _d=self.pos_result[node]['x']
            ws.write(_x, _y, _d)
            _y=10
            _d=self.pos_result[node]['y']
            ws.write(_x, _y, _d)
        #最后一行方向角
        ws.write(2*(len(_route)-1)+3,3,self.deg_azi[_route[len(_route)-1]])
        #最后一行结果坐标
        #ws.write(2*(len(_route)-1)+2,9,self.pos_result[_route[len(_route)-1]]['x'])
        #ws.write(2*(len(_route)-1)+2,10,self.pos_result[_route[len(_route)-1]]['y'])
        #最后一行点号
        ws.write(2*len(self.route)-2,0,self.route[len(self.route)-1])

        #写入求和行
        ws.write(2*len(self.route),0,'∑')
        #∑β测
        _deg=0
        for deg in self.deg_src.keys():
            _deg+=self.deg_src[deg]
        ws.write(2*len(self.route),1,_deg)
        #∑β理
        ws.write(2*len(self.route),2,(self.n-2)*180)
        #∑边长
        _l=0
        for long in self. route_len.keys():
            _l+=self.route_len[long]
        ws.write(2*len(self.route),4,_l)
        #∑坐标增量
        _dx,_dy=0,0
        for node in self.pos_delta.keys():
            _dx+=self.pos_delta[node]['x']
            _dy+=self.pos_delta[node]['y']
        ws.write(2*len(self.route),5,_dx)
        ws.write(2*len(self.route),6,_dy)
        #∑改正后坐标增量
        ws.write(2*len(self.route),7,0)
        ws.write(2*len(self.route),8,0)
        #写入其他数据
        #∑β理
        ws.write(2,12,(self.n-2)*180)
        #∑β测
        ws.write(2,13,_deg)
        #ƒβ
        ws.write(2,14,_deg-(self.n-2)*180)
        #ƒβ容
        ws.write(2,15,self.deg_limited)
        #ƒx和ƒy
        ws.write(2,16,self.pos_closingerror['Fx'])
        ws.write(2,17,self.pos_closingerror['Fy'])
        #ƒ
        ws.write(2,18,self.pos_closingerror['F'])
        #K
        ws.write(2,19,self.pos_closingerror['K'])

        wb.save(path)
    def draw(self):
        _x=[]
        _y=[]
        plt.figure(figsize=(6.4,9.6))

        for node in self.route:
            _x.append(self.pos_result[node]['x'])
            _y.append(self.pos_result[node]['y'])
        #print(_x)
        #print(_y)
        for i in range(len(_x)):
            if i==0 or i==1 or i==len(_x)-1:
                plt.scatter(_y[i], _x[i],marker='^',edgecolors='red',c='w',linewidths=2)
            else:
                plt.scatter(_y[i],_x[i],marker='o',edgecolors='k',c='w',linewidths=2)
            plt.text(_y[i]+5,_x[i]+5,self.route[i])
        plt.plot(_y,_x,c='k',lw=1)
        ax = plt.gca()
        ax.set_aspect((max(_x)/max(_y))*0.15)
        ax.spines['bottom'].set_linewidth(0) ###设置坐标轴的粗细
        ax.spines['left'].set_linewidth(0)
        ax.spines['top'].set_linewidth(0)
        ax.spines['right'].set_linewidth(0)
        plt.axes().get_xaxis().set_visible(False)  # 隐藏x坐标轴
        plt.axes().get_yaxis().set_visible(False)  # 隐藏y坐标轴
        plt.savefig(os.path.join(os.getcwd(),'sketch.png'))
        plt.show()

#cta = CTA('./JFadjust_all.in2')
#cta.calculate(input('route?'))
#cta.mk_XSL()
#cta.draw()
