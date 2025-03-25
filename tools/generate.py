import math
import os
import random

import pandas as _pd

from tools.car import Car
from tools.const_data import pos_dict, car_len, lane_id, car_nums

# 初始化车道对应车辆的字典
_lane_to_cars_dict = {lane: [] for lane in lane_id}
_lant_to_car_v = {lane: [] for lane in lane_id}


def _generate():
    cars_num_of_time = {}  # 每时刻产生多少辆车
    # 定义产生车辆的总时刻
    if car_nums <= 80:  # 车辆数小于80， 则按照10个时刻产生，
        total_time = 5 if car_nums <= 10 else 10
        # 前面每时刻产生多少辆车
        num_of_timestamp = car_nums // total_time
        # 最后一个时刻产生的车辆
        remainder = car_nums % 5 if car_nums <= 10 else car_nums % 10
        for t in range(total_time):
            cars_num_of_time[t] = num_of_timestamp
        for t in range(remainder):
            cars_num_of_time[t] += 1
    else:
        total_time = math.ceil(car_nums / 8)  # 每个时刻产生最大数量的车--8
        remainder = car_nums % 8
        for t in range(total_time - 1):
            cars_num_of_time[t] = 8
        cars_num_of_time[total_time - 1] = remainder
    print(f"总时刻{total_time}; 每个时刻产生多少辆车{cars_num_of_time}")
    # 初始车辆编号为1
    count = 1
    # 开始每时刻产生车辆
    for t in range(total_time):
        # 用一个列表存储该时刻产生车辆的车道号
        lanes_every_time = []
        # 每个时刻产生对应数量的车 car_num没用，只是为了循环，产生车辆而已
        for car_num in range(cars_num_of_time[t]):
            # 同一时刻产生的车不能在同一车道
            while True:
                # 给每辆车随机分配一个车道
                lane_selected = random.choice(lane_id)
                if lane_selected not in lanes_every_time:
                    # 将该时刻产生的车辆所在的车道号加入列表中
                    lanes_every_time.append(lane_selected)
                    break
            # 然后检查该车道是否已有车辆，以此确定车辆初始属性
            new_car = _check_and_gene(_lane_to_cars_dict, lane_selected)
            # 设置新车id编号 和 生成时刻
            new_car.id = count
            new_car.gene_time = t
            # 加入字典
            _lane_to_cars_dict[lane_selected].append(new_car)
            # 车辆编号+1
            count += 1
        # 首先此时是下一个时刻，原来的所车辆都应该前进一段距离
        if t != total_time - 1:   # 最后一个时刻不需要前行
            _move_one_step()
            # 移动完后再检查每个车辆是否与前车保持安全距离
            _adjust_pos()
    _check_all('last_check')
    for lane_, c_list in _lane_to_cars_dict.items():
        if c_list:
            print(f"{lane_}车道：")
            for c in c_list:
                print(c)


def _move_one_step():
    for lane_, c_list in _lane_to_cars_dict.items():
        # 判断该车道是否有车辆
        if c_list:
            for car in c_list:
                if lane_ in (11, 12, 13):
                    car.y = car.y + car.v
                elif lane_ in (21, 22, 23):
                    car.x = car.x - car.v
                elif lane_ in (31, 32, 33):
                    car.y = car.y - car.v
                else:
                    car.x = car.x + car.v


def _adjust_pos():
    for lane_, c_list in _lane_to_cars_dict.items():
        len_ = len(c_list)
        for i in range(len_ - 1, 0, -1):  # 倒叙遍历
            c2 = c_list[i]
            c1 = c_list[i - 1]
            need_dis_ = car_len + 2 * (c2.v - c1.v)
            if lane_ in (11, 12, 13):
                if c1.y - c2.y <= need_dis_:  # 调整前车的位置
                    c1.y = c2.y + need_dis_ + 0.5
            elif lane_ in (21, 22, 23):
                if (c2.x - c1.x) <= need_dis_:
                    c1.x = c2.x - need_dis_ - 0.5
            elif lane_ in (31, 32, 33):
                if (c2.y - c1.y) <= need_dis_:
                    c1.y = c2.y - need_dis_ - 0.5
            else:
                if (c1.x - c2.x) <= need_dis_:
                    c1.x = c2.x + need_dis_ + 0.5


def _check_and_gene(lane_dict: dict, l_id: int) -> Car:
    # 如果有车
    if lane_dict[l_id]:
        # 取出最后一辆
        last_car = lane_dict[l_id][-1]
        car = Car(0, l_id)
        if l_id in (11, 12, 13):
            dis = last_car.y + 200
            car.x = pos_dict[l_id]
            car.y = -200
        elif l_id in (21, 22, 23):
            dis = 225 - last_car.x
            car.x = 225
            car.y = pos_dict[l_id]
        elif l_id in (31, 32, 33):
            dis = 225 - last_car.y
            car.x = pos_dict[l_id]
            car.y = 225
        else:
            dis = last_car.x + 200
            car.x = -200
            car.y = pos_dict[l_id]
        # 后车最大速度满足安全距离约束
        opt_v = round((dis - car_len) / 2 + last_car.v, 2)
        # 在可行范围内给一个随机速度，这里最大速度设置了13，而不是16.67，最小速度设置了6，
        # 车长是5，速度为6，走1秒就走了6米，与后车的距离必须大于车长5米，但产生下一辆车时相距6米，最大速度为6.5
        rand_v = min(opt_v, 15)
        rand_v = random.uniform(7, rand_v)
        car.v = round(rand_v, 2)
        return car
    # 如果没车，直接生成对应属性
    else:
        # 生成9-16.67之间的随机数
        rand_v = random.uniform(7, 15)
        # 保留两位小数
        rand_v = round(rand_v, 2)
        if l_id in (11, 12, 13):
            return Car(0, l_id, rand_v, pos_dict[l_id], -200)
        elif l_id in (21, 22, 23):
            return Car(0, l_id, rand_v, 225, pos_dict[l_id])
        elif l_id in (31, 32, 33):
            return Car(0, l_id, rand_v, pos_dict[l_id], 225)
        else:
            return Car(0, l_id, rand_v, -200, pos_dict[l_id])


def _check_all(last):
    for lane_, c_list in _lane_to_cars_dict.items():
        if c_list and len(c_list) > 1:
            for i in range(1, len(c_list)):
                c2 = c_list[i]
                c1 = c_list[i - 1]
                l_ = car_len + 2 * (c2.v - c1.v)
                if lane_ in (11, 12, 13):
                    if (c1.y - c2.y) <= l_:
                        print(last, c2)
                elif lane_ in (21, 22, 23):
                    if (c2.x - c1.x) <= l_:
                        print(last, c2)
                elif lane_ in (31, 32, 33):
                    if (c2.y - c1.y) <= l_:
                        print(last, c2)
                else:
                    if (c1.x - c2.x) <= l_:
                        print(last, c2)


def _out_fun():
    out_dict = {'id': [], 'lane': [], 'v': [], 'x': [], 'y': []}
    for lane_, c_list in _lane_to_cars_dict.items():
        if c_list:
            for c in c_list:
                out_dict['id'].append(c.id)
                out_dict['lane'].append(c.lane)
                out_dict['v'].append(c.v)
                out_dict['x'].append(c.x)
                out_dict['y'].append(c.y)
    df = _pd.DataFrame(out_dict)
    df.sort_values(by='id', ascending=True, inplace=True)
    df.to_csv(f'{os.path.dirname(os.path.abspath(__file__))}/../files/cars_{car_nums}_init_data.csv', index=False)


def get_cars_data():
    _generate()
    _out_fun()


if __name__ == '__main__':
    get_cars_data()
