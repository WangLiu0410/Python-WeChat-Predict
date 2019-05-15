import numpy as np
import matplotlib.pyplot as plt


# 构建一维线性模型方程
def one_model(X, Y):
    can_num = np.polyfit(X, Y, 1)  # 一次多项式拟合，相当于线性拟合
    return can_num


# 构建6次多项式拟合模型
def dd_model(dd):
    x = np.arange(1, len(dd) + 1, 1)
    y = np.array(dd)
    z1 = np.polyfit(x, y, 6)
    p1 = np.poly1d(z1)
    return x, p1


# 采用一组数据可视化查看效果
def view_data():
    """
    这里采用的是编号为6的微信公众号2014年9月11号的数据
    通过这一天的数据，将预测的阅读量及样本数据还有构建的一维线性模型可视化
    直观展示预测结果
    当天本微信公众号置顶的推文————点赞量121， 阅读量10万+
    """
    X = [9, 4, 4, 10, 7, 11, 4]
    Y = [9073, 5887, 15011, 21829, 6896, 13651, 4082]
    z1 = one_model(X, Y)
    n = z1[0] * 121 + z1[1]

    # 绘制出样本数据，蓝色代表样本数据，红色代表预测点
    plt.scatter(X, Y, s=30, c="blue")
    plt.scatter(121, n, s=30, c="red")

    # 绘制出预测的一维直线
    x = np.linspace(0, 130)
    y = z1[0] * x + z1[0]
    plt.plot(x, y, c="black")
    plt.show()


if __name__ == "__main__":
    view_data()
