import numpy as np
import gym

class ChannelSpace(gym.Space):
    """
    {0,1,2}
    0: channel is idle
    1: channel is busy
    2: unknown

    Example usage:
    self.observation_space = spaces.ChannelSpace
    """
    def __init__(self):
        self.n = 3
        gym.Space.__init__(self, (), np.int64)
    def sample(self):
        return gym.spaces.np_random.randint(self.n)
    def contains(self, x):
        if isinstance(x, int):
            as_int = x
        elif isinstance(x, (np.generic, np.ndarray)) and (x.dtype.kind in np.typecodes['AllInteger'] and x.shape == ()):
            as_int = int(x)
        else:
            return False
        return as_int >= 0 and as_int < self.n
    def __repr__(self):
        return "Discrete(%d)" % self.n
    def __eq__(self, other):
        return self.n == other.n