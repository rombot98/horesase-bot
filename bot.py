import discord
from discord.ext import commands 
import traceback

import os
import json

INITIAL_EXTENSIONS = [
    'cog'
]

class HoresaseBot(commands.Bot):

    def __init__(self, command_prefix, description):
        super().__init__(command_prefix=command_prefix, description=description, case_insensitive=True)

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        print('-----')
        print(self.user.name)
        # print(self.user.id)
        print('-----')


if __name__ == '__main__':
    bot = HoresaseBot(command_prefix = "--", description = "地獄のミサワ「女を惚れさす名言集」bot")
    access_token= os.environ["ACCESS_TOKEN"]
    # with open("config.json","r") as f:
    #     data = json.load(f)
    #     access_token = data["ACCESS_TOKEN"]
    
    bot.run(access_token)
    