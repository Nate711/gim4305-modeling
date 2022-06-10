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
import pdb

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--torque', required=False, type=float, default=0.05)
parser.add_argument('--stop', action='store_true', default=False)
parser.add_argument('--pi', action='store_true', default=False)
args = parser.parse_args()


async def main():
    three_dof_leg = moteus_utils.MultiServo([1, 2, 3], pihat=args.pi)
    try:
        if args.stop:
            await three_dof_leg.stop_all()
            return

        while True:
            # Read states from all controllers
            states = await three_dof_leg.query_all()
            moteus_utils.print_states(states)

            # Lock abduction motor
            await three_dof_leg.servos[2].set_position(position=0.46,
                                                       kp_scale=1.0,
                                                       kd_scale=1.0,
                                                       maximum_torque=0.1,
                                                       query=False)

            # Position-control knee and hip
            # meas_knee_pos = states[3].values[moteus.Register.POSITION]
            # hip_pos = states[1].values[moteus.Register.POSITION]
            # knee_pos = -1.27 * hip_pos + 1.68
            # await three_dof_leg.servos[1].set_position(position=-1.0,
            #                                            kp_scale=1.0,
            #                                            kd_scale=1.0,
            #                                            maximum_torque=args.torque,
            #                                            query=False)
            # print(hip_pos)
            # await three_dof_leg.servos[3].set_position(position=knee_pos,
            #                                            kp_scale=1.0,
            #                                            kd_scale=1.0,
            #                                            maximum_torque=args.torque,
            #                                            query=False)

            # Maybe different
            time.sleep(0.005)

    finally:
        await three_dof_leg.stop_all()


if __name__ == '__main__':
    asyncio.run(main())
