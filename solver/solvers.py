import time

import numpy as np
import pandas as pd
from pyomo.environ import *
from pyomo.opt import SolverFactory
from typing import List

from tools.car import Car

Times = [i for i in range(1, 11)]
i = [i for i in range(1, 5)]
j = [j for j in range(1, 4)]
B = 2000
delta = 0.5
r_left = 15.625
r_right = 1.875
width = 25
L = 4.5


class MySolver:
    @staticmethod
    def solve(cars: List[Car], index: list, lane_dict: dict):
        model = ConcreteModel()
        # 设置位置决策变量
        model.x = Var(Times, index, within=Reals, initialize=0)
        model.y = Var(Times, index, within=Reals, initialize=0)
        # 第一段
        model.x1 = Var(Times, index, within=Reals)
        model.y1 = Var(Times, index, within=Reals)
        # 第二段
        model.x2 = Var(Times, index, within=Reals)
        model.y2 = Var(Times, index, within=Reals)
        # 第二段角度
        model.angle_l = Var(Times, index, within=NonNegativeReals, bounds=(0, np.pi / 2), initialize=0)
        model.angle_r = Var(Times, index, within=NonNegativeReals, bounds=(0, np.pi / 2), initialize=0)
        # 第三段
        model.x3 = Var(Times, index, within=Reals)
        model.y3 = Var(Times, index, within=Reals)
        # 设置速度决策变量
        model.v = Var(Times, index, within=PositiveReals, bounds=(0, 16.67), initialize=1)
        # 设置加速度
        model.a = Var(Times, index, within=Reals, bounds=(-6, 4), initialize=0)
        # 定义整数变量：n进入交叉口临界点、m离开交叉口临界点
        model.n = Var(Times, index, within=Binary, initialize=0)
        model.m = Var(Times, index, within=Binary, initialize=1)
        model.z = Var(Times, index, within=Binary, initialize=0)

        # 初始化位置、速度
        for c in cars:
            model.x[1, c.id].fix(c.x)
            model.y[1, c.id].fix(c.y)
            model.v[1, c.id].fix(c.v)

        # 整数变量约束
        model.n_cons = ConstraintList()
        model.m_cons = ConstraintList()
        # 速度约束
        model.v_cons = ConstraintList()
        # 安全车距约束
        model.dis_cons = ConstraintList()
        # 轨迹约束
        model.angle_l_cons = ConstraintList()
        model.angle_r_cons = ConstraintList()
        model.x_cons = ConstraintList()
        model.y_cons = ConstraintList()
        # 次序约束
        model.order_cons = ConstraintList()

        # 速度相关约束
        for car in cars:
            for t in Times:
                # model.v_cons.add(model.v[t, car.id] * model.n[t, car.id] * model.m[t, car.id] <= 12)
                model.v_cons.add(model.v[t, car.id] * model.z[t, car.id] <= 12)
                model.v_cons.add(model.z[t, car.id] == model.n[t, car.id] * model.m[t, car.id])
                # model.v_cons.add(model.z[t, car.id] <= model.n[t, car.id])
                # model.v_cons.add(model.z[t, car.id] <= model.m[t, car.id])
                # model.v_cons.add(model.z[t, car.id] >= model.n[t, car.id] + model.m[t, car.id] - 1)
            for t in Times[: -1]:
                model.v_cons.add(model.v[t + 1, car.id] == model.v[t, car.id] + model.a[t, car.id] * delta)

        # 确定整数变量
        for c in cars:
            id_ = c.id
            i_ = c.i
            j_ = c.j
            for t in Times:
                if i_ == 1:  # 1车道
                    # n的约束
                    model.n_cons.add(model.y[t, id_] - B * model.n[t, id_] <= 0)
                    model.n_cons.add(model.y[t, id_] - B * (model.n[t, id_] - 1) >= 0)
                    if j_ == 1:  # 左转
                        # m的约束
                        model.m_cons.add(model.x[t, id_] - B * model.m[t, id_] <= 0)
                        model.m_cons.add(model.x[t, id_] - B * (model.m[t, id_] - 1) >= 0)
                    elif j_ == 2:  # 直行
                        # m的约束
                        model.m_cons.add(25 - model.y[t, id_] <= B * model.m[t, id_])
                        model.m_cons.add(25 - model.y[t, id_] >= B * (model.m[t, id_] - 1))
                    else:
                        # m的约束
                        model.m_cons.add(25 - model.x[t, id_] <= B * model.m[t, id_])
                        model.m_cons.add(25 - model.x[t, id_] >= B * (model.m[t, id_] - 1))
                elif i_ == 2:  # 2车道
                    # n的约束
                    model.n_cons.add(25 - model.x[t, id_] <= B * model.n[t, id_])
                    model.n_cons.add(25 - model.x[t, id_] >= B * (model.n[t, id_] - 1))
                    if j_ == 1:  # 左转
                        # m的约束
                        model.m_cons.add(model.y[t, id_] <= B * model.m[t, id_])
                        model.m_cons.add(model.y[t, id_] >= B * (model.m[t, id_] - 1))
                    if j_ == 2:  # 直行
                        model.m_cons.add(model.x[t, id_] <= B * model.m[t, id_])
                        model.m_cons.add(model.x[t, id_] >= B * (model.m[t, id_] - 1))
                    else:  # 右转
                        model.m_cons.add(25 - model.y[t, id_] <= B * model.m[t, id_])
                        model.m_cons.add(25 - model.y[t, id_] >= B * (model.m[t, id_] - 1))
                elif i_ == 3:  # 3车道
                    # n的约束
                    model.n_cons.add(25 - model.y[t, id_] <= B * model.n[t, id_])
                    model.n_cons.add(25 - model.y[t, id_] >= B * (model.n[t, id_] - 1))
                    if j_ == 1:  # 右转
                        model.m_cons.add(model.x[t, id_] <= B * model.m[t, id_])
                        model.m_cons.add(model.x[t, id_] >= B * (model.m[t, id_] - 1))
                    elif j_ == 2:  # 直行
                        model.m_cons.add(model.y[t, id_] <= B * model.m[t, id_])
                        model.m_cons.add(model.y[t, id_] >= B * (model.m[t, id_] - 1))
                    else:  # 左转
                        model.m_cons.add(25 - model.x[t, id_] <= B * model.m[t, id_])
                        model.m_cons.add(25 - model.x[t, id_] >= B * (model.m[t, id_] - 1))
                else:  # 4车道
                    # n的约束
                    model.n_cons.add(model.x[t, id_] <= B * model.n[t, id_])
                    model.n_cons.add(model.x[t, id_] >= B * (model.n[t, id_] - 1))
                    if j_ == 1:  # 右转
                        model.m_cons.add(model.y[t, id_] <= B * model.m[t, id_])
                        model.m_cons.add(model.y[t, id_] >= B * (model.m[t, id_] - 1))
                    elif j_ == 2:  # 直行
                        model.m_cons.add(25 - model.x[t, id_] <= B * model.m[t, id_])
                        model.m_cons.add(25 - model.x[t, id_] >= B * (model.m[t, id_] - 1))
                    else:  # 左转
                        model.m_cons.add(25 - model.y[t, id_] <= B * model.m[t, id_])
                        model.m_cons.add(25 - model.y[t, id_] >= B * (model.m[t, id_] - 1))

        # 轨迹约束
        for c in cars:
            id_ = c.id
            for t in Times[:-1]:
                if (c.i, c.j) in [(1, 1), (2, 1), (3, 3), (4, 3)]:  # 左转转弯角度变化
                    model.angle_l_cons.add(
                        model.angle_l[t + 1, id_] == (model.angle_l[t, id_] + delta * model.v[t + 1, id_] / r_left) *
                        model.z[t, id_])
                if (c.i, c.j) in [(1, 3), (2, 3), (3, 1), (4, 1)]:  # 右转转弯角度变化
                    model.angle_r_cons.add(
                        model.angle_r[t + 1, id_] == (model.angle_r[t, id_] + delta * model.v[t + 1, id_] / r_right) *
                        model.z[t, id_])
                if c.i == 1:  # 1车道
                    if c.j == 2:  # 直行
                        # 轨迹约束
                        model.x_cons.add(model.x[t + 1, id_] == model.x[t, id_])
                        model.y_cons.add(model.y[t + 1, id_] == model.y[t, id_] + (
                                model.v[t, id_] * delta + 0.5 * model.a[t, id_] * delta ** 2))
                    else:
                        model.x_cons.add(model.x1[t + 1, id_] == model.x[t, id_])
                        model.y_cons.add(model.y1[t + 1, id_] == model.y[t, id_] + (
                                model.v[t, id_] * delta + 0.5 * model.a[t, id_] * delta ** 2))
                        if c.j == 1:  # 左转
                            # 第二段和三段
                            model.x_cons.add(model.x2[t + 1, id_] == r_left * np.cos(value(model.angle_l[t + 1, id_])))
                            model.x_cons.add(model.x3[t + 1, id_] == model.x[t, id_] - (
                                    model.v[t, id_] * delta + 0.5 * model.a[t, id_] * delta ** 2))
                            model.y_cons.add(model.y2[t + 1, id_] == r_left * np.sin(value(model.angle_l[t + 1, id_])))
                            model.y_cons.add(model.y3[t + 1, id_] == model.y[t, id_])
                        else:  # 右转
                            # 轨迹约束
                            model.x_cons.add(
                                model.x2[t + 1, id_] == width - r_right * np.cos(value(model.angle_r[t + 1, id_])))
                            model.x_cons.add(model.x3[t + 1, id_] == model.x[t, id_] + (
                                    model.v[t, id_] * delta + 0.5 * model.a[t, id_] * delta ** 2))
                            model.y_cons.add(model.y2[t + 1, id_] == r_right * np.sin(value(model.angle_r[t + 1, id_])))
                            model.y_cons.add(model.y3[t + 1, id_] == model.y[t, id_])
                elif c.i == 2:  # 2车道
                    if c.j == 2:  # 直行
                        model.y_cons.add(model.y[t + 1, id_] == model.y[t, id_])
                        model.x_cons.add(model.x[t + 1, id_] == model.x[t, id_] - (
                                model.v[t, id_] * delta + 0.5 * model.a[t, id_] * delta ** 2))
                    else:
                        model.x_cons.add(model.x1[t + 1, id_] == model.x[t, id_] - (
                                model.v[t, id_] * delta + 0.5 * model.a[t, id_] * delta ** 2))
                        model.y_cons.add(model.y1[t + 1, id_] == model.y[t, id_])
                        if c.j == 1:  # 左转
                            # 轨迹约束
                            model.x_cons.add(
                                model.x2[t + 1, id_] == width - r_left * np.sin(value(model.angle_l[t + 1, id_])))
                            model.x_cons.add(model.x3[t + 1, id_] == model.x[t, id_])
                            model.y_cons.add(model.y2[t + 1, id_] == r_left * np.cos(value(model.angle_l[t + 1, id_])))
                            model.y_cons.add(model.y3[t + 1, id_] == model.y[t, id_] - (
                                    model.v[t, id_] * delta + 0.5 * model.a[t, id_] * delta ** 2))
                        else:  # 右转
                            # 轨迹约束
                            model.x_cons.add(
                                model.x2[t + 1, id_] == width - r_right * np.cos(value(model.angle_r[t + 1, id_])))
                            model.x_cons.add(model.x3[t + 1, id_] == model.x[t, id_])
                            model.y_cons.add(model.y2[t + 1, id_] == r_right * np.sin(value(model.angle_r[t + 1, id_])))
                            model.y_cons.add(model.y3[t + 1, id_] == model.y[t, id_] - (
                                    model.v[t, id_] * delta + 0.5 * model.a[t, id_] * delta ** 2))
                elif c.i == 3:  # 3车道
                    if c.j == 2:  # 直行
                        # 轨迹约束
                        model.x_cons.add(model.x[t + 1, id_] == model.x[t, id_])
                        model.y_cons.add(model.y[t + 1, id_] == model.y[t, id_] - (
                                model.v[t, id_] * delta + 0.5 * model.a[t, id_] * delta ** 2))
                    else:
                        model.x_cons.add(model.x1[t + 1, id_] == model.x[t, id_])
                        model.y_cons.add(model.y1[t + 1, id_] == model.y[t, id_] - (
                                model.v[t, id_] * delta + 0.5 * model.a[t, id_] * delta ** 2))
                        if c.j == 3:  # 左转
                            # 轨迹约束
                            model.x_cons.add(
                                model.x2[t + 1, id_] == width - r_left * np.cos(value(model.angle_l[t + 1, id_])))
                            model.x_cons.add(model.x3[t + 1, id_] == model.x[t, id_] + (
                                    model.v[t, id_] * delta + 0.5 * model.a[t, id_] * delta ** 2))
                            model.y_cons.add(
                                model.y2[t + 1, id_] == width - r_left * np.sin(value(model.angle_l[t + 1, id_])))
                            model.y_cons.add(model.y3[t + 1, id_] == model.y[t, id_])
                        else:  # 右转
                            # 轨迹约束
                            model.x_cons.add(
                                model.x2[t + 1, id_] == r_right * np.cos(value(model.angle_r[t + 1, id_])))
                            model.x_cons.add(model.x3[t + 1, id_] == model.x[t, id_] - (
                                    model.v[t, id_] * delta + 0.5 * model.a[t, id_] * delta ** 2))
                            model.y_cons.add(
                                model.y2[t + 1, id_] == width - r_right * np.sin(value(model.angle_r[t + 1, id_])))
                            model.y_cons.add(model.y3[t + 1, id_] == model.y[t, id_])
                else:  # 4车道
                    if c.j == 2:  # 直行
                        # 轨迹约束
                        model.y_cons.add(model.y[t + 1, id_] == model.y[t, id_])
                        model.x_cons.add(model.x[t + 1, id_] == model.x[t, id_] + (
                                model.v[t, id_] * delta + 0.5 * model.a[t, id_] * delta ** 2))
                    else:
                        model.x_cons.add(model.x1[t + 1, id_] == model.x[t, id_] + (
                                model.v[t, id_] * delta + 0.5 * model.a[t, id_] * delta ** 2))
                        model.y_cons.add(model.y1[t + 1, id_] == model.y[t, id_])
                        if c.j == 3:  # 左转
                            # 轨迹约束
                            model.x_cons.add(model.x2[t + 1, id_] == r_left * np.sin(value(model.angle_l[t + 1, id_])))
                            model.x_cons.add(model.x3[t + 1, id_] == model.x[t, id_])
                            model.y_cons.add(
                                model.y2[t + 1, id_] == width - r_left * np.cos(value(model.angle_l[t + 1, id_])))
                            model.y_cons.add(model.y3[t + 1, id_] == model.y[t, id_] + (
                                    model.v[t, id_] * delta + 0.5 * model.a[t, id_] * delta ** 2))
                        else:  # 右转
                            # 轨迹约束
                            model.x_cons.add(model.x2[t + 1, id_] == r_right * np.sin(value(model.angle_r[t + 1, id_])))
                            model.x_cons.add(model.x3[t + 1, id_] == model.x[t, id_] - (
                                    model.v[t, id_] * delta + 0.5 * model.a[t, id_] * delta ** 2))
                            model.y_cons.add(model.y2[t + 1, id_] == r_right * np.cos(value(model.angle_r[t + 1, id_])))
                            model.y_cons.add(model.y3[t + 1, id_] == model.y[t, id_])

                if c.j != 2:  # 转弯轨迹约束
                    # 轨迹总约束
                    model.x_cons.add(
                        model.x[t + 1, id_] == model.x1[t + 1, id_] * model.m[t, id_] - model.x1[t + 1, id_] * model.z[t, id_] +
                        model.x2[t + 1, id_] * model.z[t, id_] +
                        model.x3[t + 1, id_] * model.n[t, id_] - model.x3[t + 1, id_] * model.z[t, id_])
                    model.y_cons.add(
                        model.y[t + 1, id_] == model.y1[t + 1, id_] * model.m[t, id_] - model.y1[t + 1, id_] * model.z[t, id_] +
                        model.y2[t + 1, id_] * model.z[t, id_] +
                        model.y3[t + 1, id_] * model.n[t, id_] - model.y3[t + 1, id_] * model.z[t, id_])

        # 安全距离约束
        for key, lane_cars in lane_dict.items():
            if lane_cars:
                for t in Times:
                    for index in range(len(lane_cars) - 1):
                        f = lane_cars[index].id
                        s = lane_cars[index + 1].id
                        if lane_cars[index].i == 1:
                            model.dis_cons.add(model.y[t, f] - model.y[t, s] >= L + 2 * (model.v[t, s] - model.v[t, f]))
                        elif lane_cars[index].i == 2:
                            model.dis_cons.add(model.x[t, s] - model.x[t, f] >= L + 2 * (model.v[t, s] - model.v[t, f]))
                        elif lane_cars[index].i == 3:
                            model.dis_cons.add(model.y[t, s] - model.y[t, f] >= L + 2 * (model.v[t, s] - model.v[t, f]))
                        else:
                            model.dis_cons.add(model.x[t, f] - model.x[t, s] >= L + 2 * (model.v[t, s] - model.v[t, f]))

        # 次序约束
        order_list = [car for car in cars if (car.i, car.j) not in [(1, 3), (2, 3), (3, 1), (4, 1)]]
        for c in range(len(order_list) - 1):
            for t in Times[: -1]:
                model.order_cons.add(1 - model.m[t, order_list[c].id] >= model.n[t, order_list[c + 1].id])

        # 定义目标函数
        last_car = order_list[-1]
        model.obj = Objective(expr=sum(model.m[t, last_car.id] for t in Times), sense=minimize)

        # 求解模型
        start_time = time.time()
        solver = SolverFactory('scip')
        results = solver.solve(model)
        end_time = time.time()
        total_time = end_time - start_time
        print("程序运行时间为：", total_time, "秒")

        print(results.solver.termination_condition)  # 终止条件 一般包括三种 optimal, feasible, infeasible
        print(results.solver.termination_message)  # 求解得到的信息 一般为一行字符串信息
        print(results.solver.status)  # 表示求解的状态 包括 ok, warning, error, aborted, or unknown

        # 输出
        MySolver.print_traj(model, cars)

    @staticmethod
    def print_traj(model: ConcreteModel, cars: List[Car]):
        # 输出结果
        time_ = list()
        id_ = list()
        i_ = list()
        j_ = list()
        x_ = list()
        y_ = list()
        v_ = list()
        a_ = list()
        n_ = list()
        m_ = list()
        print("Total time: ", value(model.obj))
        for c in cars:
            i = c.id
            for t in Times:
                time_.append(t)
                id_.append(i)
                i_.append(c.i)
                j_.append(c.j)
                x_.append(value(model.x[t, i]))
                y_.append(value(model.y[t, i]))
                v_.append(value(model.v[t, i]))
                a_.append(value(model.a[t, i]))
                n_.append(value(model.n[t, i]))
                m_.append(value(model.m[t, i]))
            # print("Car %d: " % i, [value(model.x[t, i]) for t in Times])
            # print("V %d: " % i, [value(model.v[t, i]) for t in Times])
            # print("a %d: " % i, [value(model.x[t, i]) for t in Times])
        out_dict = {'time': time_, 'id': id_, 'i': i_, 'j': j_, 'x': x_, 'y': y_, 'v': v_, 'a': a_, 'n': n_, 'm': m_}
        df = pd.DataFrame(out_dict)
        df.to_csv('traj_out.csv', index=False)
