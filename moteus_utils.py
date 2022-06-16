import moteus
import time
try:
    import moteus_pi3hat
except:
    pass
import pdb


class MultiServo:
    def __init__(self, ids, pihat=False):
        self.transport = moteus_pi3hat.Pi3HatRouter(
            servo_bus_map={1: [1]},  # TODO FIX
        ) if pihat else moteus.get_singleton_transport()

        self.servos = {id: moteus.Controller(
            id=id, transport=self.transport) for id in ids}

    async def stop_all(self, tries=10, delay=0.02):
        try:
            for t in range(tries):
                await self.transport.cycle([x.make_stop() for x in self.servos.values()])
                time.sleep(delay)
        except RuntimeError as re:
            print("TRYING TO STOP AGAIN")
            await self.stop_all(tries=tries, delay=delay)

    async def query_all(self):
        results = await self.transport.cycle([x.make_query() for x in self.servos.values()])
        results = {result.id: result for result in results}
        return results


def print_states(states, position=True, velocity=True, torque=True, fault=True, time_elapsed=None):
    if time_elapsed is not None:
        print(f"{time_elapsed:0.4f}", end=" ")
    for id, state in states.items():
        p = state.values[moteus.Register.POSITION]
        v = state.values[moteus.Register.VELOCITY]
        t = state.values[moteus.Register.TORQUE]
        f = state.values[moteus.Register.FAULT]
        print(
            f"id:{state.id}  P: {p:+0.3f}  V:{v:+0.3f}  T:{t:+0.3f}  F:{f}", end=" - ")
    print()
