import asyncio
from Controller.BotController import BotController
from Constant.Constants import *

from Controller import SC2Window

if __name__ == '__main__':
    controller = BotController(SC2Window.SC2Window(), Hard)
    asyncio.get_event_loop().run_until_complete(controller.update())
