from tracemalloc import start
from turtle import st
import moteus
try:
    import moteus_pi3hat
except:
    pass
import asyncio
import time
from datetime import datetime
import math
import pickle
import argparse
import moteus_utils
import movement

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--torque', required=False, type=float, default=0.1)
parser.add_argument('--stop', action='store_true', default=False)
parser.add_argument('--pi', action='store_true', default=False)
parser.add_argument('--log', action='store_true', default=False)
args = parser.parse_args()


async def main():
    data = []
    three_dof_leg = moteus_utils.MultiServo([1, 2, 3], pihat=args.pi)
    knee_controller = movement.TorqueToPD(controller=three_dof_leg.servos[3],
                                          t_begin=0.2,
                                          t_reset=0.3,
                                          termination_time=5.0,
                                          starting_position=-0.2,
                                          reset_position=3.3,
                                          pd_begin=2.5,
                                          pd_target=3.3,
                                          torque=args.torque,
                                          maximum_torque=args.torque,
                                          reset_torque=0.1)

    try:
        if args.stop:
            await three_dof_leg.stop_all()
            return
        start_time = time.time()
        while True:
            states = {1: None, 2: None, 3: None}
            time_elapsed = time.time() - start_time

            # Querying and then setting positions takes about 10-13ms per loop. Setting with query takes about 7-10ms per loop.
            # Read states from all controllers. Takes about 5 ms
            # states = await three_dof_leg.query_all()

            # Lock abduction motor
            states[2] = await three_dof_leg.servos[2].set_position(position=0.46,
                                                                   kp_scale=1.0,
                                                                   kd_scale=1.0,
                                                                   maximum_torque=args.torque,
                                                                   query=True)

            # Actuate knee motor
            states[3] = await knee_controller(t=time_elapsed,
                                              pos=states[3].values[moteus.Register.POSITION] if states[3] else None,
                                              query=True)

            if time_elapsed > 0.2:
                states[1] = await three_dof_leg.servos[1].set_position(position=-1.5,
                                                                       kp_scale=1.0,
                                                                       kd_scale=1.0,
                                                                       maximum_torque=args.torque,
                                                                       query=True)
            else:
                states[1] = await three_dof_leg.servos[1].query()

            # Either save to file or print, probably not best to do both
            if args.log:
                data.append((time_elapsed, states))
            moteus_utils.print_states(states, time_elapsed=time_elapsed)

            # Maybe different
            # Go as fast as possible?
            # await asyncio.sleep(0.002)

    finally:
        await three_dof_leg.stop_all()
        now = datetime.now()
        timestamp = now.strftime("%m_%d_%Y_%H_%M_%S")
        if args.log:
            with open(f"logs/3dof_jump/log_{timestamp}.pickle", "wb+") as f:
                pickle.dump(data, f)

if __name__ == '__main__':
    asyncio.run(main())
