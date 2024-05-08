import copy
import os
import sys

import networkx as nx

from tools.const_data import car_nums, un_conflict_lane
from tools.init_car import cars_of_lane, car_list, arrive_time_dict, lane_of_car

_t_cross = 4
car_index_in_matching = {}


def _get_matching():
    print("每个车道的车辆集合", cars_of_lane)
    # 定义无向图
    G = nx.Graph()
    # 添加结点
    G.add_nodes_from([i for i in range(1, car_nums + 1)])
    # 添加边
    for car in car_list:
        # G.add_node(car)
        car_id = car.id
        lane = car.lane
        # 找到该车道无冲突的车道集合
        un_conflict_lanes = un_conflict_lane[lane]
        # 然后对每一个无冲突车道遍历车辆
        for un_con_lane in un_conflict_lanes:
            # 取出该车到所有车辆
            cars = cars_of_lane[un_con_lane]
            # 遍历车辆，并将其加入车辆的无冲突集合
            for c in cars:
                G.add_edge(car_id, c)
    # 调函数，最大匹配算法
    matching = nx.algorithms.matching.max_weight_matching(G)
    # sorted_matching = sorted(matching)
    matching = switch_matching(list(matching))
    print("最大匹配对:")
    count = 1
    for m in matching:
        print(f'({m[0]:>2},{m[1]:<2})', end="  ")
        if count % 5 == 0:
            print()
        count += 1
    print()
    # 计算深度
    return _get_depth(matching)


def get_car_index(matching: list):
    for index, match in enumerate(matching):
        car_index_in_matching[match[0]] = (index, 0)
        car_index_in_matching[match[1]] = (index, 1)


def sort_matching(matching):
    for index, match in enumerate(matching):
        if match[0] > match[1]:
            matching[index] = (match[1], match[0])
    return sorted(matching)


def switch_matching(matching: list):
    new_matching = sort_matching(matching)
    get_car_index(new_matching)
    lane_to_car = copy.deepcopy(cars_of_lane)
    len_ = len(new_matching)
    for index in range(len_):
        match = new_matching[index]
        tup2 = match[1]
        # 取车道lane
        tup2_lane = lane_of_car[tup2]
        first_car = lane_to_car[tup2_lane][0]
        # 如果匹配对的第二辆车不是所在车道第一辆车，则进行交换，
        if tup2 != first_car:
            # 将其交换位置
            new_matching[index] = (match[0], first_car)
            # 取first_car的索引
            first_index = car_index_in_matching[first_car]
            temp_match = new_matching[first_index[0]]
            if first_index[1] == 0:
                new_matching[first_index[0]] = (tup2, temp_match[1])
            else:
                new_matching[first_index[0]] = (temp_match[0], tup2)
        lane_to_car[tup2_lane].pop(0)
        lane_to_car[lane_of_car[match[0]]].pop(0)
        # 重新排序
        new_matching = sort_matching(new_matching)
        get_car_index(new_matching)
    return new_matching


def _get_depth(matching: list):
    depth = {i: None for i in range(car_nums + 1)}
    depth[0] = 0
    for index, match in enumerate(matching):
        tup1, tup2 = match
        depth[tup1] = index + 1
        depth[tup2] = index + 1
    for id_, d in depth.items():
        if d is None:
            depth[id_] = len(matching) + 1
    for i in range(1, car_nums + 1):
        print(f"结点{i:<2}:深度{depth[i]:<2}", end='\t\t')
        if i % 5 == 0:
            print()
    del depth[0]
    return depth
    # 最先到达时间默认为第一辆车
    # min_ = arrive_time_dict[3] + 1
    # min_ = 16
    # # 设置一个字典存储每个结点的到达时刻
    # arrive_dict = {}
    # for c_id, d_ in depth.items():
    #     arrive_dict[c_id] = (d_ - 1) * _t_cross + min_
    # # 删除0结点的到达时间
    # del arrive_dict[0]
    # # 打印分析数据
    # from tools.print_code import print_analysis_data
    # print_analysis_data('3', arrive_dict, _t_cross)
    # _print_gams_file3(arrive_dict)


def _print_gams_file3(arrive_time: dict):
    from tools import print_code
    saved_stdout = sys.stdout  # 保存标准输出流
    f = open(f"{os.path.dirname(os.path.abspath(__file__))}/../gams_files/model3_{car_nums}.gms", "w", encoding='utf-8')
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
    print_code.print_gams_out_code('3')
    sys.stdout = saved_stdout  # 恢复标准输出流
    f.close()


def run_model3():
    _get_matching()


if __name__ == '__main__':
    _get_matching()


def _edmonds_algorithm(graph):
    matching = {}
    unmatched_nodes = set(graph.keys())

    def dfs(node, parent):
        if node in visited:
            return False
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor != parent:
                if neighbor in unmatched_nodes:
                    unmatched_nodes.remove(neighbor)
                    matching[node] = neighbor
                    matching[neighbor] = node
                    return True
                elif dfs(matching[neighbor], neighbor):
                    matching[node] = neighbor
                    matching[neighbor] = node
                    return True
        return False

    while len(unmatched_nodes) > 0:
        node = unmatched_nodes.pop()
        visited = set()
        dfs(node, None)
    return matching
