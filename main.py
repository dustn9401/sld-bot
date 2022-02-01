import asyncio
from Controller.BotController import BotController
from Controller.BotController import RunConfiguration
from Constant.Constants import *
from Controller import SC2Window

if __name__ == '__main__':
    config = RunConfiguration(Hard, rune_gain_behaviour=1, rune_reinforce_slot_index=0)
    controller = BotController(SC2Window.SC2Window(), config)
    asyncio.get_event_loop().run_until_complete(controller.update())
