# coding = utf-8
# constants
# 采用国际单位制单位（Pa,m,s,kg）

constants_dict = {}
constants = None


class Dict2Obj(dict):
    def __init__(self, *args, **kwargs):
        super(Dict2Obj, self).__init__(*args, **kwargs)
        self['e1'] = 3 / 8 * self['l'] + self['e'] / 4  # 一股钢轨作用下的轨枕有效支承长度

    def __getattr__(self, key):
        value = self[key]
        if isinstance(value, dict):
            value = Dict2Obj(value)
        return value


# 读取变量
def load_csv(filename: str = 'c.csv') -> list:
    with open(filename, encoding='utf-8') as f:
        data = f.read().strip()
    data = data.split('\n')
    data = [row.split(',') for row in data]
    return data


def show_window(_city: str = None):
    # 初始化
    import tkinter as tk
    from math import ceil

    def set_default():
        """给文本框赋值"""
        for idx, row in enumerate(data):
            entrys[idx].delete(0, tk.END)
            entrys[idx].insert(1, data[idx][1])

    def query():
        """查气温"""
        global T
        from temperature import get_temperature_by_city
        T = get_temperature_by_city(city.get())
        # 填入
        T_MIN.config(text='最低气温：%s℃' % T['min'])
        T_MAX.config(text='最高气温：%s℃' % T['max'])

    def entry():
        """填入轨温"""
        for idx, row in enumerate(data):
            if row[0] == 't_min':
                entrys[idx].delete(0, tk.END)
                entrys[idx].insert(1, T_MIN.cget('text')[5:-1])
            elif row[0] == 't_max':
                entrys[idx].delete(0, tk.END)
                entrys[idx].insert(1, float(T_MAX.cget('text')[5:-1]) + 20)

    def confirm():
        """计算按钮操作"""
        # 冻结编辑框
        for entry in entrys:
            entry.config(state='readonly')
        # 销毁按钮
        btn_confirm.destroy()
        btn_cancel.destroy()
        btn_default.destroy()
        get_constants()
        window.quit()

    def cancel():
        """退出程序"""
        quit()

    def get_constants():
        """获取常量"""
        global constants_dict, constants
        for idx, row in enumerate(data):
            key = row[0]
            val = entrys[idx].get()
            try:
                val = float(val)
            except:
                pass
            constants_dict.update({key: val})
        constants = Dict2Obj(constants_dict)

    data = load_csv()
    window = tk.Tk()
    window.title('Ⅲ型轨枕无缝线路设计器 作者：鲍慧明')
    padx, pady = 10, 1
    ft = ("新宋体", "14", "bold")
    # 查轨温
    tk.Label(window, text="城市：").grid(row=0, column=0, padx=padx, pady=pady)
    city = tk.Entry(window)
    city.insert(0, '珠海')
    city.grid(row=0, column=1)
    T_MIN = tk.Label(window, text="最低气温：0.0℃")
    T_MIN.grid(row=0, column=3, padx=padx, pady=pady)
    T_MAX = tk.Label(window, text="最高气温：39.1℃")
    T_MAX.grid(row=0, column=4, padx=padx, pady=pady)
    # table head
    tk.Label(window, text="符号", font=ft).grid(row=1, column=0, padx=padx, pady=pady)
    tk.Label(window, text="数值", font=ft).grid(row=1, column=1, padx=padx, pady=pady)
    tk.Label(window, text="解释", font=ft).grid(row=1, column=2, padx=padx, pady=pady)
    tk.Label(window, text="符号", font=ft).grid(row=1, column=3, padx=padx, pady=pady)
    tk.Label(window, text="数值", font=ft).grid(row=1, column=4, padx=padx, pady=pady)
    tk.Label(window, text="解释", font=ft).grid(row=1, column=5, padx=padx, pady=pady)
    _l1_ = ceil(len(data) / 2)
    entrys = []
    for idx, row in enumerate(data[:_l1_]):
        tk.Label(window, text=row[0]).grid(row=idx + 2, column=0, padx=padx, pady=pady)
        entrys.append(tk.Entry(window))
        entrys[-1].grid(row=idx + 2, column=1, padx=padx, pady=pady)
        tk.Label(window, text=row[2]).grid(row=idx + 2, column=2, padx=padx, pady=pady)
    for idx, row in enumerate(data[_l1_:]):
        tk.Label(window, text=row[0]).grid(row=idx + 2, column=3, padx=padx, pady=pady)
        entrys.append(tk.Entry(window))
        entrys[-1].grid(row=idx + 2, column=4, padx=padx, pady=pady)
        tk.Label(window, text=row[2]).grid(row=idx + 2, column=5, padx=padx, pady=pady)
    # 给文本框赋值
    set_default()

    # 查气温、填入轨温、确认、取消、恢复默认按钮
    btn_query = tk.Button(window, text='查气温', command=query)
    btn_entry = tk.Button(window, text='填入轨温', command=entry)
    btn_confirm = tk.Button(window, text='计算', command=confirm)
    btn_cancel = tk.Button(window, text='取消', command=cancel)
    btn_default = tk.Button(window, text='默认', command=set_default)
    btn_query.grid(row=0, column=2, ipadx=30, pady=5)
    btn_entry.grid(row=0, column=5, ipadx=30, pady=5)
    btn_confirm.grid(row=len(data) + 1, column=2, ipadx=30, pady=5)
    btn_cancel.grid(row=len(data) + 1, column=3, ipadx=30, pady=5)
    btn_default.grid(row=len(data) + 1, column=4, ipadx=30, pady=5)

    if _city:
        # 如果指定了城市
        # 切换城市
        city.delete(0, tk.END)
        city.insert(0, _city)
        # 查轨温
        query()
        # 填入轨温
        entry()
        # 计算
        confirm()
    else:
        # 主窗口循环显示
        window.mainloop()


def edit_constant(city: str = None):
    show_window(city)
    return constants
