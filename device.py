import time
import math


class Device:
    def __init__(self,
                 signal_strength,
                 frequency,
                 address,):
        self.signal_strength = signal_strength
        self.frequency = frequency
        self.address = address
        self.distance = []
        self.time_registered = time.time()
        self.time_last_seen  = self.time_registered

        self.distance.append(self.calc_distance())

    def update_strength(self, signal_strength):
        self.update_time_last_seen()
        if self.time_last_seen - self.time_registered < 2:
            return
        else:
            self.signal_strength = signal_strength
            self.distance.append(self.calc_distance())

    def calc_distance(self):
        dist = 10 ** ((27.55 - (20 * math.log(self.frequency, 10)) + math.fabs(self.signal_strength)) / 20)
        return dist

    def get_last_dist(self):
        return self.distance[-1]

    def update_time_last_seen(self):
        self.time_last_seen = time.time()

    def __lt__(self, other):
        # p1 < p2 calls p1.__lt__(p2)
        return self.distance[-1] < other.distance[-1]

    def __eq__(self, other):
        # p1 == p2 calls p1.__eq__(p2)
        return self.distance[-1] == other.distance[-1]