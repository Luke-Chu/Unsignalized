import os
import sys

import numpy as np

from tools.const_data import conflict_lane
from tools.init_car import car_nums, car_list, arrive_time_dict

_t_cross = 2


def _get_c_d() -> dict:
    # 初始化冲突集和发散集
    conflict_set = {i: [] for i in range(1, car_nums + 1)}
    divergent_set = {i: [0] for i in range(1, car_nums + 1)}
    # 已经遍历的车
    visited_car = []
    for car in car_list:
        lane = car.lane
        car_id = car.id
        for c in visited_car:
            c_lane = c.lane
            c_id = c.id
            # 如果前车在当前车的冲突域内，则将该车加入当前车的冲突集
            if c_lane in conflict_lane[lane]:
                conflict_set[car_id].append(c_id)
            # 如果是同一个车道，则加入其发散集
            if c_lane == lane:
                divergent_set[car_id].append(c_id)
        # 将该车加入已检查集合
        visited_car.append(car)
    # 遍历输出
    for i in range(1, car_nums + 1):
        print("C%-3d = " % i, "%-76s" % conflict_set[i], "D%-3d = " % i, divergent_set[i])
    return _cal_depth(conflict_set, divergent_set)


def _conflict_digraph(conflict_set: list, divergent_set: list):
    num_nodes = car_nums + 1
    # 定义单向边集合
    uni_edges = set()
    # 定义双向边集合
    bi_edges = set()
    # 创建一个邻接矩阵
    adj_matrix = np.zeros((num_nodes, num_nodes))

    for j in range(num_nodes):
        for i in divergent_set[j]:  # 添加单向边
            if i < j:
                adj_matrix[i][j] = 1
                uni_edges.add((i, j))
        for i in conflict_set[j]:   # 添加双向边
            if i < j:
                adj_matrix[i][j] = 1
                adj_matrix[j][i] = 1
                bi_edges.add((i, j))


def _cal_depth(conflict_set: dict, divergent_set: dict) -> dict:
    # 初始化深度
    depth = {i: int for i in range(car_nums + 1)}
    depth[0] = 0
    parent_nodes = {i: int for i in range(car_nums + 1)}
    parent_nodes[0] = 0
    for i in range(1, car_nums + 1):
        # 找父节点最大深度
        max_depth = 0
        for j in divergent_set[i]:
            if depth[j] > max_depth:
                max_depth = depth[j]
        # 找深度并集
        union_depth = set()
        for j in conflict_set[i]:
            union_depth.add(depth[j])
        # i节点最优深度：不能小于父节点最大深度max_depth，
        # 不能与冲突集深度并集union_depth有交集，尽可能小
        di = max_depth + 1
        while True:
            if di in union_depth:
                di += 1
            else:
                depth[i] = di
                break
        # 确定父节点
        parent_depth = di - 1
        found = False
        for j in conflict_set[i]:
            if depth[j] == parent_depth:
                parent_nodes[i] = j
                found = True
                break
        if not found:
            for j in divergent_set[i]:
                if depth[j] == parent_depth:
                    parent_nodes[i] = j
                    found = True
                    break
        if not found:
            print("在节点%d的冲突集和发散集中没找到合适的父节点" % i)
            for k in range(1, 32):
                if depth[k] == parent_depth:
                    parent_nodes[i] = k
    # 输出节点深度
    count = 1
    for i in range(1, car_nums + 1):
        print(f"结点{i:<2}: 深度为{depth[i]:<2} 父结点为{parent_nodes[i]:<3}", end="  ")
        if count % 3 == 0:
            print()
        count += 1
    del depth[0]
    return depth
    # 最先到达时间默认为第一辆车
    # min_ = arrive_time_dict[1] + 1
    # min_ = 17
    # # 设置一个字典存储每个结点的到达时刻
    # arrive_dict = {}
    # for c_id, d_ in depth.items():
    #     arrive_dict[c_id] = (d_ - 1) * _t_cross + min_
    # # 删除0结点的到达时间
    # del arrive_dict[0]
    # 打印分析数据
    # from tools.print_code import print_analysis_data
    # print_analysis_data('2', arr_d=arrive_dict, cross_t=_t_cross)
    # print()
    # _print_gams_file2(arrive_dict)


def _print_gams_file2(arrive_time: dict):
    from tools import print_code
    saved_stdout = sys.stdout  # 保存标准输出流
    f = open(f"{os.path.dirname(os.path.abspath(__file__))}/../gams_files/model2_{car_nums}.gms", "w", encoding='utf-8')
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
    print_code.print_gams_out_code('2')
    sys.stdout = saved_stdout  # 恢复标准输出流
    f.close()


def run_model2():
    _get_c_d()


if __name__ == '__main__':
    _get_c_d()
