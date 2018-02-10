# coding: utf-8
"""
默认PEP8的docstring，文件注释写在这里
"""
# Copyright (c) 2018 BeiTown

import os
import pandas
from sklearn.linear_model import LinearRegression


def linear_model_main(_distances, _press_times, target_distance):
    regress = LinearRegression()
    regress.fit(_distances, _press_times)
    predict_press_time = regress.predict(target_distance)
    result = {'intercept': regress.intercept_, 'coefficient': regress.coef_, 'value': predict_press_time}
    # 截距 b
    # 斜率值 k
    # 预估的按压时间
    return result


def computing_k_b_v(target_distance):
    result = linear_model_main(distances, press_times, target_distance)
    b = result['intercept']
    k = result['coefficient']
    v = result['value']
    return k[0], b[0], v[0]


def add_data(distance, press_time):
    distances.append([distance])
    press_times.append([press_time])
    save_data('./jump_range.csv', distances, press_times)


def save_data(file_name, in_distances, in_press_times):
    pf = pandas.DataFrame({'Distance': in_distances, 'Press_time': in_press_times})
    # print(pf)
    pf.to_csv(file_name, index=False, sep=',')


def get_data(file_name):
    data = pandas.read_csv(file_name)
    distance_array = []
    press_time_array = []
    for distance, press_time in zip(data['Distance'], data['Press_time']):
        distance_array.append([float(distance.strip().strip('[]'))])
        press_time_array.append([float(press_time.strip().strip('[]'))])
    return distance_array, press_time_array


def init():
    global distances, press_times
    distances = []
    press_times = []

    if os.path.exists('./jump_range.csv'):
        distances, press_times = get_data('./jump_range.csv')
    else:
        save_data('./jump_range.csv', [], [])
        return 0


def get_result_len():
    return len(distances)
