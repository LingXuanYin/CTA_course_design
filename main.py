import math


class CTA():
    def __init__(self):
        self.data, self.points_known = self.Data_read('./JFadjust_all.in2')
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

    def cal_deg_closedifference(self):
        # 计算角度闭合差
        _r = [self.route[len(self.route) - 2]] + self.route[1:]
        i = 1
        _deg = 0
        sum_closedeg = 0
        while i < len(self.route) - 1:
            r = _r[i]
            _deg = self.data[r][_r[i - 1]]['L'] - self.data[r][_r[i + 1]]['L']
            if _deg < 0:
                _deg += 360
            self.deg_src[r] = _deg
            sum_closedeg += _deg
            i += 1
        _dif = sum_closedeg - (self.n - 2) * 180
        self.deg_closedifference = _dif
        # print(_dif)
        return _dif

    def cal_deg_closedifference_limited(self):
        # 计算角度闭合差限差
        _lim = int(40 * math.sqrt(self.n)) / 10000
        _lim = self.ang_dec(str(_lim))

        self.deg_limited = _lim
        if self.deg_closedifference > self.deg_limited:
            self.deg_over_limited = True
        else:
            self.deg_over_limited = False
        return self.deg_limited

    def balance_deg_closedifference(self):
        # 角度闭合差平差
        _dif = self.deg_closedifference
        bal_V = (0 - _dif) / self.n
        for deg in self.deg_src.keys():
            self.deg_balanced[deg] = self.deg_src[deg] + bal_V
        return self.deg_balanced

    def cal_deg_azimuth(self):
        # 通过已知点计算后视导线的方位角
        p1 = self.points_known[self.route[0]]
        p2 = self.points_known[self.route[1]]
        _deg_azi_backview = math.atan((p2['y'] - p1['y']) / (p2['x'] - p1['x']))
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
            _deg = self.deg_azi_backview + _d + 180
        while _deg > 360:
            _deg = _deg - 360
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
                print(node)
                print('left')
            elif self.deg_balanced[node] < 180:  # 右角
                _deg = self.deg_azi[self.route[i - 1]] - self.deg_balanced[self.route[i]]
                print(node)
                print('right')

            if _deg > 180:
                _deg = _deg - 180
            elif _deg < 180:
                _deg = _deg + 180

            while _deg > 360:
                _deg = _deg - 360
            print(_deg)

            self.deg_azi[node] = _deg

            if i == len(self.route) - 2:
                break
            else:
                i += 1
        # print(self.deg_azi)

    def calculate(self, route: str):  # 计算主流程，输入闭合导线
        self.route = route.split('-')
        self.n = len(self.route) - 2
        self.cal_deg_closedifference()
        self.cal_deg_closedifference_limited()
        self.balance_deg_closedifference()
        self.cal_deg_azimuth()


if __name__ == '__main__':
    cta = CTA()
    cta.calculate(input('输入路线'))
    # print(cta.deg_balanced)
