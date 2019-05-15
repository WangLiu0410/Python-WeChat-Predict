import sqlite3
import pygal
import matplotlib.pyplot as plt
from model import dd_model


# 获取每天每个公众号的阅读数据，返回一个列表
def read_db():
    dates = []
    conn = sqlite3.connect('datawx.db')
    curs = conn.cursor()
    date = curs.execute('SELECT 微信号, 阅读量, 置顶推送预测, 发布日期 from 天表')
    for n in date:
        dates.append(n)
    curs.close()
    conn.close()
    return dates


# 将数据库里提取出来的数据进行处理，返回一个列表：[[[], []...], [[], []...]...]
# 第二层的每个列表代表的是一天的数据， 第三层列表代表的是每个公众号在那一天对应的阅读量
def write_data():
    ll = []
    for i in range(30):
        ll.append([])
    dates = read_db()
    for i in dates:
        ll[int(i[3][-2:]) - 1].append([i[0], i[1]])
    return ll


# 补全当天某些公众号没发送推文而导致的数据缺失
def tab_data():
    ll = write_data()
    for i in range(30):
        if not len(ll[i]) == 32:
            for j in range(1, 32):
                if not ll[i][j - 1][0] == j:
                    ll[i].insert(j - 1, [j, 0])
            if not len(ll[i]) == 32:
                ll[i].insert(31, [32, 0])
    return ll


# 将每一天各个微信公众号的阅读量进行可视化处理（每天生成一个svg文件）
def draw_data(ll):
    for day in range(30):
        x = []
        y = []
        for temp in ll[day]:
            x.append(temp[0])
            y.append(temp[1])
        hist = pygal.Bar()
        hist.x_labels = x
        hist.x_title = "微信公众号编号"
        hist.y_title = "阅读人次"
        hist.add('阅读人次', y)
        hist.render_to_file('./每天公众号阅读量柱状图/第%d天.svg' % (day + 1))


# 返回指定公众号在这一个月内每天的阅读量排名
def rank_data(ll, n):
    rank = []
    for i in ll:
        h = 1
        for j in i:
            if i[n - 1][1] < j[1]:
                h += 1
        rank.append(h)
    return rank


# 对指定的公众号预测接下来1天的阅读量排名，并可视化
def predict(ll, n):
    rank = rank_data(ll, n)
    x, p = dd_model(rank)
    yvals = p(x)
    for i in p([31]):
        m = abs(round(i))
        if m == 0:
            rank.append(1)
        elif m > 32:
            rank.append(32)
        else:
            rank.append(m)
    plt.plot(list(x) + [31], rank, '*', label='original values')
    plt.plot(x, yvals, 'r', label='polyfit values')
    plt.xlabel('Day')
    plt.ylabel('Rank')
    plt.title('WeChar-num:%d------one day predict' % n)
    plt.show()


if __name__ == "__main__":
    ll = tab_data()
    draw_data(ll)
    n = int(input("请输入你想预测排名的微信公众号的编号(1~32):"))
    predict(ll, n)
