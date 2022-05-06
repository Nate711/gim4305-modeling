import moteus
import moteus_pi3hat
import asyncio
import time
import math
import pickle
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--torque', required=False, type=float, default=0.1)
parser.add_argument('--jump_period', required=True, type=float, default=1.0)
parser.add_argument('--stop', action='store_true', default=False)

args = parser.parse_args()


def calculate_progress(time_since_start, period):
    return (time_since_start % period) / period


def jump_land(progress,
              jump_duration=0.12,
              damp_duration=0.6,
              reset_duration=0.2,
              reset_pos=0.5,
              land_pos=0.8,
              jump_pos=1.4):
    if progress < 0 or progress > 1:
        raise RuntimeError(f"Progress should be in [0,1]. Is {progress}")
    if progress < jump_duration:
        pos = jump_pos
        kp_scale = 6
        kd_scale = 2
    elif progress < jump_duration + damp_duration:
        pos = land_pos
        kp_scale = 0.4
        kd_scale = 4
    else:
        pos = reset_pos
        kp_scale = 3
        kd_scale = 2

    return (pos, kp_scale, kd_scale)


async def main():
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={1: [1]},
    )
    controller = moteus.Controller(id=1, transport=transport)
    if args.stop:
      await controller.set_stop()
      print("Stopped")
      return

    print("Controller: ", controller)
    data = {}
    data["time_since_start"] = []
    data["command"] = []
    data["moteus_state"] = []

    sum_square_torque = 0
    count = 0

    try:
        timestamp_begin_loop = time.time()
        while True:
            time_since_start = time.time() - timestamp_begin_loop
            progress = calculate_progress(time_since_start, args.jump_period)
            (pos, kp_scale, kd_scale) = jump_land(progress)
            state = await controller.set_position(position=pos,
                                                  kp_scale=kp_scale,
                                                  kd_scale=kd_scale,
                                                  maximum_torque=args.torque,
                                                  query=True
                                                  )
            data["time_since_start"].append(time_since_start)
            data["command"].append((pos, kp_scale, kd_scale, args.torque))
            data["moteus_state"].append(state)
            tau = state.values[moteus.Register.TORQUE]
            count+=1
            sum_square_torque += tau**2
            rms_torque = (sum_square_torque / count)**0.5
            read_pos = state.values[moteus.Register.POSITION]
            kt = 8.27 / 153
            print(
                f"Max torque: {args.torque}\t Comm. torque: {tau:0.3f}\t RMS torque: {rms_torque:0.2f}\t Current: {tau / kt:0.2f}\tMotor pos: {read_pos:0.2f}\t Comm pos: {pos:0.2f}\t Time: {time_since_start:0.2f}")
            await asyncio.sleep(0.005)
    finally:
        await controller.set_stop()
        with open("log.pickle", "wb+") as f:
            pickle.dump(data, f)


if __name__ == '__main__':
    asyncio.run(main())
