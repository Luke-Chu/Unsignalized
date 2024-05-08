import math
import os

import pandas as pd
from tools.const_data import car_nums
from tools.car import Car


# 读取生成车辆的数据文件
_file_name = f"{os.path.dirname(os.path.abspath(__file__))}/../files/cars_{car_nums}_init_data.csv"
_data_df = pd.read_csv(_file_name).sort_values(by='id', ascending=True)
# 车对应的车道号
lane_of_car = {}
# 先存储每辆车的预计到达时间
arrive_time_dict = {}
# 每个车道的车辆集合
cars_of_lane = {11: [], 12: [], 21: [], 22: [], 32: [], 33: [], 42: [], 43: []}
# 初始化车辆对象
car_list = []
# 遍历文件，初始化相关数据
for _index, _row in _data_df.iterrows():
    # 车id
    _id = int(_row['id'])
    # 得到车道号
    _lane = int(_row['lane'])
    # 得到该车的速度
    _v = round(_row['v'], 3)
    # 得到该车的x位置
    _x = round(_row['x'], 3)
    # 得到该车的y位置
    _y = round(_row['y'], 3)
    # 生成车辆对象
    _car = Car(_id, _lane, _v, _x, _y)
    # 计算到达时间
    # arrive_time_dict[_id] = math.ceil(_car.min_arrive_time() * 2)
    arrive_time_dict[_id] = _car.min_arrive_time()
    # 加入列表
    car_list.append(_car)
    # 将该车加入对应车道列表
    cars_of_lane[_lane].append(_id)
    # 获取该车所对的车道号
    lane_of_car[_id] = _lane


if __name__ == '__main__':
    print(f'{car_nums}辆车：')
    for _l, _cs in cars_of_lane.items():
        print(f'{_l}车道：', end="[")
        for c in _cs:
            print(c, end=" ")
        print("]")
