INTER_WIDTH: int = 25
MAX_V1 = 16.67
MAX_V2 = 12
MAX_AC = 4
MAX_DC = 6
MAX_DE_DIS = (MAX_V1 * MAX_V1 - MAX_V2 * MAX_V2) / (2 * MAX_DC)


def _get_time_1(ac_dis, v, p):
    # 加速到最大速度 然后匀速，最后减速到12
    t1 = (MAX_V1 - v) / MAX_AC  # 计算加速阶段所用时间
    d1 = ac_dis  # 加速阶段距离
    # 第三阶段从最大速度V_MAX1 减速到V_MAX2
    t3 = (MAX_V1 - MAX_V2) / MAX_DC
    d3 = MAX_DE_DIS
    # 第二阶段是匀速阶段
    t2 = (p - d1 - d3) / MAX_V1
    return t1 + t2 + t3


def _get_time_2(v, p):
    # 先匀速，再减速到12
    t2 = (v - MAX_V2) / MAX_DC
    d2 = (v * v - MAX_V2 * MAX_V2) / (2 * MAX_DC)
    t1 = (p - d2) / v
    return t1 + t2


def _get_time_3(v, p):
    # 加速到12，然后匀速
    t1 = (MAX_V2 - v) / MAX_AC
    d1 = (MAX_V2 * MAX_V2 - v * v) / (2 * MAX_AC)
    t2 = (p - d1) / MAX_V2
    return t1 + t2


class Car:
    def __init__(self, car_id: int, lane_id: int, v: float = 0, x: float = 0, y: float = 0):
        self.id = car_id  # 编号
        self.lane = lane_id  # 车道号 lane
        self.v = v  # 速度
        self.x = x  # 位置 x
        self.y = y  # 位置 y

    def __str__(self):
        return f"Car[id={self.id}, lane={self.lane}, v={self.v}, x={self.x}, y={self.y}]"

    def get_z(self) -> int:
        if self.lane in (11, 12, 13):
            return 1 if self.y > 0 else 0
        elif self.lane in (21, 22, 23):
            return 1 if self.x < INTER_WIDTH else 0
        elif self.lane in (31, 32, 33):
            return 1 if self.y < INTER_WIDTH else 0
        else:
            return 1 if self.x > 0 else 0

    def get_m(self) -> int:
        if self.lane == 11:
            return 1 if self.x > 0 else 0
        elif self.lane == 12:
            return 1 if self.y < 25 else 0
        elif self.lane == 13:
            return 1 if self.x < 25 else 0
        elif self.lane == 21:
            return 1 if self.y > 0 else 0
        elif self.lane == 22:
            return 1 if self.x > 0 else 0
        elif self.lane == 23:
            return 1 if self.y < 25 else 0
        elif self.lane == 31:
            return 1 if self.x > 0 else 0
        elif self.lane == 32:
            return 1 if self.y > 0 else 0
        elif self.lane == 33:
            return 1 if self.x < 25 else 0
        elif self.lane == 41:
            return 1 if self.y > 0 else 0
        elif self.lane == 42:
            return 1 if self.x < 25 else 0
        else:
            return 1 if self.y < 25 else 0

    def reach_dis(self) -> float:
        if self.lane in (11, 12, 13):
            return 0 - self.y
        elif self.lane in (21, 22, 23):
            return self.x - 25
        elif self.lane in (31, 32, 33):
            return self.y - 25
        else:
            return 0 - self.x

    def reach_time(self) -> float:
        if self.lane in (11, 12, 13):
            return -self.y / self.v
        elif self.lane in (21, 22, 23):
            return (self.x - INTER_WIDTH) / self.v
        elif self.lane in (31, 32, 33):
            return (self.y - INTER_WIDTH) / self.v
        else:
            return -self.x / self.v

    def min_arrive_time(self) -> float:
        # 计算加速到最大速度所需距离
        max_ac_dis = (MAX_V1 * MAX_V1 - self.v * self.v) / (2 * MAX_AC)
        if self.lane in (11, 12, 13):
            dis_from_intersection = - self.y
        elif self.lane in (21, 22, 23):
            dis_from_intersection = self.x - INTER_WIDTH
        elif self.lane in (31, 32, 33):
            dis_from_intersection = self.y - INTER_WIDTH
        else:
            dis_from_intersection = - self.x
        if dis_from_intersection - MAX_DE_DIS > max_ac_dis:
            # 如果能加速到最大速度，则先加速，再匀速，最后减速
            return _get_time_1(max_ac_dis, self.v, dis_from_intersection)
        else:  # 如果不能加速到最大速度
            if self.v > MAX_V2:
                # 若当前速度大于交叉口速度，则先匀速，再减速
                return _get_time_2(self.v, dis_from_intersection)
            else:
                # 若当前速度小于交叉口速度，则先加速，再匀速
                return _get_time_3(self.v, dis_from_intersection)

    def is_in_con_area(self) -> bool:
        if self.lane in (11, 12, 13):
            return True if -50 <= self.y <= 0 else False
        elif self.lane in (21, 22, 23):
            return True if 75 >= self.x >= 25 else False
        elif self.lane in (31, 32, 33):
            return True if 75 >= self.y >= 25 else False
        else:
            return True if -50 <= self.x <= 0 else False

    def is_right(self) -> bool:
        return True if self.lane in (13, 23, 31, 41) else False
