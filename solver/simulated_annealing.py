import copy
import math
import random
import time

from matplotlib import pyplot as plt

from model.serve_sa import get_actual_arr_time, convert_to_order, get_fcfs_order
from tools.const_data import car_nums
from tools.init_car import arrive_time_dict, cars_of_lane

# cl = get_fcfs_order()
# cl = [x for x in range(1, car_nums + 1)]
cl = convert_to_order('MM')

titles = [f'FCFS with SA', 'Improved FCFS with SA', 'OPT-DFST with SA', 'MM with SA']


def draw_opt_pic(iters_: list, opt_value: list, x_label: str, y_label: str):
    plt.figure()
    # 绘制图形
    plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman']  # 宋体和Time New Roman
    plt.plot(iters_, opt_value, linestyle='-')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(f'{car_nums}' + titles[1])
    # plt.grid(True)
    plt.show()


def cal_total_delay(cars_order: list) -> float:
    total_delay_ = 0
    # 根据通行次序得到车辆实际到达时刻
    actual_arr_time = get_actual_arr_time(cars_order)
    for c in cars_order:
        total_delay_ += actual_arr_time[c] - arrive_time_dict[c]
    return total_delay_


# 获取车辆次序列表索引
def get_idx(car_list: list) -> dict:
    idx_dict = {}
    for idx, c in enumerate(car_list):
        idx_dict[c] = idx
    return idx_dict


# 检查次序是否可行（不可超车）
def check_is_feasible(cars_order: list) -> bool:
    idx_dict = get_idx(cars_order)
    for lane_, cars in cars_of_lane.items():
        i = 0
        for c in cars:
            if idx_dict[c] < i:
                return False
            i = idx_dict[c]
    return True


# 产生新顺序方案
def gen_new_orders(old_order: list) -> list:
    new_order = copy.deepcopy(old_order)
    rand_idx = random.randint(0, car_nums - 1)
    # 是第一个就往后放
    if rand_idx == 0:
        temp = new_order[rand_idx]
        new_order[rand_idx] = new_order[rand_idx + 1]
        new_order[rand_idx + 1] = temp
    else:  # 其他都往前放
        temp = new_order[rand_idx]
        new_order[rand_idx] = new_order[rand_idx - 1]
        new_order[rand_idx - 1] = temp
    return new_order


def simulated_annealing(max_iter=500, initial_temp=1000, cooling_rate=0.95, max_gen=1000):
    # 初始化
    cur_order = cl
    cur_delay = cal_total_delay(cur_order)
    best_order = cur_order
    min_delay = cur_delay
    # 初始温度
    temp = initial_temp
    # 定义一些中间变量用于画图
    pic_min_delay = [min_delay]
    pic_iters = [0]
    iters_num = 1  # 迭代次数
    # 记录迭代时间
    start_time = time.time()
    better_values = [min_delay]
    end_times = [start_time]
    while max_gen > 1:  # 外层循环，
        for i in range(max_iter):  # 内层循环
            # 生成新的解决方案
            new_order = cur_order
            temp_order = gen_new_orders(cur_order)
            if check_is_feasible(temp_order):
                new_order = temp_order
            # 计算新路径和旧路径的距离差
            new_delay = cal_total_delay(new_order)
            delta_delay = new_delay - cur_delay
            # 距离差小于零说明更优，否则以一定概率接受较差解
            if delta_delay < 0 or random.random() < math.exp(-delta_delay / temp):
                cur_order = new_order
                cur_delay = new_delay
                # 如果当前解比最优解更好，则更新最优解
                if cur_delay < min_delay:
                    best_order = cur_order
                    min_delay = cur_delay
                    better_values.append(min_delay)
                    end_times.append(time.time())
                    # print('新的最小延时：', min_delay)
                    # print('新的最优次序：', best_order)
        # if iters_num % 10 == 0:
        #     print(iters_num, min_delay)
        # 降温
        temp *= cooling_rate
        max_gen -= 1
        iters_num += 1
        # 把每次外层循环找到的最短距离保存
        pic_min_delay.append(min_delay)
        pic_iters.append(iters_num)
    # 调用函数画出迭代次数与优化目标关系图
    draw_opt_pic(pic_iters, pic_min_delay, "Number of iterations", "Minimum total delay")
    draw_opt_pic([d - start_time for d in end_times], better_values, "Iteration time", "Minimum total delay")
    return best_order, min_delay


if __name__ == '__main__':
    print(f"初始次序：{cl}")
    print(f"初始总延时：{cal_total_delay(cl)}")
    opt_order, opt_delay = simulated_annealing()
    print(f"最优次序：{opt_order}")
    print(f"最小总延时：{opt_delay}")
