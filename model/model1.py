import os
import sys
from collections import deque
from typing import List

from tools.car import Car
from tools.const_data import car_nums, conflict_lane
from tools.init_car import car_list, arrive_time_dict, lane_of_car

# 通过交叉口的时间设置为2秒，在GAMS中离散时间为0.5秒一个时刻
_t_cross: int = 2
# 同车道先后通过交叉口的时间间隔
_same_lane_arr_interval = 2


def _get_cars_order():
    order_cars = sorted(car_list, key=lambda car: car.min_arrive_time())
    print("初始顺序")
    for index, c in enumerate(order_cars):
        print(f"{index + 1: <2}: {c.id: <2}({c.lane})车通过，到达时间{c.min_arrive_time(): <9f}，当前速度{c.v: <5f}")
    # 调整正确的顺序
    return _adjust_order(order_cars)


def _adjust_order(old_order: List[Car]):
    # 字典，8个键，键值为队列类型，方便取出判断
    visited_dict_deque = {11: deque(), 12: deque(), 21: deque(), 22: deque(),
                          32: deque(), 33: deque(), 42: deque(), 43: deque()}
    # 一个仅存放车辆索引的列表，这也是我们需要得到的东西
    car_id_order = []
    """遍历初始化"""
    for c in old_order:
        car_id = c.id
        car_lane = c.lane
        # 访问字典
        visited_dict_deque[car_lane].append(car_id)
        # 添加索引
        car_id_order.append(car_id)
    # 将每车道车辆按照编号大小排个序, 得到每个车道正确的通过顺序
    for car_lane, car_id_que in visited_dict_deque.items():
        visited_dict_deque[car_lane] = deque(sorted(car_id_que))
    print(f"初始车辆顺序---")
    count = 1
    for o in car_id_order:
        print(f'{o:<2}', end=" -> ")
        if count % 10 == 0:
            print()
        count += 1
    """对car_id_order遍历，调整不合理的顺序"""
    index = 0
    while index < len(car_id_order):
        # 取id
        c_id = car_id_order[index]
        # 取lane
        car_lane = lane_of_car[c_id]
        # 判断该车是不是所在车道剩余车辆的第一辆车
        first_car_of_lane = visited_dict_deque[car_lane][0]
        if c_id == first_car_of_lane:
            # 如果是, 队列弹出一个元素
            visited_dict_deque[car_lane].popleft()
            index += 1
        else:  # 如果不是，需要将其调整到所在车道剩余车辆第一辆车的后面
            # 先获取该元素在列表中的索引
            index_of_car = car_id_order.index(c_id)
            index_of_first = car_id_order.index(first_car_of_lane)
            # 将该元素插入到第一辆车后面
            car_id_order.insert(index_of_first + 1, c_id)
            # 再将该元素原来位置删除
            car_id_order.pop(index_of_car)
    print(car_id_order)
    print(f"调整后的车辆顺序:")
    for o in car_id_order:
        print(f'{o:<2}', end=" -> ")
        if count % 10 == 0:
            print()
        count += 1
    """根据次序确定到达时间"""
    return car_id_order
    # _get_arrive_time(car_id_order)


# 开始分析每辆车与前车是否有冲突，如果没有则在同一层，可以同时通过
def _get_arrive_time(car_id_order: list) -> dict:
    # 得到最终顺序后，确定第一辆车的到达时刻
    first_arrive_time = arrive_time_dict[car_id_order[0]]
    # first_arrive_time = 6
    # 定义到达时刻的字典
    arrive_dict = {}
    # 维护一个访问字典
    visited = {11: [], 12: [], 21: [], 22: [], 32: [], 33: [], 42: [], 43: []}
    """遍历每一辆车，确定每辆车的到达时间"""
    for i in car_id_order:
        # 获取lane
        _lane = lane_of_car[i]
        # 该车道的冲突车道集合列表
        conflict_lanes = conflict_lane[_lane]
        # 设置一个布尔变量，表示冲突车道是否有车
        con_is_empty = True
        # 设置一个变量用于存储冲突车辆最后的到达时刻
        last_time_of_con_lanes = 0
        """下面的for循环用于找冲突车道最后一辆车的最后到达时间"""
        for c_l in conflict_lanes:
            # 如果该车道已有车辆
            if visited[c_l]:
                # 说明该车道有车
                con_is_empty = False
                # 取最后一辆车
                last_id_of_con_lane = visited[c_l][-1]
                # 取该车到达时刻
                last_time_of_last_car = arrive_dict[last_id_of_con_lane]
                if last_time_of_last_car > last_time_of_con_lanes:
                    last_time_of_con_lanes = last_time_of_last_car
        """然后设置一个布尔变量用于判断该车是否是所在车道的第一辆车"""
        is_first_car = True
        last_time_of_same_lane = 0
        if visited[_lane]:
            is_first_car = False
            # 取所在车道的最后一辆车的到达时间
            last_time_of_same_lane = arrive_dict[visited[_lane][-1]]
        """下面分为四种情况对该车正确的到达时间进行处理"""
        if (con_is_empty, is_first_car) == (False, False):  # 如果冲突车道有车，所在车道有前车，这对应大多数情况
            # 比较冲突车道最后一辆车和当前车道的最后一辆车的到达时间
            if last_time_of_con_lanes > last_time_of_same_lane:
                arrive_dict[i] = last_time_of_con_lanes + _t_cross
            else:
                arrive_dict[i] = last_time_of_same_lane + _same_lane_arr_interval
        elif (con_is_empty, is_first_car) == (False, True):  # 冲突车道有车，所在车道没车，这对应少数情况
            arrive_dict[i] = last_time_of_con_lanes + _t_cross
        elif (con_is_empty, is_first_car) == (True, False):  # 冲突车道没车，所在车道有车，这对应极少数情况
            arrive_dict[i] = last_time_of_same_lane + _same_lane_arr_interval
        else:  # 冲突车道没车，所在车道没车，这对应极少数情况，是最先通过的车辆
            arrive_dict[i] = first_arrive_time
        """循环最后还需要更新访问字典"""
        visited[_lane].append(i)
    # 打印分析数据
    # from tools.print_code import print_analysis_data
    # print_analysis_data('1', arrive_dict, _t_cross)
    # print()
    # _print_gams_file1(arrive_dict)
    return arrive_dict


def _print_gams_file1(arrive_time: dict):
    from tools import print_code
    # 打印输出到文件
    saved_stdout = sys.stdout  # 保存标准输出流
    f = open(f"{os.path.dirname(os.path.abspath(__file__))}/../gams_files/minlp_model1_{car_nums}.gms", "w", encoding='utf-8')
    # 将标准输出流定向到文件
    sys.stdout = f
    # 先输出变量部分
    print_code.print_gams_var_code()
    # 输出整数变量
    print_code.print_nm_code(arrive_time, _t_cross)
    # 输出方程
    print_code.print_gams_equ_code()
    # 输出初始化部分
    print_code.print_gams_init_code()
    # 输出最后文件输出部分
    print_code.print_gams_out_code('1')
    # 恢复标准输出流
    sys.stdout = saved_stdout
    f.close()


def run_model1():
    _get_cars_order()


if __name__ == '__main__':
    _get_cars_order()
