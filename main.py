import c
from math import exp, cos, sin, tan, pi, sqrt


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
    for P in [c.axles['weight']] * c.axles['number']:
        Sigma_res += P * exp(-1 * k * x) * (cos(k * x) + sin(k * x))
        x += c.axles['wheelbase']
    return k / (2 * u) * Sigma_res


def _M0(k):
    """钢轨弯矩"""
    Sigma_res = 0
    x = 0
    for P in [c.axles['weight']] * c.axles['number']:
        Sigma_res += P * exp(-1 * k * x) * (cos(k * x) - sin(k * x))
        x += c.axles['wheelbase']
    return 1 / (4 * k) * Sigma_res


def _R0(k):
    """枕上压力"""
    Sigma_res = 0
    x = 0
    for P in [c.axles['weight']] * c.axles['number']:
        Sigma_res += P * exp(-1 * k * x) * (cos(k * x) + sin(k * x))
        x += c.axles['wheelbase']
    return c.a * k / 2 * Sigma_res


def _alpha(v) -> list:
    """
    速度系数
    :param v: km/h
    :return:
    """
    if v < 120:
        return [0.6 * v / 100]
    elif 120 < v <= 160:
        return [0.6 * 120 / 100, 0.3 * (v - 120) / 100]
    else:
        return [0.6 * 120 / 100, 0.3 * (160 - 120) / 100, 0.3 * (v - 160) / 100]


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


def compare(S, R, text: str, unit: str):
    """S为作用效应，R为结构抗力"""
    if S <= R:
        print(f'{text}为{S}{unit}，允许{text}为{R}{unit}，故{text}满足要求。')
    else:
        print(f'{text}为{S}{unit}，允许{text}为{R}{unit}，故{text}不满足要求。')


def _sigma_z_max(Rd):
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
    if 0 <= c.h <= h1:
        return Rd / (c.b * c.e1)
    elif h1 <= c.h <= h2:
        return Rd / (2 * c.h * c.e1 * tand(c.phi))
    elif c.h > h2:
        return Rd / (4 * c.h ** 2 * tand(c.phi) ** 2)


def structure_check():
    """准静态结构强度检算"""
    # 计算刚比系数
    k1, k2 = _k(c.D1), _k(c.D2)
    # 计算最大静位移、弯矩、枕上压力
    M0 = _M0(k1)
    y0 = _y0(k1, c.D1)
    R0 = _R0(k2)
    # 计算最大动位移、弯矩、枕上压力
    Md = _Md(M0)
    yd = _yd(y0)
    Rd = _Rd(R0)
    print(f'最大位移为{yd}m。')
    # 计算锁定时的轨底、轨头应力（温度应力为零）
    sigma_bottom = Md / c.W_bottom
    sigma_top = Md / c.W_top
    sigma_bottom_lock = sigma_bottom + c.sigma_f
    sigma_top_lock = sigma_top + c.sigma_f
    sigma_s_allow = _sigma_s_allow()
    compare(sigma_bottom_lock, sigma_s_allow, '锁定时的轨底应力', 'Pa')
    compare(sigma_top_lock, sigma_s_allow, '锁定时的轨头应力', 'Pa')
    # 检算轨枕强度
    Mg = _Mg(Rd)
    Mc = _Mc(Rd)
    Mg_allow = _Mg_allow()
    Mc_allow = _Mc_allow()
    compare(Mg, Mg_allow, '轨下截面正弯矩', 'N*m')
    compare(Mc, Mc_allow, '中间截面负弯矩', 'N*m')
    # 检算道床顶面压应力
    sigma_z_max = _sigma_z_max(Rd)
    sigma_z_allow = _sigma_z_allow()
    compare(sigma_z_max, sigma_z_allow, '道床应力', 'Pa')
    # 检算路基面强度
    sigma_h = _sigma_h(Rd)
    sigma_L_allow = _sigma_L_allow()
    compare(sigma_h, sigma_L_allow, '路基应力', 'Pa')


def _sigma_d():
    """钢轨动弯应力"""
    k1, k2 = _k(c.D1), _k(c.D2)
    M0 = _M0(k1)
    Md = _Md(M0)
    sigma_bottom = Md / c.W_bottom
    sigma_top = Md / c.W_top
    return max(sigma_bottom, sigma_top)


# 无缝线路部分

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
        f_0e1 = c.f_0e
        # 比较l与l0的delta
        delta = abs(l - l0)
        print(f'l={l}m，l0={l0}m，f_0e={f_0e1}，Δ={delta}m。')
        while delta > delta_allow:
            f_0e1 = _f_0e1(f_0e1, l0, l)
            l0 = l
            l = _l(R1, f_0e1, Q)
            delta = abs(l - l0)
            print(f'l={l}m，l0={l0}m，f_0e={f_0e1}，Δ={delta}m。')
        P_N = _P_N(f_0e1, l, R1, Q)
        return _P_allow(P_N)

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
    if res > 0:
        return res
    else:
        return 0.


def _lambda_short(maxPt):
    """标准轨一端的伸缩量"""
    r = _r()
    res = (maxPt - c.P_H) * c.l_short / (2 * c.E * c.F) - r * c.l_short ** 2 / (8 * c.E * c.F)
    if res > 0:
        return res
    else:
        return 0.


def _a0(lambda_long, lambda_short, lambda_long1, lambda_short1):
    """预留轨缝"""
    a_up = c.ag - (lambda_long + lambda_short)
    a_down = lambda_long1 + lambda_short1
    print(f'a上为{a_up}m，a下为{a_down}m。')
    return (a_up + a_down) / 2


def cwr():
    """无缝线路设计"""
    # 允许温降
    td_allow = _td_allow()
    # 允许温升
    tc_allow = _tc_allow()
    # 中和轨温
    te = _te(td_allow, tc_allow)
    print(f'允许温降为{td_allow}℃，允许温升为{tc_allow}℃，中和轨温为{te}摄氏度')
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
    print(f'最大温度力：{maxPt}N。')
    # 伸缩区长度
    ls = _ls(maxPt)
    print(f'伸缩区长度：{ls}m。')
    # 从锁定轨温至最低轨温
    maxPt_0 = _Pt(te - c.t_min)
    # 长轨条一端的伸缩量
    lambda_long = _lambda_long(maxPt_0)
    # 标准轨一端的伸缩量
    lambda_short = _lambda_short(maxPt_0)
    # 从锁定轨温至最高轨温
    maxPt_1 = _Pt(c.t_max - te)
    # 长轨条一端的伸缩量
    lambda_long1 = _lambda_long(maxPt_1)
    # 标准轨一端的伸缩量
    lambda_short1 = _lambda_short(maxPt_1)
    # 预留轨缝
    a0 = _a0(lambda_long, lambda_short, lambda_long1, lambda_short1)
    print(f'预留轨缝为{a0}m。')


if __name__ == '__main__':
    structure_check()
    cwr()
