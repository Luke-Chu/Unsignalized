INTER_WIDTH: int = 25


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
