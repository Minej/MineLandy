from asyncio import events
from http import client
import json
import tkinter
import queue
import requests
from config import TOKEN
import nextcord
import discord
import wavelink
from wavelink.ext import spotify
from discord.ext import commands
from mcstatus import MinecraftServer
import datetime
from discord.ui import Button, View

bot = commands.Bot(command_prefix = '!')


#terminal 
@bot.event
async def on_ready():
    print('Бот подключился')
    bot.loop.create_task(node_connect())
    await bot.change_presence(activity=discord.Game(name="mc.minelandy.ru"))

@bot.command()
@commands.has_any_role(874265030412107827, 940623991599661137, 874234538270797884)
async def clear(ctx, amount : int):
    await ctx.channel.purge(limit = amount)

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, введи число')
        
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.name}, стопэ, у тебя прав нет')
           
@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f'Node {node.identifier} is ready!')
    
async def node_connect():
    await bot.wait_until_ready()
    await wavelink.NodePool.create_node(bot = bot, host = 'lavalinkinc.ml', port = 443, password = 'incognito', https = True, spotify_client = spotify.SpotifyClient(client_id = "442383a0f9984adf9453711b0483af8d", client_secret = "de4446f90dff4d6090ad6914d08ea283"))

@bot.event
async def on_wavelink_track_end(player: wavelink.Player, track: wavelink.Track, reason):
    ctx = player.ctx
    vc = ctx.voice_client

    if vc.loop:
        return await vc.play(track)

    if vc.queue.is_empty:
        return await vc.disconnect()

    next_song = vc.queue.get()
    await vc.play(next_song)
    em = nextcord.Embed(title = f"Сейчас играет {vc.track.title}", description = f"Артист: {vc.track.author}", color = 0xe25a00)
    em.add_field(name = "Продолжительность", value = f"{str(datetime.timedelta(seconds = vc.track.length))}")
    em.add_field(name = "Информация", value = f"URL: {str(vc.track.uri)}")
    em.set_image(url=next_song.thumb)
    em.set_author(name="MineLandy", icon_url="https://i.ibb.co/CWLjzyv/308505.png")
    em.set_thumbnail(url = 'https://i.ibb.co/fvz5KbM/61b541009ce0a981919641.png')
    em.timestamp = datetime.datetime.now()
    em.set_footer(text=f'\u200b {ctx.author.display_name}', icon_url=ctx.author.display_avatar)
    await ctx.send(embed=em)
    if next_song.thumb:
        em.set_image(url=next_song.thumb)
    else:
        em.add_field(name="Issue", value=f"Thumbnail not found for {next_song.title}", inline=False)
        await ctx.send(embed=em)

@bot.command()
async def play(ctx: commands.Context, *, search: wavelink.YouTubeTrack):
        embed1 = discord.Embed(description=f"Хммм? Сначала зайди в голосовой канал", color = 0xe25a00)
        if not ctx.author.voice:
            return await ctx.send(embed=embed1)
        elif not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("Хммм? Сначала зайди в голосовой канал", color = 0xe25a00)
        elif ctx.author.voice != ctx.me.voice: 
            return await ctx.send("Ты в другом канале. Зайди в другой голосовой канал")
        else:
            vc: wavelink.Player = ctx.voice_client

        if vc.queue.is_empty and not vc.is_playing():
            await vc.play(search)
            em = nextcord.Embed(title = f"Сейчас играет {vc.track.title}", description = f"Артист: {vc.track.author}", color = 0xe25a00)
            em.add_field(name = "Продолжительность", value = f"{str(datetime.timedelta(seconds = vc.track.length))}")
            em.add_field(name = "Информация", value = f"URL: {str(vc.track.uri)}")
            em.set_image(url=search.thumb)
            em.set_author(name="MineLandy", icon_url="https://i.ibb.co/CWLjzyv/308505.png")
            em.set_thumbnail(url = 'https://i.ibb.co/fvz5KbM/61b541009ce0a981919641.png')
            em.timestamp = datetime.datetime.now()
            em.set_footer(text=f'\u200b {ctx.author.display_name}', icon_url=ctx.author.display_avatar)
            await ctx.send(embed=em)
        else:
            await vc.queue.put_wait(search)
            em = nextcord.Embed(title = f"Сейчас играет {vc.track.title}", description = f"Артист: {vc.track.author}", color = 0xe25a00)
            em.add_field(name = "Продолжительность", value = f"{str(datetime.timedelta(seconds = vc.track.length))}")
            em.add_field(name = "Информация", value = f"URL: {str(vc.track.uri)}")
            em.set_image(url=search.thumb)
            em.set_author(name="MineLandy", icon_url="https://i.ibb.co/CWLjzyv/308505.png")
            em.set_thumbnail(url = 'https://i.ibb.co/fvz5KbM/61b541009ce0a981919641.png')
            em.timestamp = datetime.datetime.now()
            em.set_footer(text=f'\u200b {ctx.author.display_name}', icon_url=ctx.author.display_avatar)
            await ctx.send(embed=em)
            
        vc.ctx = ctx
        setattr(vc, "loop", False)

@bot.command()
async def pause(ctx: commands.Context):
    if not ctx.voice_client:
        return await ctx.send("Я не в голосовом канале", color = 0xe25a00)
    elif not getattr(ctx.author.voice, "channel", None):
        return await ctx.send("Хммм? Сначала зайди в голосовой канал", color = 0xe25a00)
    # elif not ctx.author.voice == ctx.me.voice:
    #     return await ctx.send("Ты в другом канале. Зайди в другой голосовой канал")
    else:
        vc: wavelink.Player = ctx.voice_client
    
    await vc.pause()
    em = nextcord.Embed(description=f"Воспроизведение остановлено", color = 0xe25a00) 
    await ctx.send(embed = em)

@bot.command()
async def resume(ctx: commands.Context):
    if not ctx.voice_client:
        em = nextcord.Embed(description=f"Я не в голосовом канале", color = 0xe25a00)
        await ctx.send(embed = em)
    elif not getattr(ctx.author.voice, "channel", None):
        em = nextcord.Embed(description=f"Хммм? Сначала зайди в голосовой канал", color = 0xe25a00)
        await ctx.send(embed = em)
    # elif not ctx.author.voice == ctx.me.voice:
    #     return await ctx.send("Ты в другом канале. Зайди в другой голосовой канал")
    else:
        vc: wavelink.Player = ctx.voice_client
    
    await vc.resume()
    em = nextcord.Embed(description=f"Воспроизведение продолжилось", color = 0xe25a00)
    await ctx.send(embed = em)

@bot.command()
async def stop(ctx: commands.Context):
    if not ctx.voice_client:
        em = nextcord.Embed(description=f"Я не в голосовом канале", color = 0xe25a00)
        await ctx.send(embed = em)
    elif not getattr(ctx.author.voice, "channel", None):
        em = nextcord.Embed(description=f"Хммм? Сначала зайди в голосовой канал", color = 0xe25a00)
        await ctx.send(embed = em)
    # elif not ctx.author.voice == ctx.me.voice:
    #     return await ctx.send("Ты в другом канале. Зайди в другой голосовой канал")
    else:
        vc: wavelink.Player = ctx.voice_client
    
    await vc.disconnect()
    em = nextcord.Embed(description=f"Воспроизведение остановилось", color = 0xe25a00)
    await ctx.send(embed = em)

@bot.command()
async def skip(ctx: commands.Context):
    if not ctx.voice_client:
        em = nextcord.Embed(description=f"Я не в голосовом канале", color = 0xe25a00)
        await ctx.send(embed = em)
    elif not getattr(ctx.author.voice, "channel", None):
        em = nextcord.Embed(description=f"Хммм? Сначала зайди в голосовой канал", color = 0xe25a00)
        await ctx.send(embed = em)
    # elif not ctx.author.voice == ctx.me.voice:
    #     return await ctx.send("Ты в другом канале. Зайди в другой голосовой канал")
    else:
        vc: wavelink.Player = ctx.voice_client
    
    await vc.stop()
    em = nextcord.Embed(description=f"Переход к следующей композиции", color = 0xe25a00)
    await ctx.send(embed = em)
    
@bot.command()
async def loop(ctx: commands.Context):
    if not ctx.voice_client:
        em = nextcord.Embed(description=f"Я не в голосовом канале", color = 0xe25a00)
        await ctx.send(embed = em)
    elif not getattr(ctx.author.voice, "channel", None):
        em = nextcord.Embed(description=f"Хммм? Сначала зайди в голосовой канал", color = 0xe25a00)
        await ctx.send(embed = em)
    # elif not ctx.author.voice == ctx.me.voice:
    #     return await ctx.send("Ты в другом канале. Зайди в другой голосовой канал")
    else:
        vc: wavelink.Player = ctx.voice_client
    
    try:
        vc.loop ^= True
    except Exception:
        setattr(vc, "loop", False)
    
    if vc.loop:
        em = nextcord.Embed(description=f"Повторение включено", color = 0xe25a00)
        await ctx.send(embed = em)
    else:
        em = nextcord.Embed(description=f"Повторение выключено", color = 0xe25a00)
        await ctx.send(embed = em)

@bot.command()
async def queue(ctx: commands.Context):
    if not ctx.voice_client:
        em = nextcord.Embed(description=f"Я не в голосовом канале", color = 0xe25a00)
        await ctx.send(embed = em)
    elif not getattr(ctx.author.voice, "channel", None):
        em = nextcord.Embed(description=f"Хммм? Сначала зайди в голосовой канал", color = 0xe25a00)
        await ctx.send(embed = em)
    # elif not ctx.author.voice == ctx.me.voice:
    #     return await ctx.send("Ты в другом канале. Зайди в другой голосовой канал")
    else:
        vc: wavelink.Player = ctx.voice_client

    if vc.queue.is_empty:
        em = nextcord.Embed(description=f"Очередь пустая")
        await ctx.send(embed = em)
    
    
    em = nextcord.Embed(title = f"Очередь \n {vc.track.title}", description = f"Артист: {vc.track.author}\n Продолжительность: {str(datetime.timedelta(seconds = vc.track.length))}", color = 0xe25a00)
    em.set_author(name="MineLandy", icon_url="https://i.ibb.co/CWLjzyv/308505.png")
    em.set_thumbnail(url = 'https://i.ibb.co/fvz5KbM/61b541009ce0a981919641.png')
    em.timestamp = datetime.datetime.now()
    em.set_footer(text=f'\u200b {ctx.author.display_name}', icon_url=ctx.author.display_avatar)
    queue = vc.queue.copy()
    song_count = 0
    for song in queue:
        song_count += 1
        em.add_field(name = f"\nВ очереди {song_count}\n", value = f"{song}", inline=False)
        
    return await ctx.send(embed=em)

@bot.command()
async def volume(ctx: commands.Context, volume: int):
    if not ctx.voice_client:
        em = nextcord.Embed(description=f"Я не в голосовом канале", color = 0xe25a00)
        await ctx.send(embed = em)
    elif not getattr(ctx.author.voice, "channel", None):
        em = nextcord.Embed(description=f"Хммм? Сначала зайди в голосовой канал", color = 0xe25a00)
        await ctx.send(embed = em)
    # elif not ctx.author.voice == ctx.me.voice:
    #     return await ctx.send("Ты в другом канале. Зайди в другой голосовой канал")
    else:
        vc: wavelink.Player = ctx.voice_client
    
    if volume > 100:
        em = nextcord.Embed(description=f"Куда больше? Оглохнешь", color = 0xe25a00)
        await ctx.send(embed = em)
    elif volume < 0:
        em = nextcord.Embed(description=f"Куда тише?", color = 0xe25a00)
        await ctx.send(embed = em)
    em1 = nextcord.Embed(description=f"Громкость изменено на {volume}%", color = 0xe25a00)
    await ctx.send(embed = em1)
    return await vc.set_volume(volume)

@bot.command()
async def playlist(ctx : commands.Context):
    if not ctx.voice_client:
        em = nextcord.Embed(description=f"Я не в голосовом канале", color = 0xe25a00)
        await ctx.send(embed = em)
    elif not getattr(ctx.author.voice, "channel", None):
        em = nextcord.Embed(description=f"Хммм? Сначала зайди в голосовой канал", color = 0xe25a00)
        await ctx.send(embed = em)
    elif ctx.author.voice == ctx.me.voice:
        return await ctx.send("Ты в другом канале. Зайди в другой голосовой канал")
    else:
        vc: wavelink.Player = ctx.voice_client
    
    if not vc.is_playing():
        em = nextcord.Embed(description=f"Ничего не играет", color = 0xe25a00)
        await ctx.send(emned = em)
    
    em = nextcord.Embed(title = f"Сейчас играет {vc.track.title}", description = f"Артист: {vc.track.author}", color = 0xe25a00)
    em.add_field(name = "Продолжительность", value = f"{str(datetime.timedelta(seconds = vc.track.length))}")
    em.add_field(name = "Информация", value = f"URL: {str(vc.track.uri)}")
    return await ctx.send(embed = em, ephemeral=True)

# @bot.command()
# async def splay(ctx: commands.Context, *, search: str):
#     em1 = nextcord.Embed(description=f"Хммм? Сначала зайди в голосовой канал")
#     if not ctx.voice_client:
#         return await ctx.send("Я не в голосовом канале")
#     elif not getattr(ctx.author.voice, "channel", None):
#         return await ctx.send("Хммм? Сначала зайди в голосовой канал")
#     elif not ctx.author.voice == ctx.me.voice:
#         return await ctx.send("Ты в другом канале. Зайди в другой голосовой канал")
#     else:
#         vc: wavelink.Player = ctx.voice_clie

#     if vc.queue.is_empty and not vc.is_playing():
#         try:
#             track = await spotify.SpotifyTrack.search(query = search, return_first = True)
#             await vc.play(track)
#             em = nextcord.Embed(title = f"Сейчас играет {vc.track.title}", description = f"Артист: {vc.track.author}", color = 0xf0cc0a)
#             em.add_field(name = "Продолжительность", value = f"{str(datetime.timedelta(seconds = vc.track.length))}")
#             em.add_field(name = "Информация", value = f"URL: {str(vc.track.uri)}")
#             em.set_image(url = 'https://i.ibb.co/ggJPTRH/Minecraft-1-18-2-2022-03-19-14-46-33-2.gif')
#             em.set_author(name="MineLandy", icon_url="https://i.ibb.co/CWLjzyv/308505.png")
#             em.set_thumbnail(url = 'https://i.ibb.co/fvz5KbM/61b541009ce0a981919641.png')
#             em.timestamp = datetime.datetime.now()
#             em.set_footer(text='\u200b',icon_url="https://i.ibb.co/GMZR9js/image.png")
#             await ctx.send(embed=em)
#         except Exception as abc:
#             await ctx.send("Пожалуйста введи **spotify** ссылку")
#             return print(abc)
        
#     else:
#         await vc.queue.put_wait(track)
#         em = nextcord.Embed(title = f"Сейчас играет {vc.track.title}", description = f"Артист: {vc.track.author}", color = 0xf0cc0a)
#         em.add_field(name = "Продолжительность", value = f"{str(datetime.timedelta(seconds = vc.track.length))}")
#         em.add_field(name = "Информация", value = f"URL: {str(vc.track.uri)}")
#         em.set_image(url = 'https://i.ibb.co/ggJPTRH/Minecraft-1-18-2-2022-03-19-14-46-33-2.gif')
#         em.set_author(name="MineLandy", icon_url="https://i.ibb.co/CWLjzyv/308505.png")
#         em.set_thumbnail(url = 'https://i.ibb.co/fvz5KbM/61b541009ce0a981919641.png')
#         em.timestamp = datetime.datetime.now()
#         em.set_footer(text='\u200b',icon_url="https://i.ibb.co/GMZR9js/image.png")
#         await ctx.send(embed=em)
#     vc.ctx = ctx
#     if vc.loop:
#         return
#     setattr(vc, "loop", False)

#minecraft

@bot.command()
async def mine(ctx):
    server = MinecraftServer.lookup("mc.minelandy.me")
    status = server.status()
    await ctx.send("The server has {0} players and replied in {1} ms".format(status.players.online, status.latency))
    latency = server.ping()
    await ctx.send("The server replied in {0} ms".format(latency))
    
    em = nextcord.Embed(description = "Игркои {0} \n пинг{1}".format(status.players.online, status.latency), color = 0xe25a00)
    em.add_field(name = "Информация", value = f"MineLandy 1.18.2 Ванилла Мы за честную игру, заходи к нам!")
    em.set_author(name="MineLandy", icon_url="https://i.ibb.co/CWLjzyv/308505.png")
    em.set_thumbnail(url = 'https://i.ibb.co/fvz5KbM/61b541009ce0a981919641.png')
    em.set_footer(text=f'\u200b {ctx.author.display_name}', icon_url=ctx.author.display_avatar)
    await ctx.send(embed=em)
    
bot.run(TOKEN)