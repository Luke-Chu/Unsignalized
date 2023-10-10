from statistics import mean

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

model_selected = [3]
cars_selected = [80]

"""
11左转车道：
    x = r * cos(θ)
    y = r * sin(θ)
21左转车道：
    x = width - r * sin(θ)
    y = r * cos(θ)
33左转车道：
    x = width - r * cos(θ)
    y = width - r * sin(θ)
43左转车道
    x = r * sin(θ)
    y = width - r * cos(θ)
当通过交叉口的时刻为4个时刻时，θ分别为：
    pi / 16, pi * 3 / 16, pi * 5 / 16, pi * 7 / 16
当通过交叉口的时刻为5个时刻时，θ分别为：
    pi / 20, pi * 3 / 20, pi * 5 / 20, pi * 7 / 20, pi * 9 / 20 
"""
r = 15.625
pos_x = {11: [15.325, 12.992, 8.681, 3.048], 21: [21.952, 16.319, 12.008, 9.675],
         33: [9.675, 12.008, 16.319, 21.952], 43: [3.048, 8.681, 12.992, 15.325]}
pos_y = {11: [3.048, 8.681, 12.992, 15.325], 21: [15.325, 12.992, 8.681, 3.048],
         33: [21.952, 16.319, 12.008, 9.675], 43: [9.675, 12.008, 16.319, 21.952]}


def adjust_traj():
    for ml_s in model_selected:
        for c_s in cars_selected:
            traj_df = pd.read_csv(f'model{ml_s}_{c_s}.txt', sep='\\s+', header=None, names=['lane', 'id', 'time', 'x', 'y', 'v'])
            # traj_df = pd.read_csv(f'D:/Luke/Desktop/xin/model_xin_{ml_s}_{c_s}.txt', sep='\\s+', header=None,
            #                       names=['lane', 'id', 'time', 'x', 'y', 'v'])
            adjust_dict = {11: [], 21: [], 33: [], 43: []}
            # 设置车id初始值为0
            visited_id = 0
            visited_lane = 0
            for index, row in traj_df.iterrows():
                # 获取该行的车道号
                car_lane = row['lane']
                # 每次遍历一个新的车道时，需要更新访问车辆的id，因为文件中每个车道的id是从1开始
                if visited_lane != car_lane:
                    visited_lane = car_lane
                    visited_id = 0
                # 获取该行的车辆id
                car_id = row['id']
                # 如果车辆的id和已经访问的车辆id相等，可以直接跳过
                if car_id == visited_id:
                    continue
                if car_lane == 11:   # 11车道调整
                    # 第一次x坐标小于15.625，说明是进入交叉口的第一个时刻
                    if row['x'] < 15.625:
                        # 将索引加入待处理索引中
                        adjust_dict[car_lane].append(index)
                        visited_id = car_id
                elif car_lane == 21:  # 21车道调整
                    # 第一次y坐标小于15.625时，进入了交叉口
                    if row['y'] < 15.625:
                        # 将索引加入待处理中
                        adjust_dict[car_lane].append(index)
                        visited_id = car_id
                elif car_lane == 33:  # 33车道调整
                    # 第一次x坐标大于9.375，进入了交叉口
                    if row['x'] > 9.375:
                        # 将索引加入待处理中
                        adjust_dict[car_lane].append(index)
                        visited_id = car_id
                elif car_lane == 43:  # 43车道调整
                    # 第一次y坐标大于9.375，进入了交叉口
                    if row['y'] > 9.375:
                        adjust_dict[car_lane].append(index)
                        visited_id = car_id
            for lane_, index_list in adjust_dict.items():
                for index in index_list:
                    for i in range(index, index + 4):
                        traj_df.at[i, 'x'] = pos_x[lane_][i - index]
                        traj_df.at[i, 'y'] = pos_y[lane_][i - index]
            traj_df.to_csv(f'model{ml_s}_{c_s}.txt', index=False, sep=' ', header=False, lineterminator='\n')
            # traj_df.to_csv(f'D:/Luke/Desktop/xin/model_xin_{ml_s}_{c_s}.txt', index=False, sep=' ', header=False, lineterminator='\n')


def analysis():
    # 设置一个字典存储每个模型的平均能耗
    model_energy = {}
    for ml_s in model_selected:
        model_energy[ml_s] = {}
        for cn_s in cars_selected:
            traj_df = pd.read_csv(f'D:/Luke/Desktop/xin/model_xin_{ml_s}_{cn_s}.txt', sep='\\s+', header=None,
                                  names=['lane', 'id', 'time', 'x', 'y', 'v'])
            # 设置一个字典存储每个车道的平均能耗
            lane_energy = {}
            for lane_id, lane_df in traj_df.groupby(by='lane'):
                # 设置一个字典存储每辆车的平均能耗
                car_energy = {}
                for c_id, c_df in lane_df.groupby(by='id'):
                    # 这就得到了每辆车的轨迹
                    # 提取速度列
                    speed_col = c_df['v']
                    # 下一时刻的速度
                    next_speed_col = c_df['v'].shift(-1)
                    # 计算加速度
                    c_df['acc'] = (next_speed_col - speed_col) / 0.5
                    # 将小于0的加速度置为0，因为计算能耗只看大于0的加速度
                    c_df.loc[c_df['acc'] < 0, 'acc'] = 0
                    # 然后计算每时刻的能耗    E = a + 0.014 * v
                    c_df['energy'] = c_df['acc'] + 0.014 * 3.6 * c_df['v']
                    # 计算平均能耗
                    mean_energy = c_df['energy'].mean()
                    # 加入字典中
                    car_energy[c_id] = mean_energy
                    # print(f"{lane_id}车道--车{c_id}的平均能耗", mean_energy)
                # 计算每个车道的平均能耗
                lane_energy[lane_id] = mean(car_energy.values())
                print(f'{lane_id}车道平均能耗{lane_energy[lane_id]}')
            # 计算同模型下，不同数量的每个模型的平均能耗
            model_energy[ml_s][cn_s] = mean(lane_energy.values())
            print(f'model{ml_s}，下数量{cn_s}的平均能耗{model_energy[ml_s][cn_s]}')

    for cn_s in cars_selected:
        for ml_s in model_selected:
            print(f'数量{cn_s}下，model{ml_s}的平均能耗：{round(model_energy[ml_s][cn_s], 3)}')


def analysis_all():
    v_data = {
        'nums': [10, 30, 50, 80, 100],
        'FCFS': [15.491, 12.575, 9.576, 7.646, 6.283],
        'OPT-DFST': [14.963, 13.049, 10.170, 7.303, 6.083],
        'MM': [15.019, 13.086, 10.180, 7.303, 6.084]
    }
    pass_time_data = {
        'nums': [10, 30, 50, 80, 100],
        'FCFS': [22, 78, 112, 168, 224],
        'OPT-DFST': [24, 64, 104, 164, 200],
        'MM': [20, 60, 100, 160, 200]
    }
    last_time_data = {
        'nums': [10, 30, 50, 80, 100],
        'FCFS': [43, 92, 122, 179, 230],
        'OPT-DFST': [49, 80, 121, 180, 216],
        'MM': [45, 76, 117, 176, 216]
    }
    cpu_time_data = {
        'nums': [10, 30, 50, 80, 100],
        'FCFS': [0.03, 0.19, 0.58, 4.31, 7.05],
        'OPT-DFST': [0.09, 0.16, 0.50, 5.09, 6.59],
        'MM': [0.03, 0.19, 0.47, 2.94, 8.66]
    }
    pass_rate_data = {
        'nums': [10, 30, 50, 80, 100],
        'FCFS': [1, 1, 0.98, 0.7, 0.51],
        'OPT-DFST': [1, 1, 0.98, 0.65, 0.52],
        'MM': [1, 1, 1, 0.65, 0.52]
    }
    energy_data = {
        'nums': [10, 30, 50, 80, 100],
        'FCFS': [1.231, 1.336, 1.517, 1.407, 1.230],
        'OPT-DFST': [1.307, 1.401, 1.509, 1.297, 1.319],
        'MM': [1.275, 1.403, 1.360, 1.433, 1.251]
    }
    data = [v_data, pass_time_data, last_time_data, pass_rate_data, cpu_time_data, energy_data]
    titile_list = ['平均速度对比图', '通行时间对比图', '最后通过时间对比图', '通过率对比图', 'CPU计算时间对比图', '能耗对比图']
    ylabel_list = ['平均速度', '通行时间', '最后通过时间', '通过率', 'CPU计算时间', '能耗']
    for i in range(6):
        draw_figure(data[i], titile_list[i], ylabel_list[i])


def draw_figure(data, title_, y_label):
    plt.figure()
    # 设置Matplotlib的字符集
    plt.rcParams['font.sans-serif'] = 'SimHei'  # 指定中文字体（例如：黑体）'KaiTi'
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    # 设置横坐标和柱状图的位置
    x = data['nums']
    x_pos = range(len(x))
    # 调整柱状图宽度和位置
    bar_width = 0.2
    plt.bar(x_pos, data['FCFS'], width=bar_width, align='center', alpha=0.5, label='FCFS')
    plt.bar([p + bar_width for p in x_pos], data['OPT-DFST'], width=bar_width, align='center', alpha=0.5, label='OPT-DFST')
    plt.bar([p + 2 * bar_width for p in x_pos], data['MM'], width=bar_width, align='center', alpha=0.5, label='MM')
    # 设置图形的标题和标签
    plt.title(title_)
    plt.xlabel('车辆数目')
    plt.ylabel(y_label)
    # 设置横坐标刻度和标签
    plt.xticks([p + bar_width for p in x_pos], x)
    plt.legend()
    # 自动调整子图布局
    plt.tight_layout()
    # plt.show()
    plt.savefig(f'./../figures/{title_}.png')


if __name__ == '__main__':
    adjust_traj()
    # analysis()
    # analysis_all()
