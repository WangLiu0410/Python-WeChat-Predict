import sqlite3
import xlrd
from model import one_model


# 创建数据库
def sql_model():
    conn = sqlite3.connect('datawx.db')
    curs = conn.cursor()

    """
    本数据库分为三页：
        第一页完完整整的存放表格数据
        第二页保存每个公众号每天的阅读量总和
        第三页保存每个公众号每月的总阅读量
    """

    curs.execute("""
    CREATE TABLE 总表(
        微信号 int,
        是否头条 int,
        阅读量 int,
        点赞量 int,
        发布日期 TEXT
    )
    """)

    curs.execute("""
    CREATE TABLE 天表(
        微信号 int,
        阅读量 int,
        置顶推送预测 int,
        发布日期 TEXT
    )
    """)

    curs.execute("""
    CREATE TABLE 月表(
        微信号 int,
        阅读量 int,
        等级评定 TEXT
    )
    """)

    conn.commit()
    curs.close()
    conn.close()


# 数据库中第一页的数据写入
def w_sqlite_1():
    wb = xlrd.open_workbook('dataWx.xlsx')
    ws = wb.sheet_by_index(0)
    conn = sqlite3.connect('datawx.db')
    curs = conn.cursor()
    for i in range(1, ws.nrows):
        row = ws.row_values(i)
        times = xlrd.xldate_as_tuple(ws.cell(i, 4).value, 0)[:3]
        time_data = str(times[0]) + " " + str(times[1]) + " " + str(times[2])
        query = 'INSERT INTO 总表 VALUES(?,?,?,?,?)'
        vals = [int(row[0]),  int(row[1]),  int(
            row[2]),  int(row[3]),  time_data]
        curs.execute(query, vals)
    conn.commit()
    curs.close()
    conn.close()


# 统计每天阅读量,查看置顶推送文章是否预测正确的
def every_sum(dates):
    big_read = []
    read = []
    good = []
    top = 1
    for i in dates:
        if i[2] < 100001:
            read.append(i[2])
            good.append(i[3])
        else:
            big_read.append(i)
    if not big_read == []:
        c10 = one_model(good, read)
        for i in big_read:
            rn = c10[0] * i[3] + c10[1]
            if rn > 100001:
                read.append(round(rn))
            else:
                read.append(100001)
    read = sum(read)
    for k in dates[:-1]:
        if k[2] > dates[-1][2]:
            top = 0
    return read, top


# 读取数据库中总表的所有数据，返回一个列表
def read_one():
    dates = []
    conn = sqlite3.connect('datawx.db')
    curs = conn.cursor()
    date = curs.execute('SELECT 微信号, 是否头条, 阅读量, 点赞量, 发布日期 from 总表')
    for n in date:
        dates.append(n)
    curs.close()
    conn.close()
    return dates


#  数据库第二页的数据写入
def w_sqlite_2():
    temp = []
    dates = read_one()
    conn = sqlite3.connect('datawx.db')
    curs = conn.cursor()
    for i in dates:
        if temp == []:
            temp.append(i)
        elif i[4] == temp[0][4]:
            temp.append(i)
        else:
            read_sum, top = every_sum(temp)
            curs.execute(
                'INSERT INTO 天表 VALUES(?,?,?,?)',
                [temp[0][0], read_sum, top, temp[0][-1]]
                )
            temp = []
            temp.append(i)
    read_sum, top = every_sum(temp)
    curs.execute(
        'INSERT INTO 天表 VALUES(?,?,?,?)',
        [temp[0][0], read_sum, top, temp[0][-1]]
        )
    conn.commit()
    curs.close()
    conn.close()


# 公众号每月阅读量汇总
def month_sum():
    name = None
    read = 0
    month_date = []
    conn = sqlite3.connect('datawx.db')
    curs = conn.cursor()
    date = curs.execute('SELECT 微信号, 阅读量, 置顶推送预测, 发布日期 from 天表')
    for i in date:
        if read == 0:
            name = i[0]
            read = i[1]
        elif i[0] == name:
            read += i[1]
        else:
            month_date.append([name, read])
            name = i[0]
            read = i[1]
    month_date.append([name, read])
    curs.close()
    conn.close()
    return month_date


# 数据库第三页数据的写入
def w_sqlite_3():
    """
    等级设置规定：
        我们将这32个微信公众号每月的总计阅读量进行排序
        每月总阅读量我们以100万次为一个10分
        超过100万次，我们等级以字母划分
        100万～300万：A
        300万～600万：S
        600万～900万：SS
    """
    month_date = month_sum()
    month_date.sort(reverse=True, key=lambda x: x[1])
    conn = sqlite3.connect('datawx.db')
    curs = conn.cursor()
    for i in month_date:
        grade = (i[1] / 1000000) * 10
        if grade < 10:
            curs.execute(
                'INSERT INTO 月表 VALUES(?,?,?)',
                [i[0], i[1], str(grade)[:4]]
                )
        elif grade <= 30:
            curs.execute(
                'INSERT INTO 月表 VALUES(?,?,?)',
                [i[0], i[1], "A"]
                )
        elif grade <= 60:
            curs.execute(
                'INSERT INTO 月表 VALUES(?,?,?)',
                [i[0], i[1], "S"]
                )
        else:
            curs.execute(
                'INSERT INTO 月表 VALUES(?,?,?)',
                [i[0], i[1], "SS"]
                )
    conn.commit()
    curs.close()
    conn.close()


if __name__ == "__main__":
    sql_model()
    w_sqlite_1()
    w_sqlite_2()
    w_sqlite_3()
