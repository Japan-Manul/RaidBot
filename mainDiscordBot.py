import asyncio
import sqlite3 as sql
from time import strftime, strptime, ctime

import pyautogui as ag
from discord.ext import tasks, commands

from tools import write_to_log, translate, db
from dropdowns import *
from ScreenAnalyzer import analyze_cycle, build_image
from settings import config


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

sends_flag = True

@bot.event
async def on_ready():
    write_to_log('main', 'launch')
    start_count.start()
    write_to_log('main', 'loop_event', 'start_count started')


@tasks.loop(seconds=1)
async def start_count():
    curtime = strptime(ctime())
    time_to_start = (curtime[4] - curtime[4] % 7.5 + 7.5) * 60 - (curtime[4] * 60 + curtime[5])
    print('time to start ', time_to_start)
    if (curtime[4] * 60 + curtime[5]) % 450 == 0:
        await asyncio.sleep(1)
        slow_count.start()
        write_to_log('main', 'loop_event', 'slow_count started')
        start_count.stop()
        write_to_log('main', 'loop_event', 'start_count stopped')


@tasks.loop(seconds=450)
async def slow_count():
    curtime = strptime(ctime())
    write_to_log('main', 'loop_event', 'slow_count tick')
    if curtime[4] % 30 == 0 and sends_flag:
        result = analyze_cycle()
        write_to_log('main', 'analyze_cycle', f'result: {result}')

        admin = await bot.fetch_user(config['admin_id'])
        file1 = discord.File(fr"{config['base_dir']}\temp\ProcessScreenE.jpg", filename="imageE.jpg")
        file2 = discord.File(fr"{config['base_dir']}\temp\ProcessScreenM.jpg", filename="imageM.jpg")
        file3 = discord.File(fr"{config['base_dir']}\temp\ProcessScreenH.jpg", filename="imageH.jpg")
        await admin.send(f'{result}', files=(file1, file2, file3))

        embed_easy = discord.Embed(title='Легкий рейд', colour=discord.Colour.orange())
        embed_mid = discord.Embed(title='Средний рейд', colour=discord.Colour.blurple())
        embed_hard = discord.Embed(title='Сложный рейд', colour=discord.Colour.purple())

        embed_easy.add_field(name=translate(result['Easy'][0]),
                             value=f'{translate(result["Easy"][2])}, {translate(result["Easy"][1])}')
        embed_mid.add_field(name=translate(result['Mid'][0]),
                            value=f'{translate(result["Mid"][2])}, {translate(result["Mid"][1])}')
        embed_hard.add_field(name=translate(result['Hard'][0]),
                             value=f'{translate(result["Hard"][2])}, {translate(result["Hard"][1])}')

        embed_easy.set_thumbnail(
            url='https://static.wikia.nocookie.net/crossout/images/8/8e/%D0%9C%D0%B5%D0%B4%D1%8C.png/revision/latest?cb=20170613081917&path-prefix=ru')
        embed_mid.set_thumbnail(
            url='https://static.wikia.nocookie.net/crossout/images/8/80/%D0%9F%D0%BB%D0%B0%D1%81%D1%82%D0%B8%D0%BA.png/revision/latest/scale-to-width-down/280?cb=20180522135255&path-prefix=ru')
        embed_hard.set_thumbnail(
            url='https://static.wikia.nocookie.net/crossout/images/a/ac/%D0%AD%D0%BB%D0%B5%D0%BA%D1%82%D1%80%D0%BE%D0%BD%D0%B8%D0%BA%D0%B0.png/revision/latest/scale-to-width-down/279?cb=20170613085834&path-prefix=ru')

        build_image('Easy', result['Easy'])
        build_image('Mid', result['Mid'])
        build_image('Hard', result['Hard'])

        embed_easy.set_image(url="attachment://imageE.jpg")
        embed_mid.set_image(url="attachment://imageM.jpg")
        embed_hard.set_image(url="attachment://imageH.jpg")

        embed_easy.set_author(name=f'{curtime[3]}:{curtime[4] if curtime[4] != 0 else "00"}')

        with db:
            curs = db.cursor()
            curs.execute("SELECT channel_id FROM servers")
            channel_ids = curs.fetchall()
            db.commit()
            curs.close()
        write_to_log('sends', 'start_channels_sends')
        for id in channel_ids:
            file_easy = discord.File(fr"{config['base_dir']}\temp\Easy.jpg", filename="imageE.jpg")
            file_mid = discord.File(fr"{config['base_dir']}\temp\Mid.jpg", filename="imageM.jpg")
            file_hard = discord.File(fr"{config['base_dir']}\temp\Hard.jpg", filename="imageH.jpg")
            try:
                channel = await bot.fetch_channel(f'{id[0]}')
                await channel.send(files=(file_easy, file_mid, file_hard), embeds=(embed_easy, embed_mid, embed_hard),
                                   delete_after=1800)
                write_to_log('sends', 'channel_send', f"channel_id:'{id[0]}'")
            except:
                write_to_log('sends', 'channel_error', f"channel_id:'{id[0]}'")

        with db:
            curs = db.cursor()
            curs.execute("SELECT user_id FROM users")
            user_ids = curs.fetchall()
            db.commit()
            curs.close()
        write_to_log('sends', 'start_users_sends')
        for user_id in user_ids:
            for diff in 'Easy', 'Mid', 'Hard':
                curr_embed = embed_easy if diff == 'Easy' else embed_mid if diff == 'Mid' else embed_hard
                with db:
                    curs = db.cursor()
                    curs.execute(
                        f"SELECT * FROM requests WHERE user_id = '{user_id[0]}' AND diff = '{diff}' AND raid = '{result[diff][0]}'")
                    curr_requests = curs.fetchall()
                    db.commit()
                    curs.close()
                for request in curr_requests:
                    if (result[diff][2] in request[4].split('$')) and (result[diff][1] in request[5].split('$')):
                        try:
                            user = await bot.fetch_user(f"{user_id[0]}")
                            curr_file = discord.File(fr"{config['base_dir']}\temp\{diff}.jpg",
                                                     filename=f"image{diff[0]}.jpg")
                            await user.send(file=curr_file, embed=curr_embed)
                            write_to_log('sends', 'user_send', f"user_id:'{user_id[0]}'")
                        except:
                            write_to_log('sends', 'user_error', f"user_id:'{user_id[0]}'")
        write_to_log('sends', 'end_sends')
    else:
        ag.moveTo(320, 430)
        ag.click()


@bot.command()
async def add(ctx):
    view = DiffSelect()
    await ctx.reply('Загляни в личку!')
    await ctx.author.send(view=view)


@bot.command()
async def delete(ctx):
    with db:
        curs = db.cursor()
        curs.execute(f"SELECT * FROM requests WHERE user_id = {ctx.author.id}")
        rows = curs.fetchall()
        db.commit()
        curs.close()
    view = DeleteView(rows)
    await ctx.reply('Загляни в личку!')
    await ctx.author.send(view=view)


@bot.command()
async def show(ctx):
    text = f'{ctx.author} requests\n'
    curs = db.cursor()
    curs.execute(f"SELECT diff,raid,maps,factions FROM requests WHERE user_id = {ctx.author.id}")
    rows = curs.fetchall()
    for row in rows:
        text += f'> {row}\n'
    curs.close()
    write_to_log('commands', 'show', f"id:'{ctx.author.id}'")
    await ctx.reply('Загляни в личку!', )
    await ctx.author.send(text)


@bot.command()
async def choose_channel(ctx):
    with db:
        curs = db.cursor()
        write_to_log('db', 'INSERT', f"into 'servers' values ('{str(ctx.guild.id)}','{str(ctx.channel.id)}')")
        curs.execute(
            f"INSERT OR REPLACE INTO servers (server, channel_id) VALUES ('{str(ctx.guild.id)}','{str(ctx.channel.id)}')")
        db.commit()
        curs.close()
    await ctx.reply(
        f'Канал #{ctx.channel} был выбран для сервера "{ctx.guild}", вы можете использовать >delete_channel чтобы удалить сервер из базы данных')
    write_to_log('commands', 'choose_channel', f"guild_id:'{ctx.guild.id}' channel_id:'{ctx.channel.id}'")


@bot.command()
async def delete_channel(ctx):
    with db:
        curs = db.cursor()
        write_to_log('db', 'DELETE', f"from 'servers' where 'id'={ctx.guild.id}")
        curs.execute(f"DELETE FROM servers WHERE server = '{str(ctx.guild.id)}'")
        db.commit()
        curs.close()
    await ctx.reply(
        f'Сервер "{ctx.guild}" был удалён из базы данных, вы можете использовать >choose_channel чтобы выбрать новый канал для этого сервера.')
    write_to_log('commands', 'delete_channel', f"guild_id:'{ctx.guild.id}'")


@bot.command()
@commands.is_owner()
async def admin_send(ctx, mode):
    if mode == 'logs':
        file_names = ('logs/main.log', 'logs/sends.log', 'logs/commands.log', 'logs/db.log')
    elif mode == 'temp':
        file_names = ('temp/ProcessScreenE.jpg', 'temp/ProcessScreenM.jpg', 'temp/ProcessScreenH.jpg', 'temp/Easy.jpg', 'temp/Mid.jpg', 'temp/Hard.jpg')
    elif mode == 'db':
        file_names = ('CrossDataBase.db',)
    else:
        file_names = ()

    files = []
    for file_name in file_names:
        files.append(discord.File(fr"{config['base_dir']}\{file_name}", filename=f"{file_name}"))
    await ctx.reply('Держи', files=files)


@bot.command()
@commands.is_owner()
async def admin_loop(ctx, mode):
    if mode == 'start':
        start_count.start()
        await ctx.reply('start_count запущен')
        write_to_log('main', 'loop_event', 'start_count started')
        write_to_log('commands', 'admin_loop', 'start')
    elif mode == 'stop':
        slow_count.stop()
        await ctx.reply('slow_count приостановлен')
        write_to_log('main', 'loop_event', 'slow_count stopped')
        write_to_log('commands', 'admin_loop', 'stop')
    else:
        await ctx.reply('Команда не распознана')
        write_to_log('commands', 'admin_loop', 'unknown mode')


@bot.command()
@commands.is_owner()
async def admin_sends(ctx, mode):
    if mode == 'start':
        global sends_flag
        sends_flag = True
        await ctx.reply('рассылки возобновлены')
        write_to_log('sends', 'sends resumed by admin')
        write_to_log('commands', 'admin_sends', 'start')
    elif mode == 'stop':
        global sends_flag
        sends_flag = False
        await ctx.reply('рассылки приостановлены')
        write_to_log('sends', 'sends stopped by admin')
        write_to_log('commands', 'admin_sends', 'stop')
    else:
        await ctx.reply('Команда не распознана')
        write_to_log('commands', 'admin_sends', 'unknown mode')


bot.run(config['token'])
