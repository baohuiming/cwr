# coding = utf-8
# constants
# 采用国际单位制单位（Pa,m,s,kg）

# default list
# 轨道部分
E = 2.1e11  # 钢轨弹性模量
sigma_s = 457e6  # 钢轨屈服强度
Ix = 32170000e-12  # 钢轨对水平轴惯性矩
Iy = 5240000e-12  # 钢轨对垂直轴惯性矩
F = 77.45e-4  # 钢轨断面面积
W_bottom = 396000e-9  # 轨底抗弯模量
W_top = 339400e-9  # 轨头抗弯模量
D1 = 33e6  # 检算钢轨时的钢轨支座刚度
D2 = 72e6  # 检算轨下基础时的钢轨支座刚度
l = 2.6  # 轨枕长度
a1 = 0.50  # 荷载作用点至轨端距离
e = 0.95  # 一股钢轨下轨枕的全支承长度
b1 = 0.150  # 轨底宽
b = 0.275  # 轨枕底面宽度
h = 0.45  # 道床厚度
n = 1760  # 每公里铺设根数
a = 0.5682  # 轨枕间距
life_type = '新轨'  # 钢轨类型
bed_type = '碎石'  # 道床类型
soil_type = '新建砂黏土'  # 路基类型
sleeper_type = 3  # 轨枕类型，Ⅲ型轨枕
phi = 35  # 压力扩散角度φ，一般为35°
b2 = 0.40  # 道床肩宽
P_H = 570e3  # 接头阻力

# 车辆及线路部分
v = 160  # 速度
R = 2000  # 最小曲线半径
axles_weight = 112.8e3  # 轴重
axles_wheelbase = 2  # 轴距
axles_number = 3  # 轴数
l0 = 4.0  # 弹性初始弯曲半波长，通常取4.0m
f = 0.2e-2  # 容许弯曲矢度
f_0e = 0.3e-2  # 弹性初始弯曲矢度
f_0p = 0.3e-2  # 塑性初始弯曲矢度
l_short = 50  # 标准轨长度
ag = 18e-3  # 构造轨缝

# 温度部分
t_max = 59.1  # 最高轨温
t_min = 0.0  # 最低轨温
alpha = 11.8e-6  # 钢轨线膨胀系数
tk = 0  # 设计锁定轨温修正值，取0~5

# 其他部分
sigma_f = 10e6  # 制动应力取10MPa

e1 = 3 / 8 * l + e / 4  # 一股钢轨作用下的轨枕有效支承长度


# 读取变量
def load_csv(filename: str = 'c.csv') -> list:
    with open(filename, encoding='utf-8') as f:
        data = f.read().strip()
    data = data.split('\n')
    data = [row.split(',') for row in data]
    return data


def show_window():
    # 初始化
    import tkinter as tk
    from math import ceil

    def set_default():
        """给文本框赋值"""
        for idx, row in enumerate(data):
            entrys[idx].delete(0, tk.END)
            entrys[idx].insert(1, data[idx][1])

    def confirm():
        window.quit()

    def cancel():
        quit()

    data = load_csv()
    window = tk.Tk()
    window.title('Ⅲ型轨枕无缝线路设计器 作者：鲍慧明')
    padx, pady = 10, 1
    ft = ("新宋体", "14", "bold")
    # table head
    tk.Label(window, text="符号", font=ft).grid(row=0, column=0, padx=padx, pady=pady)
    tk.Label(window, text="数值", font=ft).grid(row=0, column=1, padx=padx, pady=pady)
    tk.Label(window, text="解释", font=ft).grid(row=0, column=2, padx=padx, pady=pady)
    tk.Label(window, text="符号", font=ft).grid(row=0, column=3, padx=padx, pady=pady)
    tk.Label(window, text="数值", font=ft).grid(row=0, column=4, padx=padx, pady=pady)
    tk.Label(window, text="解释", font=ft).grid(row=0, column=5, padx=padx, pady=pady)
    _l1_ = ceil(len(data) / 2)
    entrys = []
    for idx, row in enumerate(data[:_l1_]):
        tk.Label(window, text=row[0]).grid(row=idx + 1, column=0, padx=padx, pady=pady)
        entrys.append(tk.Entry(window))
        entrys[-1].grid(row=idx + 1, column=1, padx=padx, pady=pady)
        tk.Label(window, text=row[2]).grid(row=idx + 1, column=2, padx=padx, pady=pady)
    for idx, row in enumerate(data[_l1_:]):
        tk.Label(window, text=row[0]).grid(row=idx + 1, column=3, padx=padx, pady=pady)
        entrys.append(tk.Entry(window))
        entrys[-1].grid(row=idx + 1, column=4, padx=padx, pady=pady)
        tk.Label(window, text=row[2]).grid(row=idx + 1, column=5, padx=padx, pady=pady)
    # 给文本框赋值
    set_default()

    # 确认、取消、恢复默认按钮
    btn_confirm = tk.Button(window, text='计算', command=confirm)
    btn_cancel = tk.Button(window, text='取消', command=cancel)
    btn_default = tk.Button(window, text='默认', command=set_default)
    btn_confirm.grid(row=len(data) + 1, column=2, ipadx=30, pady=5)
    btn_cancel.grid(row=len(data) + 1, column=3, ipadx=30, pady=5)
    btn_default.grid(row=len(data) + 1, column=4, ipadx=30, pady=5)

    # 主窗口循环显示
    window.mainloop()


show_window()
