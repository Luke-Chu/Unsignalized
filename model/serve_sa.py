from model.model1 import _get_arrive_time, _get_cars_order
from model.model2 import _get_c_d
from model.model3 import _get_matching
from tools.init_car import arrive_time_dict


def get_fcfs_order():
    return _get_cars_order()


def get_actual_arr_time(cars_order: list) -> dict:
    assign_time = _get_arrive_time(cars_order)
    # 根据安排到达时间和最小到达时间作比较，取较大的一个
    return {c: max(t, arrive_time_dict[c]) for c, t in assign_time.items()}


def get_depth() -> dict:
    return _get_c_d()


def convert_to_order(select: str) -> list:
    # 该字典键是车id
    if select == 'OPT-DFST':
        depth_dict = get_depth()
    else:
        depth_dict = _get_matching()
    order_list = []
    # 键是深度
    depth_convert_dict = {x: [] for x in range(1, depth_dict.__len__())}
    for c_, d_ in depth_dict.items():
        depth_convert_dict[d_].append(c_)
    # 然后将同一深度的车辆根据到达时刻转换成列表
    for d_, cl_ in depth_convert_dict.items():
        if len(cl_) > 1:
            # 同一深度下多辆车，按到达时间排序后加入
            order_list.extend(sorted(cl_, key=lambda car: arrive_time_dict[car]))
        elif cl_:
            # 该深度下只有一辆车，直接加入即可
            order_list.append(cl_[0])
    return order_list


if __name__ == '__main__':
    print(convert_to_order())
