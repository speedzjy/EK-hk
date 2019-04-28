# 我采用requests库
import requests
import time
import json
import matplotlib.pyplot as plt
import sqlite3
# 用来获取 时间戳
def gettime():
    return int(round(time.time() * 1000))

if __name__ == '__main__':
    # 用来自定义头部的
    headers = {}
    # 用来传递参数的
    keyvalue = {}
    # 目标网址(问号前面的东西)
    url = 'http://data.stats.gov.cn/easyquery.htm'

    # 头部的填充
    headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) ' \
                            'AppleWebKit/605.1.15 (KHTML, like Gecko) ' \
                            'Version/12.0 Safari/605.1.15'

    # 下面是参数的填充
    keyvalue['m'] = 'QueryData'
    keyvalue['dbcode'] = 'hgnd'
    keyvalue['rowcode'] = 'zb'
    keyvalue['colcode'] = 'sj'
    keyvalue['wds'] = '[]'
    keyvalue['dfwds'] = '[{"wdcode":"zb","valuecode":"A0802"}]'
    keyvalue['k1'] = str(gettime())

    # 发出请求，使用get方法，这里使用我们自定义的头部和参数
    #r = requests.get(url, headers=headers, params=keyvalue)
    # 建立一个Session,在Session基础上进行一次请求
    s = requests.session()
    r = s.post(url, params=keyvalue, headers=headers)
    #解析数据
    year = [] #年份
    int_year = []#整数形式的年份列表
    revenue = [] #全国财政收入
    revenue_central = [] #中央财政收入
    revenue_regional = [] #地方财政收入
    ratio_central = []
    ratio_regional = []
    data = json.loads(r.text)
    data_one = data['returndata']['datanodes']
    #获取总财政收入，中央收入，地方收入，存入列表
    for value in data_one:
        if ('A080201_sj' in value['code']) & (float(value['code'][-4:])!=2018):
            year.append(value['code'][-4:])
            revenue.append(float(value['data']['strdata']))
        if ('A080202_sj' in value['code']) & (float(value['code'][-4:])!=2018):
            revenue_central.append(float(value['data']['strdata']))
        if ('A080203_sj' in value['code']) & (float(value['code'][-4:])!=2018):
            revenue_regional.append(float(value['data']['strdata']))
    list.reverse(year)
    list.reverse(revenue)
    list.reverse(revenue_central)
    list.reverse(revenue_regional)

    for i in range(2008,1998,-1):
        # 修改dfwds字段内容
        str1='[{"wdcode":"sj","valuecode":'
        str2=str(i)
        str3='}]'
        keyvalue['dfwds'] = str1+str2+str3
        # 再次进行请求
        r = s.post(url, params=keyvalue, headers=headers)
        data_less2009 = json.loads(r.text)
        data_two = data_less2009['returndata']['datanodes']
        #前插方式将2009年以前年份的数据插入列表
        for value in data_two:
            if ('A080201_sj' in value['code']):
                year.insert(0,value['code'][-4:])
                revenue.insert(0,float(value['data']['strdata']))
            if ('A080202_sj' in value['code']):
                revenue_central.insert(0,float(value['data']['strdata']))
            if ('A080203_sj' in value['code']):
                revenue_regional.insert(0,float(value['data']['strdata']))

    for i in range(0,len(year)):
        ratio_central.append(float(revenue_central[i])/float(revenue[i]))
        ratio_regional.append(float(revenue_regional[i])/float(revenue[i]))
        int_year.append(int(year[i]))
    print(year)
    print(revenue)
    print(revenue_central)
    print(revenue_regional)
    print(ratio_regional)
    print(ratio_central)

    # 保存数据至数据库
    input_str = input("Input DATABASE Name:")
    str_stand = input_str + '.db'
    conn = sqlite3.connect(str_stand)
    # 创建一个Cursor:
    cu = conn.cursor()
    # 创建年份——人口表格
    cu.execute('create table year_revenue (revenue , year UNIQUE)')
    # 创建年份——男,女人口表格
    cu.execute('create table year_r_c (revenue , year UNIQUE)')
    cu.execute('create table year_r_r (revenue , year UNIQUE)')
    for i in range(0, 19):
        str_year = str(year[i])
        str_revenue = str(revenue[i])
        str_revenue_c = str(revenue_central[i])
        str_revenue_r = str(revenue_regional[i])
        str1 = "insert into year_revenue values(" + str_revenue + "," + str_year + ")"
        str2 = "insert into year_r_c values(" + str_revenue_c + "," + str_year + ")"
        str3 = "insert into year_r_r values(" + str_revenue_r + "," + str_year + ")"
        cu.execute(str1)
        cu.execute(str2)
        cu.execute(str3)
    conn.commit()
    cu.execute("select * from year_revenue")
    y_r = str(cu.fetchall())
    y_r = y_r.replace(')', '')  # 字符串中指定字符消除
    y_r = y_r.replace('(', '')
    y_r = y_r.replace("[", '')
    y_r = y_r.replace("]", '')
    y_r = y_r.replace(" ", '')
    y_r = y_r.replace("'", '')
    y_r = y_r.replace("'", '')
    y_r = y_r.split(',')
    print(y_r)
    # y_r=[总收入，年份]
    cu.execute("select * from year_r_c")
    y_r_c = str(cu.fetchall())
    y_r_c = y_r_c.replace(')', '')
    y_r_c = y_r_c.replace('(', '')
    y_r_c = y_r_c.replace('[', '')
    y_r_c = y_r_c.replace(']', '')
    y_r_c = y_r_c.replace("'", '')  # 前单引号消除
    y_r_c = y_r_c.replace("'", '')  # 后单引号消除
    y_r_c = y_r_c.split(',')
    # y_r_c=[中央收入，年份]
    cu.execute("select * from year_r_r")
    y_r_r = str(cu.fetchall())
    y_r_r = y_r_r.replace(')', '')
    y_r_r = y_r_r.replace('(', '')
    y_r_r = y_r_r.replace('[', '')
    y_r_r = y_r_r.replace(']', '')
    y_r_r = y_r_r.replace("'", '')  # 前单引号消除
    y_r_r = y_r_r.replace("'", '')  # 后单引号消除
    y_r_r = y_r_r.split(',')
    # y_r_r=[地方收入，年份]
    # 从数据库中读取
    year_L = []  # 整数形式的年份列表
    revenue_L = []  # 年末总人口
    revenue_central_L = []  # 年末男性总人口
    revenue_regional_L = []  # 年末女性总人口
    ratio_central_L = []
    ratio_regional_L = []

    for i in range(0, 19):
        k = 2 * i + 1
        q = 2 * i
        year_L.append(y_r[k])
        revenue_L.append(float(y_r[q]))
        revenue_central_L.append(float(y_r_c[q]))
        revenue_regional_L.append(float(y_r_r[q]))

    #绘制数据图表
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    fig1 = plt.figure(figsize=(18, 9))
    plt.subplot(2, 2, 1)
    plt.bar(year_L, revenue_L)
    plt.xlabel(u'年份')
    plt.ylabel(u'亿元')
    plt.title(u'年末国内财政总收入')
    plt.subplot(2, 2, 2)
    plt.bar(year_L, revenue_central_L)
    plt.xlabel(u'年份')
    plt.ylabel(u'亿元')
    plt.title(u'年末中央财政总收入')

    plt.subplot(2, 2, 3)
    plt.bar(year_L, revenue_regional_L)
    plt.xlabel(u'年份')
    plt.ylabel(u'亿元')
    plt.title(u'年末地方财政总收入')

    plt.subplot(2, 2, 4)
    #plt.ylim((0.47, 0.53))
    plt.xticks(int_year)
    line_central = plt.plot(int_year, ratio_central,color = 'red',linewidth = 2.0, linestyle = '--')
    line_regional = plt.plot(int_year, ratio_regional,color = 'blue',linewidth = 3.0, linestyle = '-.')
    #plt.legend( labels=['男', '女'],loc='upper right')
    plt.xlabel(u'年份')
    plt.ylabel(u'比例')
    plt.title(u'中央、地方收入占比折线图')

    plt.show()
