import asyncio
from Controller.BotController import BotController
from Controller.RunConfiguration import RunConfiguration
from Constant.Constants import *
from Controller import SC2Window

if __name__ == '__main__':
    config = RunConfiguration(Hell, rune_gain_behaviour=1, rune_reinforce_slot_index=0)
    controller = BotController(SC2Window.SC2Window(), config)
    # controller.test_func()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(controller.update())
