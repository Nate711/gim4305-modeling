import moteus


class TorqueToPD:
    def __init__(self,
                 controller,
                 t_begin,
                 t_reset,
                 starting_position,
                 reset_position,
                 pd_begin,
                 pd_target,
                 torque,
                 kp_scale=1.0,
                 kd_scale=1.0,
                 maximum_torque=1.0,
                 termination_time=1.0,
                 reset_torque=0.2):
        self.controller = controller
        self.t_begin = t_begin
        self.t_reset = t_reset
        self.starting_position = starting_position
        self.reset_position = reset_position
        self.pd_begin = pd_begin
        self.pd_target = pd_target
        self.torque = torque
        self.kp_scale = kp_scale
        self.kd_scale = kd_scale
        self.maximum_torque = maximum_torque
        self.reset_torque = reset_torque

        self.past_pd_threshold = False

        self.termination_time = termination_time

    async def __call__(self, t, pos=None):
        if pos is None:
            state = await self.controller.query()
            pos = state.values[moteus.Register.POSITION]

        if t < self.t_begin:
            return await self.controller.set_position(position=self.starting_position,
                                                      kp_scale=self.kp_scale,
                                                      kd_scale=self.kd_scale,
                                                      maximum_torque=self.maximum_torque,
                                                      query=True)
        elif pos < self.pd_begin and not self.past_pd_threshold:
            return await self.controller.set_position(maximum_torque=self.maximum_torque,
                                                      kp_scale=0.0,
                                                      kd_scale=0.0,
                                                      feedforward_torque=self.torque,
                                                      query=True)
        elif t < self.t_reset:
            self.past_pd_threshold = True
            return await self.controller.set_position(position=self.pd_target,
                                                      kp_scale=self.kp_scale,
                                                      kd_scale=self.kd_scale,
                                                      maximum_torque=self.maximum_torque,
                                                      query=True
                                                      )
        elif t < self.termination_time:
            return await self.controller.set_position(position=self.reset_position,
                                                      kp_scale=self.kp_scale,
                                                      kd_scale=self.kd_scale,
                                                      maximum_torque=self.reset_torque,
                                                      query=True
                                                      )
        else:
            return await self.controller.set_stop()

