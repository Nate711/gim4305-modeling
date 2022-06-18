from tracemalloc import start
from turtle import st
import moteus
import copy
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
    leader_follower = moteus_utils.MultiServo([1, 2], pihat=args.pi)

    try:
        if args.stop:
            await leader_follower.stop_all()
            return
        start_time = time.time()

        last_states = None
        smoothed_leader_torque = 0.0
        while True:
            states = {1: None, 2: None}
            time_elapsed = time.time() - start_time

            leader_pos = last_states[1].values[moteus.Register.POSITION] if last_states else 0.0
            leader_vel = last_states[1].values[moteus.Register.VELOCITY] if last_states else 0.0

            follower_pos = last_states[2].values[moteus.Register.POSITION] if last_states else 0.0
            follower_vel = last_states[2].values[moteus.Register.VELOCITY] if last_states else 0.0

            # calling individually also 3.5-4.5 ms

            states[2] = await leader_follower.servos[2].set_position(position=leader_pos,
                                                                     velocity=leader_vel*0.2,
                                                                     kp_scale=1.0,
                                                                     kd_scale=1.0,
                                                                     maximum_torque=args.torque,
                                                                     query=True)
            expected_follower_torque = 0.8 * \
                (leader_pos - follower_pos) + 0.005 * \
                (leader_vel * 0.2 - follower_vel)

            # states[1] = await leader_follower.servos[1].set_position(position=follower_pos,
            #                                                          velocity=follower_vel*0.2,
            #                                                          kp_scale=0,#1.0,
            #                                                          kd_scale=0,#1.0,
            #                                                          maximum_torque=args.torque,
            #                                                          query=True)
            smoothed_leader_torque = 0.9 * smoothed_leader_torque + 0.1 * -expected_follower_torque
            print(f"{expected_follower_torque:0.3f} {smoothed_leader_torque:0.3f}")
            states[1] = await leader_follower.servos[1].set_position(position=0,
                                                                     velocity=0,
                                                                     kp_scale=0,
                                                                     kd_scale=0,
                                                                     feedforward_torque=smoothed_leader_torque,
                                                                     maximum_torque=args.torque,
                                                                     query=True)

            # leader_task = leader_follower.servos[1].set_position(position=follower_pos,
            #                                                      velocity=follower_vel*0.2,
            #                                                      kp_scale=0,
            #                                                      kd_scale=0,
            #                                                      maximum_torque=args.torque,
            #                                                      query=True)
            # follower_task = leader_follower.servos[2].set_position(position=leader_pos,
            #                                                        velocity=leader_vel*0.2,
            #                                                        kp_scale=0,
            #                                                        kd_scale=0,
            #                                                        maximum_torque=args.torque,
            #                                                        query=True)
            # (states[1], states[2]) = await asyncio.gather(leader_task, follower_task) # 3.5 to 4.5ms

            last_states = copy.deepcopy(states)

            # Either save to file or print, probably not best to do both
            if args.log:
                data.append((time_elapsed, states))
            # moteus_utils.print_states(states, time_elapsed=time_elapsed)

            # Maybe different
            # Go as fast as possible?
            # await asyncio.sleep(0.002)

    finally:
        await leader_follower.stop_all()
        now = datetime.now()
        timestamp = now.strftime("%m_%d_%Y_%H_%M_%S")
        if args.log:
            with open(f"logs/leader_follower/log_{timestamp}.pickle", "wb+") as f:
                pickle.dump(data, f)

if __name__ == '__main__':
    asyncio.run(main())
