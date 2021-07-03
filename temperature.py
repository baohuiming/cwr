# coding = utf8

def get_id_by_name(cityname: str) -> int:
    """
    输入城市的名字，返回对应的站点id
    """
    # 读取csv
    with open('station-name.csv') as f:
        data = f.read()

    data = data.split('\n')
    for row in data:
        if cityname in row:
            return int(row[:5])


def get_province_capital_by_city(cityname: str) -> str:
    """
    输入城市的名字，返回省会名字
    """
    from city import provinces
    for province in provinces:
        citys = province['city']
        for city in citys:
            if cityname in city['name'].replace('市', ''):
                return citys[0]['name'].replace('市', '')


def get_temperature_by_city(cityname: str) -> dict:
    """
    获取某城市自2000年来的最高温度和最低温度；
    若该城市无历史数据，则获取该城市所在省会的最高温度和最低温度。
    """

    def get_temperature_by_id(station_id: int):
        """根据id获取2000年来该气象站的最高温度和最低温度"""
        from bs4 import BeautifulSoup  # 引用BeautifulSoup库
        import requests  # 引用requests

        url = f'http://www.meteomanz.com/sy4?ind={station_id}&y1=2000'
        lst = []
        r = requests.get(url)
        r.encoding = 'utf-8'
        text = r.text
        soup = BeautifulSoup(text, "html.parser")
        table = soup.find('table')
        tr = table.find_all('tr')
        for page in range(0, 23):
            td = tr[page].find_all('td')
            lst.append(float(td[4].text), )
            lst.append(float(td[5].text), )
        lst.sort()
        return {'min': lst[0],
                'max': lst[-1],
                }

    try:
        # 尝试获取该城市
        station_id = get_id_by_name(cityname)
        T = get_temperature_by_id(station_id)
    except:
        # 获取省会
        province_capital = get_province_capital_by_city(cityname)
        station_id = get_id_by_name(province_capital)
        print(f'获取{cityname}历史温度失败，故采用所在省省会{province_capital}的数据。')
        T = get_temperature_by_id(station_id)
    print(f'自2000年来，最低温度：{T["min"]}℃，最高温度：{T["max"]}℃。')
    return T
