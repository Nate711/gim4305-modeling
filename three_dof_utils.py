import math

ACTUATOR_1_ZERO = -1.438
ACTUATOR_2_ZERO = 0.466
ACTUATOR_3_ZERO = 3.573

GEAR_RATIO = 0.1


def actuator_1_qB_deg(pos):
    return GEAR_RATIO * (pos - ACTUATOR_1_ZERO) * 360.0


def actuator_1_qB_dot_rad_sec(vel):
    return GEAR_RATIO * vel * 2 * math.pi


def actuator_3_qC_deg(pos):
    return - GEAR_RATIO * (pos - ACTUATOR_3_ZERO) * 360.0

def actuator_3_qC_dot_rad_sec(vel):
    return - GEAR_RATIO * vel * 2 * math.pi

