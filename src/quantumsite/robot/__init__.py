class Robot:

    def __init__(self, r_0: tuple[float, float] | np.ndarray):
        self.r_0: np.ndarray = np.array(r_0) # Starting point of the robot
    
    # TODO: Implement necessary functions and variables to allow the robot class to
    # move and to use the reinforcement learning algorithm to improve. Also implement
    # reward system.
