import requests as req

import webbrowser as wb
from pygooglechart import Chart
from pygooglechart import SimpleLineChart
from pygooglechart import Axis

def get_data(url, param):
    return req.get(url, param).json()

def create_chart(npatients, dates, year, month):
    width = 700
    height = 400
    chart = SimpleLineChart(width, height)
    chart.add_data(npatients)
    chart.set_colours(['333333'])
    chart.set_line_style(index=0, thickness=1)
    # グラフの下のやつ
    if len(dates) <= 31:
        chart.set_axis_labels(Axis.BOTTOM, [i+1 for i in range(len(dates))])
    else:
        interval = 16
        offset = len(dates) // interval
        chart.set_axis_labels(Axis.BOTTOM, [dates[i * offset][5:] for i in range(interval)])
    # グラフの左のやつ
    npatients = sorted(npatients)
    minimum = min(npatients)
    maximum = max(npatients)
    chart.set_axis_labels(Axis.LEFT, [
        minimum,
        maximum // 4,
        maximum // 2,
        maximum // 4 + maximum // 2, 
        maximum])
    # interval = 5
    # offset = len(npatients) // interval
    # chart.set_axis_labels(Axis.LEFT, [npatients[i * offset] for i in range(interval)])
    
    # 2021-08-24 -> [2021, 8, 24] -> year, month = 2021, 8
    if month == 0:
        chart.set_title(f'{year}年の感染者数')
    else:
        chart.set_title(f'{year}年{month}月の感染者数')
    return chart

def main():
    s = input('年と月を入力: ')
    try:
        year, month = map(int, s.split())
    except ValueError:
        print('入力方法が違います (例: 2021 08)')
        main()
        return
    if year < 2020 or month < 0 or month > 12:
        print('入力方法が違います (例: 2021 08)')
        main()
        return
    print('データを取得します...')
    url = 'https://opendata.corona.go.jp/api/Covid19JapanAll'
    param = {'dataName': '沖縄県'}
    data = get_data(url, param)['itemList']
    index = 0
    # indexの開始位置を決める
    while True:
        data_date = data[index]['date']
        data_year, data_month = map(int, data_date[:7].split('-'))
        # 最初に決めた年と月と一致すればOK
        if data_year == year and (data_month == month or month == 0):
            break
        index += 1
    md_dates = []
    md_npatients = []
    while True:
        md_dates.append(data[index]['date'])
        md_npatients.append(int(data[index]['npatients']) - int(data[index+1]['npatients']))
        # 月が変われば終わり
        if (month == 0 and (index+2 == len(data) or int(data[index+1]['date'][:4]) != year))\
            or (month != 0 and int(data[index+1]['date'][5:7]) != month):
            break
        index += 1
    # 月末から取得したので、反転させる
    md_dates = list(reversed(md_dates))
    md_npatients = list(map(int, [d for d in list(reversed(md_npatients))]))
    print('グラフを作成中...')
    chart = create_chart(md_npatients, [s for s in md_dates], year, month)
    filename = f'corona_{year}.png' if month == 0 else f'corona_{year}_{month}.png'
    chart.download(filename)
    wb.open(filename)

if __name__ == '__main__':
	main()
