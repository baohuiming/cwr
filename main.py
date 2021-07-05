from constant import edit_constant
from math import exp, cos, sin, tan, pi, sqrt

c = None
log = ''
image = None
im = None


def logger(text):
    global log
    # print(text)
    log += text + '\n'


# 轨道结构部分

def _k(D):
    """刚比系数"""
    u = D / c.a
    return (u / (4 * c.E * c.Ix)) ** 0.25


def _y0(k, D):
    """位移"""
    u = D / c.a
    Sigma_res = 0
    x = 0
    for P in [c.axles_weight] * int(c.axles_number):
        Sigma_res += P * exp(-1 * k * x) * (cos(k * x) + sin(k * x))
        x += c.axles_wheelbase
    return k / (2 * u) * Sigma_res


def _M0(k):
    """钢轨弯矩"""
    Sigma_res = 0
    x = 0
    for P in [c.axles_weight] * int(c.axles_number):
        Sigma_res += P * exp(-1 * k * x) * (cos(k * x) - sin(k * x))
        x += c.axles_wheelbase
    return 1 / (4 * k) * Sigma_res


def _R0(k):
    """枕上压力"""
    Sigma_res = 0
    x = 0
    for P in [c.axles_weight] * int(c.axles_number):
        Sigma_res += P * exp(-1 * k * x) * (cos(k * x) + sin(k * x))
        x += c.axles_wheelbase
    return c.a * k / 2 * Sigma_res


def _alpha(v) -> list:
    """速度系数"""
    alpha_1_k = {'电力': 0.6, '内燃': 0.4}[c.traction_type]
    if v < 120:
        return [alpha_1_k * v / 100]
    elif 120 < v <= 160:
        return [alpha_1_k * 120 / 100, 0.3 * (v - 120) / 100]
    else:
        return [alpha_1_k * 120 / 100, 0.3 * (160 - 120) / 100, 0.3 * (v - 160) / 100]


def _beta(delta_h=75):
    """偏载系数，Δh单位为mm"""
    return 0.002 * delta_h


def _yd(y0):
    """最大动位移"""
    product = 1
    for alpha in _alpha(c.v):
        product *= 1 + alpha
    beta = _beta()
    return (product + beta) * y0


def _f(R):
    """根据曲线半径返回不同的横向水平力系数f"""
    if R < 300:
        return 2.00
    elif 300 <= R < 400:
        return 2.00
    elif 400 <= R < 500:
        return 1.80
    elif 500 <= R < 600:
        return 1.70
    elif 600 <= R < 800:
        return 1.60
    elif 800 <= R < 12000:  # 曲线半径大于12000米视为直线
        return 1.45
    else:
        return 1.25


def _Md(M0):
    """最大动弯矩"""
    product = 1
    for alpha in _alpha(c.v):
        product *= 1 + alpha
    beta = _beta()
    f = _f(c.R)
    return (product + beta) * f * M0


def _Rd(R0):
    """动载下最大枕上压力"""
    product = 1
    for alpha in _alpha(c.v):
        product *= 1 + alpha
    beta = _beta()
    return (product + beta) * R0


def _K():
    """新轨k取1.3，再用轨取1.35"""
    if c.life_type == '新轨':
        return 1.3
    elif c.life_type == '再用轨':
        return 1.35


def _sigma_s_allow():
    """钢轨容许应力"""
    return c.sigma_s / _K()


def _sigma_z_allow():
    """碎石道床=0.5MPa，卵石道床=0.4MPa"""
    if c.bed_type == '碎石':
        return 0.5e6
    elif c.bed_type == '卵石':
        return 0.4e6


def _sigma_L_allow():
    """新建砂黏土路基=0.13MPa，既有砂黏土路基=0.15MPa"""
    if c.soil_type == '新建砂黏土':
        return 0.13e6
    elif c.soil_type == '既有砂黏土':
        return 0.15e6


def _Mg(Rd):
    """轨下截面正弯矩"""
    Ks = 1
    return Ks * (c.a1 ** 2 / (2 * c.e) - c.b1 / 8) * Rd


def _Mc(Rd):
    """中间截面负弯矩"""
    Ks = 1
    return -1 * (Ks * (3 * c.l ** 2 + 4 * c.e ** 2 - 8 * c.a1 * c.e - 12 * c.a1 * c.l)) / (4 * (3 * c.l + 2 * c.e)) * Rd


def _Mg_allow():
    """与轨枕类型相关"""
    if c.sleeper_type == 1:
        return 11.9e3
    elif c.sleeper_type == 2:
        return 13.3e3
    elif c.sleeper_type == 3:
        return 18e3


def _Mc_allow():
    """与轨枕类型相关"""
    if c.sleeper_type == 1:
        return 8.8e3
    elif c.sleeper_type == 2:
        return 10.5e3
    elif c.sleeper_type == 3:
        return 14e3


def compare(S, R, text: str, unit: str, rate: float = 0.):
    """S为作用效应，R为结构抗力"""
    _S = '%.3f' % (S * 10 ** rate)
    _R = '%.3f' % (R * 10 ** rate)
    if S <= R:
        logger(f'{text}为{_S}{unit}，允许{text}为{_R}{unit}，故{text}满足要求。')
    else:
        logger(f'【警告】{text}为{_S}{unit}，允许{text}为{_R}{unit}，故{text}不满足要求！')


def _sigma_z_max(Rd):
    """道床顶面最大压应力"""
    m = 1.6  # 应力分布不均匀系数
    return m * Rd / (c.b * c.e1)


def _sigma_h(Rd):
    """道床顶面应力"""

    def cotd(degree):
        degree = degree / 180 * pi
        return 1 / tan(degree)

    def tand(degree):
        degree = degree / 180 * pi
        return tan(degree)

    h1 = c.b / 2 * cotd(c.phi)
    h2 = c.e1 / 2 * cotd(c.phi)
    logger('h1=%.3fm,h2=%.3fm' % (h1, h2))
    if 0 <= c.h < h1:
        logger('0≤h<h1')
        return Rd / (c.b * c.e1)
    elif h1 <= c.h <= h2:
        logger('h1≤h≤h2')
        return Rd / (2 * c.h * c.e1 * tand(c.phi))
    elif c.h > h2:
        logger('h>h2')
        return Rd / (4 * c.h ** 2 * tand(c.phi) ** 2)


def structure_check():
    """准静态结构强度检算"""
    logger('——计算位移、弯矩、枕上压力——')
    # 计算刚比系数
    k1, k2 = _k(c.D1), _k(c.D2)
    logger('刚比系数k1=%.4fm^-1，k2=%.4fm^-1。' % (k1, k2))
    # 计算最大静位移、弯矩、枕上压力
    M0 = _M0(k1)
    y0 = _y0(k1, c.D1)
    R0 = _R0(k2)
    logger('最大静位移、弯矩、枕上压力为：y0={:.3f}mm,M0={:.3f}kN*m,R0={:.3f}kN'.format(y0 * 1000, M0 * 0.001, R0 * 0.001))
    # 计算最大动位移、弯矩、枕上压力
    Md = _Md(M0)
    yd = _yd(y0)
    Rd = _Rd(R0)
    logger('最大动位移、弯矩、枕上压力为：yd={:.3f}mm,Md={:.3f}kN*m,Rd={:.3f}kN'.format(yd * 1000, Md * 0.001, Rd * 0.001))
    # 计算锁定时的轨底、轨头应力（温度应力为零）
    sigma_bottom = Md / c.W_bottom
    sigma_top = Md / c.W_top
    sigma_bottom_lock = sigma_bottom + c.sigma_f
    sigma_top_lock = sigma_top + c.sigma_f
    sigma_s_allow = _sigma_s_allow()
    logger('\n——轨道强度检算——')
    compare(sigma_bottom_lock, sigma_s_allow, '锁定时的轨底应力', 'MPa', -6)
    compare(sigma_top_lock, sigma_s_allow, '锁定时的轨头应力', 'MPa', -6)
    # 检算轨枕强度
    Mg = _Mg(Rd)
    Mc = _Mc(Rd)
    Mg_allow = _Mg_allow()
    Mc_allow = _Mc_allow()
    compare(Mg, Mg_allow, '轨下截面正弯矩', 'kN·m', -3)
    compare(Mc, Mc_allow, '中间截面负弯矩', 'kN·m', -3)
    # 检算道床顶面压应力
    sigma_z_max = _sigma_z_max(Rd)
    sigma_z_allow = _sigma_z_allow()
    compare(sigma_z_max, sigma_z_allow, '道床应力', 'MPa', -6)
    # 检算路基面强度
    sigma_h = _sigma_h(Rd)
    sigma_L_allow = _sigma_L_allow()
    compare(sigma_h, sigma_L_allow, '路基应力', 'MPa', -6)


# 无缝线路部分

def _sigma_d():
    """钢轨动弯应力"""
    k1, k2 = _k(c.D1), _k(c.D2)
    M0 = _M0(k1)
    Md = _Md(M0)
    sigma_bottom = Md / c.W_bottom
    return sigma_bottom


def _td_allow():
    """允许降温幅度"""
    sigma_s_allow = _sigma_s_allow()
    sigma_d = _sigma_d()
    return (sigma_s_allow - sigma_d - c.sigma_f) / (c.E * c.alpha)


def _Q():
    """等效道床横向阻力"""
    return {
        1760: {0.3: 7600, 0.4: 8400},
        1840: {0.3: 7900, 0.4: 8700},
    }[c.n][c.b2]


def _tc_allow():
    """允许升温幅度"""

    def _P_allow(delta_allow: float = 1 / 1000) -> float:
        """最大温度压力，根据统一公式计算，delta为误差，默认为1/1000"""

        def _R1():
            """变形曲率1/R1"""
            R0 = c.l0 ** 2 / (8 * c.f_0p)
            R1 = 1 / (1 / R0 + 1 / c.R)
            return R1

        def _l(R1, f_0e, Q):
            """曲线变形弦长l"""
            l_square = 1 / Q * (2 * pi ** 2 * c.E * c.Iy / R1 +
                                sqrt((2 * pi ** 2 * c.E * c.Iy / R1) ** 2 + pi ** 5 * c.E * c.Iy / 2 * (c.f + f_0e) * Q)
                                )
            return sqrt(l_square)

        def _f_0e1(f_0e, l0, l):
            """重新计算矢度"""
            return l ** 2 * f_0e / l0 ** 2

        def _P_N(f_0e, l, R1, Q):
            """温度力"""
            return (pi ** 5 * c.E * c.Iy * (c.f + f_0e) / (2 * l ** 4) + Q) / (
                    (c.f + f_0e) * pi ** 3 / (4 * l ** 2) + 1 / R1)

        def _P_allow(P_N):
            """允许温度压力"""
            return P_N / 1.3

        # 求得变形曲率1/R1
        R1 = _R1()
        # 获得道床横向等效阻力
        Q = _Q()
        # 求得变形曲线弦长l
        l = _l(R1=R1, f_0e=c.f_0e, Q=Q)
        l0 = c.l0
        i = 1
        f_0e1 = c.f_0e
        # 比较l与l0的delta
        delta = abs(l - l0)
        logger('\n——计算变形曲线弦长——')
        logger(f'第{i}次迭代：l={l}m，l0={l0}m，f_0e={f_0e1}m，Δ={delta}m。')
        while delta > delta_allow:
            i += 1
            f_0e1 = _f_0e1(f_0e1, l0, l)
            l0 = l
            l = _l(R1, f_0e1, Q)
            delta = abs(l - l0)
            logger(f'第{i}次迭代：l={l}m，l0={l0}m，f_0e={f_0e1}m，Δ={delta}m。')
        P_N = _P_N(f_0e1, l, R1, Q)
        res = _P_allow(P_N)
        logger('故变形曲线弦长为%.3fm，允许温度力为%.3fkN。' % (l, res / 1000))
        return res

    Pf = 0  # 附加压力为零
    P_allow = _P_allow()
    return (P_allow - 2 * Pf) / (2 * c.E * c.F * c.alpha)


def _te(td, tc):
    """设计锁定轨温"""
    return (c.t_max + c.t_min) / 2 + (td - tc) / 2 + c.tk


def _tn(te):
    return te - 5


def _tm(te):
    return te + 5


def _Pt(delta_t):
    """温度力"""
    sigma = c.E * c.alpha * delta_t
    return sigma * c.F


def _r():
    """道床纵向阻力"""
    return {
        1: {
            1760: 8700,
            1840: 9100,
        },
        2: {
            1760: 10900,
            1840: 11500,
        },
        3: {
            1667: 15200,
            1760: 16000,
        }
    }[c.sleeper_type][c.n]


def _ls(maxPt):
    """伸缩区长度"""
    r = _r()
    return (maxPt - c.P_H) / r


def _lambda_long(maxPt):
    """长轨条一端的伸缩量"""
    r = _r()
    res = (maxPt - c.P_H) ** 2 / (2 * c.E * c.F * r)
    if maxPt - c.P_H > 0:
        return res
    else:
        return 0.


def _lambda_short(maxPt):
    """标准轨一端的伸缩量"""
    r = _r()
    res = (maxPt - c.P_H) * c.l_short / (2 * c.E * c.F) - r * c.l_short ** 2 / (8 * c.E * c.F)
    if maxPt - c.P_H > 0:
        if (maxPt - c.P_H) < (r * c.l_short / 2):
            """当温度力小于纵向阻力r×l/2时，当成长轨计算"""
            return _lambda_long(maxPt)
        else:
            return res
    else:
        return 0.


def _a0(lambda_long, lambda_short, lambda_long1, lambda_short1):
    """预留轨缝"""
    a_up = c.ag - (lambda_long + lambda_short)
    a_down = lambda_long1 + lambda_short1
    logger('a上为%.3fmm，a下为%.3fm。' % (a_up * 1000, a_down * 1000))
    return (a_up + a_down) / 2


def cwr():
    """无缝线路设计"""
    # 允许温降
    td_allow = _td_allow()
    # 允许温升
    tc_allow = _tc_allow()
    # 中和轨温
    te = _te(td_allow, tc_allow)
    logger('\n——无缝线路强度、稳定性检算——')
    logger('允许温降为%.3f℃，允许温升为%.3f℃，中和轨温为%.3f℃。' % (td_allow, tc_allow, te))
    # 施工锁定轨温上、下限
    tm, tn = _tm(te), _tn(te)
    # 实际温降、温升
    td = tm - c.t_min
    tc = c.t_max - tn
    # 检核
    compare(td, td_allow, '温降', '℃')
    compare(tc, tc_allow, '温升', '℃')
    # 最大温度力
    maxPt = _Pt(max(td, tc))
    logger('\n——伸缩区长度计算——')
    logger('最大温度力：%.3fkN。' % (maxPt * 0.001))
    # 伸缩区长度
    ls = _ls(maxPt)
    logger('伸缩区长度：%.3fm。' % ls)
    # 从锁定轨温至最低轨温
    logger('\n——预留轨缝计算——')
    X, y = [], []
    for delta_t in range(-5, 6):
        te0 = int(te + delta_t)
        logger(f'从锁定轨温t={te0}℃至最低轨温时：')
        maxPt_0 = _Pt(te0 - c.t_min)
        logger('    最大温度力：%.3fkN。' % (maxPt_0 * 0.001))
        # 长轨条一端的伸缩量
        lambda_long = _lambda_long(maxPt_0)
        # 标准轨一端的伸缩量
        lambda_short = _lambda_short(maxPt_0)
        logger('    长轨条一端的缩短量为%.3fmm,标准轨一端的缩短量为%.3fmm。' % (lambda_long * 1000, lambda_short * 1000))
        # 从锁定轨温至最高轨温
        logger(f'从锁定轨温t={te0}℃至最高轨温时：')
        maxPt_1 = _Pt(c.t_max - te0)
        logger('    最大温度力：%.3fkN。' % (maxPt_1 * 0.001))
        # 长轨条一端的伸缩量
        lambda_long1 = _lambda_long(maxPt_1)
        # 标准轨一端的伸缩量
        lambda_short1 = _lambda_short(maxPt_1)
        logger('    长轨条一端的伸长量为%.3fmm,标准轨一端的伸长量为%.3fmm。' % (lambda_long1 * 1000, lambda_short1 * 1000))
        # 预留轨缝
        a0 = _a0(lambda_long, lambda_short, lambda_long1, lambda_short1)
        if lambda_long + lambda_short > 18e-3:
            logger('【警告】长短轨的缩短量之和大于构造轨缝ag=18mm，不适合铺设无缝线路！\n')
        elif a0 <= 0:
            logger('【警告】计算预留轨缝不大于0，不适合铺设无缝线路！\n')
        else:
            logger('故预留轨缝为%.3fmm，取整数为%dmm。\n' % (a0 * 1000, round(a0 * 1000)))
            X.append(te0)
            y.append(round(a0 * 1000))
    return X, y


def show_result():
    """展示结果"""
    # 初始化
    import tkinter as tk
    from PIL import Image
    from PIL import ImageTk
    global image, im
    window = tk.Toplevel()
    window.title('结果')
    # 文本框
    txt = tk.Text(window, width=120, height=39, font=('微软雅黑', 12,))
    txt.insert('insert', log)
    txt.grid(row=0, column=0, padx=3, pady=3)
    # 图片框
    image = Image.open("result/te-a0.jpg")
    w_, h_ = image.size
    im = ImageTk.PhotoImage(image)
    canvas = tk.Canvas(window, height=h_, width=w_)
    canvas.create_image(w_ / 2, h_ / 2, image=im)
    canvas.grid(row=0, column=1)
    # 主窗口循环显示
    window.mainloop()


def draw(X, y, save: bool = True, filename: str = 'result/te-a0.jpg'):
    """画出结果图"""
    from clipboard import paste_img
    import matplotlib.pyplot as plt
    from matplotlib.pyplot import MultipleLocator
    from matplotlib.font_manager import FontProperties  # 字体管理器

    # 设置汉字格式
    font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=15)
    plt.plot(X, y, marker='x')
    # 标题
    plt.xlabel('锁定轨温$t_e$/℃', fontproperties=font)
    plt.ylabel('预留轨缝$a_0$/mm', fontproperties=font)
    # 坐标轴刻度
    x_major_locator = MultipleLocator(1)
    # 把x轴的刻度间隔设置为1，并存在变量里
    y_major_locator = MultipleLocator(1)
    # 把y轴的刻度间隔设置为1，并存在变量里
    ax = plt.gca()
    # ax为两条坐标轴的实例
    ax.xaxis.set_major_locator(x_major_locator)
    # 把x轴的主刻度设置为1的倍数
    ax.yaxis.set_major_locator(y_major_locator)
    # 把y轴的主刻度设置为1的倍数
    if save:
        # 保存图片
        plt.savefig(filename)
        # 将图片复制到剪贴板中
        paste_img(filename)


def draws(Xs, ys, labels: list, save: bool = True, filename: str = 'te-a0.jpg'):
    """画出结果图"""
    from clipboard import paste_img
    import matplotlib.pyplot as plt
    from matplotlib.pyplot import MultipleLocator
    from matplotlib.font_manager import FontProperties  # 字体管理器

    def random_color():
        """生成随机颜色"""
        import random
        colorArr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        color = ""
        for i in range(6):
            color += colorArr[random.randint(0, 14)]
        return "#" + color

    # 设置汉字格式
    font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=15)
    # 设置图像大小
    plt.figure(figsize=(16, 10))

    print(Xs, ys)

    l = []
    for i in range(len(Xs)):
        l.append(tuple(plt.plot(Xs[i], ys[i], marker='x', color=random_color())))
    plt.legend(handles=l, labels=labels, prop=font, ncol=2)

    # 标题
    plt.xlabel('锁定轨温$t_e$/℃', fontproperties=font)
    plt.ylabel('预留轨缝$a_0$/mm', fontproperties=font)
    # 坐标轴刻度
    x_major_locator = MultipleLocator(1)
    # 把x轴的刻度间隔设置为1，并存在变量里
    y_major_locator = MultipleLocator(1)
    # 把y轴的刻度间隔设置为1，并存在变量里
    ax = plt.gca()
    # ax为两条坐标轴的实例
    ax.xaxis.set_major_locator(x_major_locator)
    # 把x轴的主刻度设置为1的倍数
    ax.yaxis.set_major_locator(y_major_locator)
    # 把y轴的主刻度设置为10的倍数
    if save:
        # 保存图片
        plt.savefig(filename)
        # 将图片复制到剪贴板中
        paste_img(filename)


def draw_citys(citys: str = '哈尔滨、乌鲁木齐、沈阳、北京、青岛、敦煌、郑州、武汉、绵阳、南昌、南京、福州、拉萨、昆明、广州'):
    """不同城市"""
    global c
    Xs, ys = [], []
    citys = citys.split('、')
    for city in citys:
        c = edit_constant(_city=city)
        structure_check()
        X, y = cwr()
        Xs.append(X)
        ys.append(y)
    draws(Xs, ys, citys, filename='result/te-a0-citys.jpg')


def draw_Rs(Rs: str = '2000、2500、3000、3500、4000、4500、5000'):
    """不同曲线半径"""
    global c
    Xs, ys = [], []
    Rs = Rs.split('、')
    for _R in Rs:
        c = edit_constant(_param={'name': 'R', 'value': _R})
        structure_check()
        X, y = cwr()
        Xs.append(X)
        ys.append(y)
    draws(Xs, ys, Rs, filename='result/te-a0-Rs.jpg')


def draw_hs(hs: str = '0.2、0.3、0.4、0.5、0.6'):
    """不同道床厚度"""
    global c
    Xs, ys = [], []
    hs = hs.split('、')
    for _h in hs:
        c = edit_constant(_param={'name': 'h', 'value': _h})
        structure_check()
        X, y = cwr()
        Xs.append(X)
        ys.append(y)
    draws(Xs, ys, hs, filename='result/te-a0-hs.jpg')


def draw_f_0ps(f_0ps: str = '0.001、0.0015、0.002、0.0025、0.003'):
    """不同塑性初始弯曲"""
    global c
    Xs, ys = [], []
    f_0ps = f_0ps.split('、')
    for _f_0p in f_0ps:
        c = edit_constant(_param={'name': 'f_0p', 'value': _f_0p})
        structure_check()
        X, y = cwr()
        Xs.append(X)
        ys.append(y)
    draws(Xs, ys, f_0ps, filename='result/te-a0-f_0ps.jpg')


def draw_axles_weights(axles_weights: str = '70000、80000、90000、100000、112800、150000、200000'):
    """不同轴重"""
    global c
    Xs, ys = [], []
    axles_weights = axles_weights.split('、')
    for _axles_weight in axles_weights:
        c = edit_constant(_param={'name': 'axles_weight', 'value': _axles_weight})
        structure_check()
        X, y = cwr()
        Xs.append(X)
        ys.append(y)
    draws(Xs, ys, axles_weights, filename='result/te-a0-axles_weights.jpg')


def draw_axles_wheelbases(axles_wheelbases: str = '1、2、3、4、5'):
    """不同轴距"""
    global c
    Xs, ys = [], []
    axles_wheelbases = axles_wheelbases.split('、')
    for _axles_wheelbase in axles_wheelbases:
        c = edit_constant(_param={'name': 'axles_wheelbase', 'value': _axles_wheelbase})
        structure_check()
        X, y = cwr()
        Xs.append(X)
        ys.append(y)
    draws(Xs, ys, axles_wheelbases, filename='result/te-a0-axles_wheelbases.jpg')


def draw_axles_numbers(axles_numbers: str = '1、2、3、4、5'):
    """不同轴数量"""
    global c
    Xs, ys = [], []
    axles_numbers = axles_numbers.split('、')
    for _axles_number in axles_numbers:
        c = edit_constant(_param={'name': 'axles_number', 'value': _axles_number})
        structure_check()
        X, y = cwr()
        Xs.append(X)
        ys.append(y)
    draws(Xs, ys, axles_numbers, filename='result/te-a0-axles_numbers.jpg')


def draw_l_shorts(l_shorts: str = '12.5、25、50、100、250、500'):
    """不同标准轨长度"""
    global c
    Xs, ys = [], []
    l_shorts = l_shorts.split('、')
    for _l_short in l_shorts:
        c = edit_constant(_param={'name': 'l_short', 'value': _l_short})
        structure_check()
        X, y = cwr()
        Xs.append(X)
        ys.append(y)
    draws(Xs, ys, l_shorts, filename='result/te-a0-l_shorts.jpg')


def draw_b2s(b2s: str = '0.3、0.4'):
    """不同道砟肩宽"""
    global c
    Xs, ys = [], []
    b2s = b2s.split('、')
    for _b2 in b2s:
        c = edit_constant(_param={'name': 'b2', 'value': _b2})
        structure_check()
        X, y = cwr()
        Xs.append(X)
        ys.append(y)
    draws(Xs, ys, b2s, filename='result/te-a0-b2s.jpg')


def draw_all():
    """画出所有不同参数的图"""
    draw_axles_numbers()
    draw_axles_weights()
    draw_axles_wheelbases()
    draw_b2s()
    draw_f_0ps()
    draw_hs()
    draw_l_shorts()
    draw_Rs()
    draw_citys()


def main():
    global c
    c = edit_constant()
    structure_check()
    X, y = cwr()
    draw(X, y, )
    show_result()


if __name__ == '__main__':
    main()
