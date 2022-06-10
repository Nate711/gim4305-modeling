from tracemalloc import start
from turtle import st
import moteus
try:
    import moteus_pi3hat
except:
    pass
import asyncio
import time
import math
import pickle
import argparse
import moteus_utils
import movement

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--torque', required=False, type=float, default=0.05)
parser.add_argument('--stop', action='store_true', default=False)
parser.add_argument('--pi', action='store_true', default=False)
args = parser.parse_args()


async def main():
    three_dof_leg = moteus_utils.MultiServo([1, 2, 3], pihat=args.pi)
    knee_controller = movement.TorqueToPD(controller=three_dof_leg.servos[3],
                                          t_begin=0.2,
                                          t_reset=0.3,
                                          termination_time=5.0,
                                          starting_position=-0.2,
                                          reset_position=3.0,
                                          pd_begin=2.5,
                                          pd_target=3.0,
                                          torque=0.1,
                                          maximum_torque=0.1,
                                          reset_torque=0.1)

    try:
        if args.stop:
            await three_dof_leg.stop_all()
            return
        start_time = time.time()
        while True:
            time_elapsed = time.time() - start_time

            # Read states from all controllers
            states = await three_dof_leg.query_all()
            moteus_utils.print_states(states)

            # Lock abduction motor
            await three_dof_leg.servos[2].set_position(position=0.46,
                                                       kp_scale=1.0,
                                                       kd_scale=1.0,
                                                       maximum_torque=0.1,
                                                       query=False)

            # Actuate knee motor
            await knee_controller(t=time_elapsed)

            # Maybe different
            time.sleep(0.005)

    finally:
        await three_dof_leg.stop_all()


if __name__ == '__main__':
    asyncio.run(main())
