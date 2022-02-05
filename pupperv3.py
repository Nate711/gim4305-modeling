import moteus
import moteus_pi3hat
import asyncio
import time
import math
import pickle
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--torque', required=False, type=float, default=0.1)
args = parser.parse_args()


async def main():
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={1: [1]},
    )
    controller = moteus.Controller(id=1, transport=transport)
    print(controller)
    data = []
    try:
        timestamp_begin_loop = time.time()
        while True:
            time_since_start = time.time() - timestamp_begin_loop
            pos = 0.0#math.sin(time.time() * 12) * 0
            state = await controller.set_position(position=pos,
                                                  kp_scale=6.0,
                                                  kd_scale=2.0,
                                                  maximum_torque=args.torque,
                                                  query=True
                                                  )
            data.append((time_since_start, state))
            tau = state.values[moteus.Register.TORQUE]
            kt = 8.27 / 153
            print(f"{args.torque} {tau:0.2}\t{tau / kt:0.2}")
            await asyncio.sleep(0.01)
    finally:
        await controller.set_stop()
        with open("log.pickle", "wb+") as f:
            pickle.dump(data, f)


if __name__ == '__main__':
    asyncio.run(main())
