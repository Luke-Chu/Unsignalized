import os

import numpy as np

from tools.const_data import lane_id, plan_time
from tools.init_car import car_nums, pd, cars_of_lane, lane_of_car


def print_gams_var_code():
    print(f'Sets    t  时间  /1*{plan_time}/')
    for lane_, c_list in cars_of_lane.items():
        print(f'\tc{lane_}  {lane_}车道编号  /1*{c_list.__len__()}/')
    print(';')
    abso_path = os.path.dirname(os.path.abspath(__file__))
    with open(f"{abso_path}/../files/gams_basic_code1.txt", 'r', encoding='utf-8') as file:
        code = file.read()
    print(code)


def print_gams_equ_code():
    t_ = plan_time
    abso_path = os.path.dirname(os.path.abspath(__file__))
    with open(f"{abso_path}/../files/gams_basic_code2.txt", 'r', encoding='utf-8') as file:
        code = file.read()
    print(code)
    print(f'object..        obj =e= (sum(c11, x11("1", c11) - x11("{t_}", c11)) + sum(c11, y11("{t_}", c11) - y11("1", '
          f'c11)) + sum(c12, y12("{t_}", c12) - y12("1", c12)) +')
    print(f'{"":23} sum(c21, y21("1", c21) - y21("{t_}", c21)) + sum(c21, x21("1", c21) - x21("{t_}", c21)) '
          f'+ sum(c22, x22("1", c22) - x22("{t_}", c22)) +')
    print(f'{"":23} sum(c33, y33("1", c33) - y33("{t_}", c33)) + sum(c33, x33("{t_}", c33) - x33("1", c33)) '
          f'+ sum(c32, y32("1", c32) - y32("{t_}", c32)) +')
    print(f'{"":23} sum(c43, y43("{t_}", c43) - y43("1", c43)) + sum(c43, x43("{t_}", c43) - x43("1", c43)) '
          f'+ sum(c42, x42("{t_}", c42) - x42("1", c42))) / ({car_nums} * delta * {t_});')
    print()
    print()


def print_gams_out_code(model):
    print(f'display x11.l, y11.l, v11.l, y12.l, v12.l, x21.l, y21.l, v21.l, x22.l, v22.l, '
          f'y32.l, v32.l, x33.l, y33.l, v33.l, x42.l, v42.l, x43.l, y43.l, v43.l;')
    print(f'Model no_signal /all/;')
    print(f'solve no_signal maximizing obj using LP;')
    print()
    print()
    print(f'file results /model{model}_{car_nums}.txt/;')
    print(f'*results.ap = 1;')
    print(f'put results;')
    print(f"loop(c11, loop(t, put '11': 8; put c11.tl: 8; put t.tl: 8; "
          f"put x11.l(t, c11): 12:3, y11.l(t, c11): 12:3, v11.l(t, c11)/));")
    print(f"loop(c12, loop(t, put '12': 8; put c12.tl: 8; put t.tl: 8; "
          f"put fix5: 12:3, y12.l(t, c12): 12:3, v12.l(t, c12)/));")
    print(f"loop(c21, loop(t, put '21': 8; put c21.tl: 8; put t.tl: 8; "
          f"put x21.l(t, c21): 12:3, y21.l(t, c21): 12:3, v21.l(t, c21)/));")
    print(f"loop(c22, loop(t, put '22': 8; put c22.tl: 8; put t.tl: 8; "
          f"put x22.l(t, c22): 12:3, fix5: 12:3, v22.l(t, c22)/));")
    print(f"loop(c32, loop(t, put '32': 8; put c32.tl: 8; put t.tl: 8; "
          f"put fix2: 12:3, y32.l(t, c32): 12:3, v32.l(t, c32)/));")
    print(f"loop(c33, loop(t, put '33': 8; put c33.tl: 8; put t.tl: 8; "
          f"put x33.l(t, c33): 12:3, y33.l(t, c33): 12:3, v33.l(t, c33)/));")
    print(f"loop(c42, loop(t, put '42': 8; put c42.tl: 8; put t.tl: 8; "
          f"put x42.l(t, c42): 12:3, fix2: 12:3, v42.l(t, c42)/));")
    print(f"loop(c43, loop(t, put '43': 8; put c43.tl: 8; put t.tl: 8; "
          f"put x43.l(t, c43): 12:3, y43.l(t, c43): 12:3, v43.l(t, c43)/));")


def print_gams_init_code(ms: str = None):
    abso_path = os.path.dirname(os.path.abspath(__file__))
    if ms is not None:
        _file_path = f'{abso_path}/../files/xin_model{ms}_init_data_{car_nums}.csv'
    else:
        _file_path = f'{abso_path}/../files/cars_{car_nums}_init_data.csv'
    _data_df = pd.read_csv(_file_path)
    _data_df['x'] = _data_df['x'].round(3)
    _data_df['y'] = _data_df['y'].round(3)
    for _lane in lane_id:
        _df = _data_df[_data_df['lane'] == _lane]
        v_list = _df['v'].to_list()
        x_list = _df['x'].to_list()
        y_list = _df['y'].tolist()
        print(f"*{_lane}车道的初始化数据----------")
        if _lane in (11, 21, 33, 43):  # 需要打印三个数据：x,y,v
            _print_each('v', v_list, _lane)
            _print_each('x', x_list, _lane)
            _print_each('y', y_list, _lane)
        elif _lane in (12, 32):  # 需要打印v和y
            _print_each('v', v_list, _lane)
            _print_each('y', y_list, _lane)
        else:  # 22 42 需要打印v和x
            _print_each('v', v_list, _lane)
            _print_each('x', x_list, _lane)


def print_nm_code(arrive_time: dict, cross_time: int):
    # 设置总时刻
    total_t = plan_time
    # 初始化两个字典，存储n和m
    n_dict = {}
    m_dict = {}
    for lane, cars in cars_of_lane.items():
        n_dict[lane] = np.zeros((total_t, cars.__len__()))
        m_dict[lane] = np.full((total_t, cars.__len__()), 1)
    # 通过切片操作赋值
    for car_id, arr_t in arrive_time.items():
        # 获取该车所在车道
        car_lane = lane_of_car[car_id]
        index_of_car = cars_of_lane[car_lane].index(car_id)
        n_dict[car_lane][arr_t - 1:, index_of_car] = 1
        # 离开时间
        out_t = arr_t + cross_time
        m_dict[car_lane][out_t - 1:, index_of_car] = 0
    for lane, cars in cars_of_lane.items():
        """"输出整数变量n"""
        print("table    n%d(t, c%d)  %d车道的车辆是否进入交叉口的整数变量" % (lane, lane, lane))
        print("%12s" % "", end="")
        # 第一行
        for id_ in range(cars.__len__()):
            print("%-4d" % (id_ + 1), end="")
        print()
        # 剩下行
        for t in range(total_t):
            print("%8s%-4d" % ("", t + 1), end="")
            for i in range(cars.__len__()):
                print("%-4d" % n_dict[lane][t][i], end="")
            print()
        print(";")
        """"输出整数变量m"""
        print("table    m%d(t, c%d)  %d车道的车辆是否离开交叉口的整数变量" % (lane, lane, lane))
        print("%12s" % "", end="")
        # 第一行
        for id_ in range(cars.__len__()):
            print("%-4d" % (id_ + 1), end="")
        print()
        # 剩下行
        for t in range(total_t):
            print("%8s%-4d" % ("", t + 1), end="")
            for i in range(cars.__len__()):
                print("%-4d" % m_dict[lane][t][i], end="")
            print()
        print(";")


def _print_each(flag: str, ele: list, lane_: str):
    for index, e in enumerate(ele):
        print(f'{flag}{lane_}.fx("1", "{index + 1}") = {e};')
    print()


def print_analysis_data(ml: str, arr_d: dict, cross_t: int):
    print(f"每辆车的到达时刻:")
    count = 1
    for car_id in range(1, car_nums + 1):
        print(f'车{car_id:<2}: {arr_d[car_id]:>2}到达', end="  ")
        if count % 5 == 0:
            print()
        count += 1
    # 打印最先到达，和最后通过时间
    min_arrive_time = min(arr_d.values())
    max_arrive_time = max(arr_d.values())
    print(f"model{ml}最先到达：{min_arrive_time}; 最后到达：{max_arrive_time}; 最后通过：{max_arrive_time + cross_t}")
    # 打印规划时间内通过了多少车
    count_pass = sum(1 for value in arr_d.values() if value + cross_t <= plan_time)
    count_no_pass = sum(1 for value in arr_d.values() if value + cross_t > plan_time)
    print(f'model{ml}规划{car_nums}辆车, {plan_time}时刻：{count_pass}辆车通过，{count_no_pass}辆车没通过')


if __name__ == '__main__':
    # print_gams_init_code()
    print_gams_var_code()
    print_gams_equ_code()
    # print_gams_out_code()
