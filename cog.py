import discord
from discord.ext import commands

import requests
import json
import re
import random

import io
import aiohttp

class HoresaseCog(commands.Cog):
    def __init__(self, bot):
        print("initializing...")
        self.bot = bot
        self.bot.remove_command('help')

        self.api = "http://horesase.azurewebsites.net/api"
        self.commands_list = {
            "--id X": "IDがXの画像を表示する",
            "--character X": "キャラクター名がXのランダムな画像を表示する",
            "--word X": "名前がXの画像を表示する",
            "--list X": "キャラクター名がXの画像の名前を全て表示する。変数が無い場合はキャラクター名を全て表示する",
            "--gacha": "全ての画像からランダムな画像を表示する。",
            "--help": "ヘルプ画面を表示する",
            # "--kuso": "ク　ソ　リ　プ",
            # "--random": "ク　ソ　リ　プ(ver2)",
            # "--verbose": "画像取得時、各種データを表示する"
            "--info": "このbotの詳細を表示する"
        }
        self.kuso_flag = False
        self.random_kuso_flag = False
        self.verbose_flag = True

        r = requests.get("http://horesase.azurewebsites.net/api/characters")
        data = json.loads(r.text)
        self.characters = [item['name'] for item in data]
        for i in range(len(self.characters)):
            self.characters[i] = re.sub(r'\([^)]*\)', '', self.characters[i])

        # r = requests.head("http://horesase.azurewebsites.net/api/meigens")
        # print(r.headers)
        # data = json.loads(r.headers)
        # self.total_count = r.headers['X-Pagination']['total_count']
        self.total_count = 2131

    async def request(self, ctx, id=None, word=None, character=None):
        r = None
        if id:
            r = requests.get("http://horesase.azurewebsites.net/api/meigens/" + str(id))
        if character:
            r = requests.get("http://horesase.azurewebsites.net/api/meigens?limit=100&character=" + character)
        if word:
            r = requests.get("http://horesase.azurewebsites.net/api/meigens?limit=100&word=" + word)


        if not r or not r.text or r.text == "null":
            await ctx.send("エラー：指定された入力に該当する画像は存在しません。")
        else:
            response = json.loads(r.text)
            if not response:
                await ctx.send("エラー：指定された入力に該当する画像は存在しません。")
            else:
                if isinstance(response, list):
                    if word and response[0]['title'].startswith(word):
                        response = response[0]
                    else:
                        response = random.choice(response)
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(response['image']) as resp:
                        if resp.status != 200:
                            await ctx.send("エラー：APIが応答しません。HTTP Response Code:"  + str(resp.status))
                        data = io.BytesIO(await resp.read())
                        if not self.verbose_flag:
                            await ctx.send(file=discord.File(data, 'horesase.png'))
                        else:
                            context = "character: " + re.sub(r'\([^)]*\)', '', response["character"]) + "\n" + \
                                    "id: "        + str(response["id"]) + "\n" + \
                                    "name: "      + response["title"] + "\n" + \
                                    "body: "      + response["body"] + "\n"
                            await ctx.send(context,file=discord.File(data, 'horesase.png'))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return 
        if self.random_kuso_flag and random.randint(1,10) == 1:
            # ゴミコードなので書き直したいけどとりあえずは…
            id = random.randint(1,self.total_count)
            r = requests.get("http://horesase.azurewebsites.net/api/meigens/" + str(id))
            response = json.loads(r.text)
            async with aiohttp.ClientSession() as session:
                async with session.get(response['image']) as resp:
                    if resp.status != 200:
                        await message.channel.send("エラー：APIが応答しません。HTTP Response Code:"  + str(resp.status))
                    data = io.BytesIO(await resp.read())
                    if not self.verbose_flag:
                        await message.channel.send(file=discord.File(data, 'horesase.png'))
                    else:
                        context = "character: " + re.sub(r'\([^)]*\)', '', response["character"]) + "\n" + \
                                "id: "        + str(response["id"]) + "\n" + \
                                "name: "      + response["title"] + "\n" + \
                                "body: "      + response["body"] + "\n"
                        await message.channel.send(context,file=discord.File(data, 'horesase.png'))

            
    #コマンド一覧
    @commands.command()
    async def info(self, ctx):
        embed = discord.Embed(title="info", description="地獄のミサワの「女を惚れさす名言集」bot。\n詳細は--help参照")
        # embed.set_footer(text="惚れさせてやるよ。")
        await ctx.send(embed=embed)

    @commands.command(aliases=["h"])
    async def help(self, ctx):
        embed = discord.Embed(title="help")
        for k,v in self.commands_list.items():
            embed.add_field(name=k, value=v)
        embed.set_footer(text="惚れさせてやるよ。")
        await ctx.send(embed=embed)

    @commands.command(aliases=["i"])
    async def id(self, ctx, id=None):
        print(id)
        if not id:
            await ctx.send("エラー：IDを指定してください")
        elif not id.isdigit():
            await ctx.send("エラー：IDは正式な数値ではありません。")
        else:
            id = int(id)
            await self.request(ctx=ctx, id=id)

    @commands.command(aliases=["c", "char"])
    async def character(self, ctx, character=None):
        if not id:
            await ctx.send("エラー：キャラクターを指定してください")
        else:
            await self.request(ctx=ctx, character=character)

    @commands.command(aliases=["w"])
    async def word(self, ctx, word=None):
        if not id:
            await ctx.send("エラー：名前を指定してください")
        else:
            await self.request(ctx=ctx, word=word)

    @commands.command(aliases=["g", "random", "rand"])
    async def gacha(self, ctx):
        await self.request(ctx=ctx, id=random.randint(1,self.total_count))

    @commands.command(aliases=["l", "ls"])
    async def list(self, ctx, character=None):
        if not character:
            message = self.characters
        else:
            r = requests.get("http://horesase.azurewebsites.net/api/meigens?limit=30&character=" + character)
            data = json.loads(r.text)
            message = [d["title"] for d in data]
        await ctx.send(message)
         
    @commands.command(aliases=["v"])
    async def verbose(self, ctx):
        self.verbose_flag = not self.verbose_flag
        message = "verboseモードがオンになりました" if self.verbose_flag else "verboseモードがオフになりました"
        await ctx.send(message)

    @commands.command(aliases=["rk"])
    async def random_kuso(self, ctx):
        self.random_kuso_flag = not self.random_kuso_flag
        message = "ランダムクソリプモードがオンになりました" if self.random_kuso_flag else "ランダムクソリプモードがオフになりました"
        await ctx.send(message)

# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(HoresaseCog(bot)) 
