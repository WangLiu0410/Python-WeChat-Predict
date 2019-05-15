from Predict_data import read_db
from model import dd_model
import pygal


# 将数据库里提取出来的数据进行处理，返回一个列表：[[], []...]
# 每个列表里的数据为每个公众号所有有记录的阅读人次
def write_data_1():
    ll = []
    for i in range(32):
        ll.append([])
    dates = read_db()
    n = 0
    for i in dates:
        if i[0] == n + 1:
            ll[n].append(i[1])  # [int(i[3][-2:])]
        else:
            n += 1
            ll[n].append(i[1])  # [int(i[3][-2:])]
    return ll


# 经过测试，我们对每个公众号所有有阅读数据记录的值做6次多项式拟合
# 经过6次多项式拟合后的模型精度有一定的保证，过拟合现象也不是很严重
# 我们返回一个列表，包含所有微信公众号未来三天阅读量的一个预测数据
def predict():
    ll = write_data_1()
    data_1 = []
    data_2 = []
    data_3 = []
    n = 1
    for i in ll:
        x, p = dd_model(i)
        data_1.append([n, abs(round(p(len(i))))])
        data_2.append([n, abs(round(p(len(i) + 1)))])
        data_3.append([n, abs(round(p(len(i) + 2)))])
        n += 1
    data_1.sort(reverse=True, key=lambda y: y[1])
    data_2.sort(reverse=True, key=lambda y: y[1])
    data_3.sort(reverse=True, key=lambda y: y[1])
    return [data_1, data_2, data_3]


if __name__ == "__main__":
    future_data = predict()
    n = 1
    for i in future_data:
        x = []
        y = []
        for j in i:
            x.append(j[0])
            y.append(j[1])
        hist = pygal.Bar()
        hist.x_labels = x
        hist.x_title = "微信公众号编号"
        hist.y_title = "预测阅读人次"
        hist.add('阅读人次', y)
        hist.render_to_file('./预测未来三天/第%d天.svg' % n)
        n += 1
