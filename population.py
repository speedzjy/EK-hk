import requests
import time  #获取时间戳
import json
import matplotlib.pyplot as plt    #绘图库
import sqlite3         #sqlite数据库
# 获取 时间戳
def gettime():
    return int(round(time.time() * 1000))

if __name__ == '__main__':
    # 用来自定义头部的
    headers = {}
    # 用来传递参数
    keyvalue = {}
    # 目标网址
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
    keyvalue['dfwds'] = '[{"wdcode":"zb","valuecode":"A0301"}]'
    keyvalue['k1'] = str(gettime())

    # 发出请求，使用get方法
    # 建立一个Session,在Session基础上进行一次请求
    s = requests.session()
    r = s.get(url, params=keyvalue, headers=headers)
    #解析数据
    year = [] #年份
    int_year = []#整数形式的年份列表
    population = [] #年末总人口
    population_man = [] #年末男性总人口
    population_woman = [] #年末女性总人口
    ratio_man = [] #男人口占比
    ratio_woman = [] #女人口占比
    data = json.loads(r.text)
    data_one = data['returndata']['datanodes']
    #获取总人口，男性人口，女性人口存入列表
    for value in data_one:
        if ('A030101_sj' in value['code']):
            year.append(value['code'][-4:])
            population.append(int(value['data']['strdata']))
        if ('A030102_sj' in value['code']):
            population_man.append(int(value['data']['strdata']))
        if ('A030103_sj' in value['code']):
            population_woman.append(int(value['data']['strdata']))
    list.reverse(year)
    list.reverse(population)
    list.reverse(population_man)
    list.reverse(population_woman)
    for i in range(2008,1998,-1):
        # 修改dfwds字段内容
        str1='[{"wdcode":"sj","valuecode":'
        str2=str(i)
        str3='}]'
        keyvalue['dfwds'] = str1+str2+str3
        # 再次进行请求
        r = s.get(url, params=keyvalue, headers=headers)
        data_less2009 = json.loads(r.text)
        data_two = data_less2009['returndata']['datanodes']
        #前插方式将2009年以前年份的数据插入列表
        for value in data_two:
            if ('A030101_sj' in value['code']):
                year.insert(0,value['code'][-4:])
                population.insert(0,int(value['data']['strdata']))
            if ('A030102_sj' in value['code']):
                population_man.insert(0,int(value['data']['strdata']))
            if ('A030103_sj' in value['code']):
                population_woman.insert(0,int(value['data']['strdata']))
    for i in range(0,len(year)):
        ratio_man.append(int(population_man[i])/int(population[i]))
        ratio_woman.append(int(population_woman[i])/int(population[i]))
        int_year.append(int(year[i]))
    print(year)
    print(population)
    print(population_man)
    print(population_woman)
    print(ratio_man)
    print(ratio_woman)

    #保存数据至数据库
    input_str = input("Input DATABASE Name:")
    str_stand = input_str + '.db'
    conn = sqlite3.connect(str_stand)
    # 创建一个Cursor:
    cu = conn.cursor()
    #创建年份——人口表格
    cu.execute('create table year_population (population , year UNIQUE)')
    #创建年份——男,女人口表格
    cu.execute('create table year_p_man (population , year UNIQUE)')
    cu.execute('create table year_p_woman (population , year UNIQUE)')
    for i in range(0, 20):
        str_year = str(year[i])
        str_population = str(population[i])
        str_population_man = str(population_man[i])
        str_population_woman = str(population_woman[i])
        str1 = "insert into year_population values(" + str_population + "," + str_year + ")"
        str2 = "insert into year_p_man values(" + str_population_man + "," + str_year + ")"
        str3 = "insert into year_p_woman values(" + str_population_woman + "," + str_year + ")"
        cu.execute(str1)  #插入数据
        cu.execute(str2)
        cu.execute(str3)
    conn.commit()
    cu.execute("select * from year_population")
    y_p = str(cu.fetchall())
    y_p = y_p.replace(')', '') #字符串中指定字符消除
    y_p = y_p.replace('(', '')
    y_p = y_p.replace("[", '')
    y_p = y_p.replace("]", '')
    y_p = y_p.replace(" ", '')
    y_p = y_p.replace("'", '')
    y_p = y_p.replace("'", '')
    y_p = y_p.split(',') #将y_p重新变成列表
    print(y_p)
    #y_p=[总人口，年份]
    cu.execute("select * from year_p_man")
    y_p_man = str(cu.fetchall())
    y_p_man = y_p_man.replace(')', '')
    y_p_man = y_p_man.replace('(', '')
    y_p_man = y_p_man.replace('[', '')
    y_p_man = y_p_man.replace(']', '')
    y_p_man = y_p_man.replace("'", '')  # 前单引号消除
    y_p_man = y_p_man.replace("'", '')  # 后单引号消除
    y_p_man = y_p_man.split(',')
    # y_p_man=[男人口，年份]
    cu.execute("select * from year_p_woman")
    y_p_woman = str(cu.fetchall())
    y_p_woman = y_p_woman.replace(')', '')
    y_p_woman = y_p_woman.replace('(', '')
    y_p_woman = y_p_woman.replace('[', '')
    y_p_woman = y_p_woman.replace(']', '')
    y_p_woman = y_p_woman.replace("'", '')  # 前单引号消除
    y_p_woman = y_p_woman.replace("'", '')  # 后单引号消除
    y_p_woman = y_p_woman.split(',')
    # y_p_woman=[女人口，年份]
    print(y_p)
    #从数据库中读取
    year_L = []  # 整数形式的年份列表
    population_L = []  # 年末总人口
    population_man_L = []  # 年末男性总人口
    population_woman_L = []  # 年末女性总人口
    ratio_man_L = []  # 男人口占比
    ratio_woman_L = []  # 女人口占比

    for i in range(0,20):
        k=2*i + 1
        q=2*i
        year_L.append(y_p[k])
        population_L.append(int(y_p[q]))
        population_man_L.append(int(y_p_man[q]))
        population_woman_L.append(int(y_p_woman[q]))

    #绘制数据图表
    fig1=plt.figure(figsize=(10,6))
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.bar(year_L, population_L)
    print(year_L)
    print(year)
    #plt.bar(year, population)
    plt.xlabel(u'年份')
    plt.ylabel(u'万人')
    plt.title(u'年末总人口')
    fig2=plt.figure(figsize=(10,6))
    plt.ylim((0.47, 0.53))
    plt.xticks(int_year)
    line_man = plt.plot(int_year, ratio_man,color = 'red',linewidth = 2.0, linestyle = '--')
    line_woman = plt.plot(int_year, ratio_woman,color = 'blue',linewidth = 3.0, linestyle = '-.')
    plt.legend( labels=['男', '女'],loc='upper right')
    plt.xlabel(u'年份')
    plt.ylabel(u'比例')
    plt.title(u'男女占比折线图')
    plt.show()

