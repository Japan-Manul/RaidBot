from time import strftime, strptime, ctime
import sqlite3 as sql

import discord
from discord.ext import tasks, commands
from discord.ext.commands import Bot

from ScreenAnalyzer import *
from settings import config

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

db = sql.connect('CrossDataBase.db')
with db:
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    user_id STRING, 
    diff STRING, 
    raid STRING, 
    maps STRING, 
    factions STRING
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id STRING PRIMARY KEY, 
    time STRING DEFAULT '0'
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS servers (
    server STRING PRIMARY KEY, 
    channel_id STRING
    )""")
    db.commit()
    cursor.close()


class RaidSelect(discord.ui.Select):
    def __init__(self, mod):
        cur_options = []
        if mod == 'Easy':
            cur_options = [('Последний конвой', 'TheLastConvoy'), ('Стальная колыбель', 'SteelCradle'),
                           ('Прорыв периметра', 'PerimeterBreach'), ('Война за огонь', 'TheWarForFire'),
                           ('Бей и беги', 'HitAndRun'), ('Похищение данных', 'DataTheft'),
                           ('Угнать за пару минут', 'GoneInTwoMinutes')]
        elif mod in ('Mid', 'Hard'):
            cur_options = [('Последний конвой', 'TheLastConvoy'), ('Стальная колыбель', 'SteelCradle'),
                           ('Прорыв периметра', 'PerimeterBreach'), ('Война за огонь', 'TheWarForFire'),
                           ('Бей и беги', 'HitAndRun'), ('Похищение данных', 'DataTheft'),
                           ('Угнать за пару минут', 'GoneInTwoMinutes'), ('Оборона рубежа', 'FrontierDefense')]
        options = []
        for option in cur_options:
            options.append(discord.SelectOption(label=f"{option[0]}", value=f"{option[1]}"))
        super().__init__(options=options, placeholder="Выбери рейд")

    async def callback(self, interaction: discord.Interaction):
        await self.view.select_raid(interaction, self.values)


class MapSelect(discord.ui.Select):
    def __init__(self, mod):
        cur_options = []
        if mod in ('GoneInTwoMinutes', 'HitAndRun', 'TheLastConvoy'):
            max_value = 3
            cur_options = [('Чертовы рудники', 'CursedMines'), ('Мертвое шоссе', 'DeadHighway'),
                           ('Восточный ретранслятор', 'EasternArray')]
        elif mod in ('DataTheft', 'TheWarForFire'):
            max_value = 8
            cur_options = [('Мост', 'Bridge'), ('Тэц', 'Powerplant'), ('Старый город', 'OldTown'),
                           ('Химический завод', 'ChemicalPlant'), ('Гнев Хана', 'WrathOfKhan'),
                           ('Кладбище кораблей', 'ShipGraveyard'), ('Каньон основателей', 'FoundersCanyon'),
                           ('Рок-сити', 'RockCity')]
        elif mod == 'FrontierDefense':
            max_value = 6
            cur_options = [('Мост', 'Bridge'), ('Химический завод', 'ChemicalPlant'), ('Кратер', 'Crater'),
                           ('Крепость', 'Fortress'), ('Кладбище кораблей', 'ShipGraveyard'), ('Рок-сити', 'RockCity')]

        elif mod == 'PerimeterBreach':
            max_value = 2
            cur_options = [('Затерянный берег', 'LostCoast'), ('Терминал-45', 'Terminal45')]

        elif mod == 'SteelCradle':
            max_value = 4
            cur_options = [('Химический завод', 'ChemicalPlant'), ('Фабрика', 'Factory'), ('Гнев Хана', 'WrathOfKhan'),
                           ('Кладбище кораблей', 'ShipGraveyard')]
        options = []
        for option in cur_options:
            options.append(discord.SelectOption(label=f"{option[0]}", value=f"{option[1]}"))
        super().__init__(options=options, placeholder="Выбери карты", max_values=max_value)

    async def callback(self, interaction: discord.Interaction):
        await self.view.select_map(interaction, self.values)


class FactionSelect(discord.ui.Select):
    def __init__(self, mod):
        cur_options = []
        if mod == 'Easy':
            max_value = 3
            cur_options = [('Бешеные', 'Lunatics'), ('Скитальцы', 'Nomads'), ('Мусорщики', 'Scavengers')]
        elif mod in ('Mid', 'Hard'):
            max_value = 6
            cur_options = [('Бешеные', 'Lunatics'), ('Огнепоклонники', 'FireStarters'), ('Скитальцы', 'Nomads'),
                           ('Дети рассвета', 'DawnsChildren'), ('Мусорщики', 'Scavengers'),
                           ('Степные волки', 'Steppenwolfs')]
        options = []
        for option in cur_options:
            options.append(discord.SelectOption(label=f"{option[0]}", value=f"{option[1]}"))
        super().__init__(options=options, placeholder="Выбери фракции", max_values=max_value)

    async def callback(self, interaction: discord.Interaction):
        await self.view.select_faction(interaction, self.values)


class DiffSelect(discord.ui.View):
    answer1 = None
    answer2 = None
    answer3 = None
    answer4 = None

    @discord.ui.select(
        placeholder="Выбери сложность",
        options=[
            discord.SelectOption(label="Лёгкая", value="Easy"),
            discord.SelectOption(label="Средняя", value="Mid"),
            discord.SelectOption(label="Сложная", value="Hard")
        ]
    )
    async def select_diff(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        self.answer1 = select_item.values
        self.children[0].disabled = True
        raid_select = RaidSelect(self.answer1[0])
        self.add_item(raid_select)
        await interaction.message.edit(view=self)
        await interaction.response.defer()

    async def select_raid(self, interaction: discord.Interaction, choices):
        self.answer2 = choices
        self.children[1].disabled = True
        map_select = MapSelect(self.answer2[0])
        self.add_item(map_select)
        await interaction.message.edit(view=self)
        await interaction.response.defer()

    async def select_map(self, interaction: discord.Interaction, choices):
        self.answer3 = choices
        self.children[2].disabled = True
        faction_select = FactionSelect(self.answer1[0])
        self.add_item(faction_select)
        await interaction.message.edit(view=self)
        await interaction.response.defer()

    async def select_faction(self, interaction: discord.Interaction, choices):
        self.answer4 = choices
        self.children[3].disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        write_to_log('commands', 'add',
                     f"id:'{interaction.user.id}' diff:'{self.answer1}' raid:'{self.answer2}' maps:'{self.answer3}' factions:'{self.answer4}'")
        with db:
            curs = db.cursor()

            maps_string = ''
            for elem in self.answer3:
                maps_string += elem + '$'
            maps_string = maps_string[:-1]

            factions_string = ''
            for elem in self.answer4:
                factions_string += elem + '$'
            factions_string = factions_string[:-1]

            write_to_log('db', 'INSERT',
                         f"into 'requests' values ('{str(interaction.user.id)}','{self.answer1[0]}','{self.answer2[0]}','{maps_string}','{factions_string}')")
            curs.execute(
                f"INSERT INTO requests (user_id,diff,raid,maps,factions) VALUES ('{str(interaction.user.id)}','{self.answer1[0]}','{self.answer2[0]}','{maps_string}','{factions_string}')")
            curs.execute(f"SELECT * FROM users WHERE user_id = '{str(interaction.user.id)}'")
            if len(curs.fetchall()) == 0:
                write_to_log('db', 'INSERT', f"into 'users' values ('{str(interaction.user.id)}'")
                curs.execute(f"INSERT INTO users (user_id) VALUES ('{str(interaction.user.id)}')")
            db.commit()
            curs.close()
        self.stop()


def translate(word):
    ru_eng_dict = {
        'Easy': 'Лёгкий',
        'Mid': 'Средний',
        'Hard': 'Тяжёлый',
        'DawnsChildren': 'Дети Рассвета',
        'FireStarters': 'Огнепоклонники',
        'Lunatics': 'Бешеные',
        'Nomads': 'Скитальцы',
        'Scavengers': 'Мусорщики',
        'Steppenwolfs': 'Степные волки',
        'Bridge': 'Мост',
        'ChemicalPlant': 'Химический завод',
        'Crater': 'Кратер',
        'CursedMines': 'Чертовы рудники',
        'DeadHighway': 'Мертвое шоссе',
        'EasternArray': 'Восточный ретранслятор',
        'Factory': 'Фабрика',
        'Fortress': 'Крепость',
        'FoundersCanyon': 'Каньон основателей',
        'LostCoast': 'Затерянный берег',
        'OldTown': 'Старый город',
        'Powerplant': 'ТЭЦ',
        'RockCity': 'Рок-Сити',
        'ShipGraveyard': 'Кладбище кораблей',
        'Terminal45': 'Терминал-45',
        'WrathOfKhan': 'Гнев Хана',
        'DataTheft': 'Похищение данных',
        'FrontierDefense': 'Оборона рубежа',
        'GoneInTwoMinutes': 'Угнать за пару минут',
        'HitAndRun': 'Бей и беги',
        'PerimeterBreach': 'Прорыв периметра',
        'SteelCradle': 'Стальная колыбель',
        'TheLastConvoy': 'Последний конвой',
        'TheWarForFire': 'Война за огонь'}
    return ru_eng_dict[word]


class DeleteSelect(discord.ui.Select):

    def __init__(self, rows):
        options = []
        for row in rows:
            options.append(
                discord.SelectOption(label=f'{translate(row[2])} - {translate(row[3])}', value=f'{row[0]}',
                                     description=f'{str(list(map(translate, row[4].split("$"))))[:99:]}'))
        super().__init__(
            placeholder="Выбери пункты, которые хочешь удалить.",
            min_values=1,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.MessageInteraction):
        await self.view.select_delete(interaction, self.values)


class DeleteView(discord.ui.View):
    answer = None

    def __init__(self, rows):
        super().__init__()
        self.add_item(DeleteSelect(rows))

    async def select_delete(self, interaction: discord.Interaction, choices):
        self.answer = choices
        self.children[0].disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        write_to_log('commands', 'delete', f"choice:'{self.answer}'")
        with db:
            curs = db.cursor()
            for answer in self.answer:
                curs.execute(f"DELETE FROM requests WHERE id={answer}")
                write_to_log('db', 'DELETE', f"from 'requests' where 'id'={answer}")
            db.commit()
            curs.close()
        self.stop()


def write_to_log(file, event, description=None):
    if description:
        text = f'{strftime("%x %X")} | <{event}>: {description}\n'
    else:
        text = f'{strftime("%x %X")} |----<{event + ">":{"-"}{"<"}{40}}\n'
    with open(fr"logs\{file}.log", "a") as f:
        f.write(text)
        print(text)


@tasks.loop(seconds=450)
async def slow_count():
    curtime = strptime(ctime())
    write_to_log('main', 'loop_event', 'slow_count tick')
    if curtime[4] % 30 == 0:
        result = analyze_cycle()
        write_to_log('main', 'analyze_cycle', f'result: {result}')

        admin = await bot.fetch_user(config['admin_id'])
        file1 = discord.File(fr"{config['base_dir']}\temp\ProcessScreenE.jpg", filename="imageE.jpg")
        file2 = discord.File(fr"{config['base_dir']}\temp\ProcessScreenM.jpg", filename="imageM.jpg")
        file3 = discord.File(fr"{config['base_dir']}\temp\ProcessScreenH.jpg", filename="imageH.jpg")
        await admin.send(f'{result}',files=(file1, file2, file3))

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
                write_to_log('sends','channel_send',f"channel_id:'{id[0]}'")
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
            with db:
                curs = db.cursor()
                curs.execute(
                    f"SELECT * FROM requests WHERE user_id = '{user_id[0]}' AND diff = 'Easy' AND raid = '{result['Easy'][0]}'")
                easy_requests = curs.fetchall()
                db.commit()
                curs.close()

            for request in easy_requests:
                if (result['Easy'][2] in request[4].split('$')) and (result['Easy'][1] in request[5].split('$')):
                    try:
                        user = await bot.fetch_user(f"{user_id[0]}")
                        file_easy = discord.File(fr"{config['base_dir']}\temp\Easy.jpg",
                                                 filename="imageE.jpg")
                        await user.send(file=file_easy, embed=embed_easy)
                        write_to_log('sends','user_send',f"user_id:'{id[0]}'")
                    except:
                        write_to_log('sends','user_error',f"user_id:'{id[0]}'")
            with db:
                curs = db.cursor()
                curs.execute(
                    f"SELECT * FROM requests WHERE user_id = {user_id[0]} AND diff = 'Mid' AND raid = '{result['Mid'][0]}'")
                mid_requests = curs.fetchall()
                db.commit()
                curs.close()
            for request in mid_requests:
                if (result['Mid'][2] in request[4].split('$')) and (result['Mid'][1] in request[5].split('$')):
                    try:
                        user = await bot.fetch_user(f'{user_id[0]}')
                        file_mid = discord.File(fr"{config['base_dir']}\temp\Mid.jpg",
                                                filename="imageM.jpg")
                        await user.send(file=file_mid, embed=embed_mid)
                        write_to_log('sends', 'user_send', f"user_id:'{id[0]}'")
                    except:
                        write_to_log('sends','user_error',f"user_id:'{id[0]}'")
            with db:
                curs = db.cursor()
                curs.execute(
                    f"SELECT * FROM requests WHERE user_id = {user_id[0]} AND diff = 'Hard' AND raid = '{result['Hard'][0]}'")
                hard_requests = curs.fetchall()
                db.commit()
                curs.close()
            for request in hard_requests:
                if (result['Hard'][2] in request[4].split('$')) and (result['Hard'][1] in request[5].split('$')):
                    try:
                        user = await bot.fetch_user(f'{user_id[0]}')
                        file_hard = discord.File(fr"{config['base_dir']}\temp\Hard.jpg",
                                                 filename="imageH.jpg")
                        await user.send(file=file_hard, embed=embed_hard)
                        write_to_log('sends', 'user_send', f"user_id:'{id[0]}'")
                    except:
                        write_to_log('sends', 'user_error', f"user_id:'{id[0]}'")

    else:
        pyautogui.moveTo(320, 430)
        pyautogui.click()


@tasks.loop(seconds=1)
async def start_count():
    curtime = strptime(ctime())
    time_to_start = (curtime[4] - curtime[4] % 7.5 + 7.5) * 60 - (curtime[4] * 60 + curtime[5])
    print('time to start ', time_to_start)
    if (curtime[4] * 60 + curtime[5]) % 450 == 0:
        sleep(1)
        slow_count.start()
        write_to_log('main', 'loop_event', 'slow_count started')
        start_count.stop()
        write_to_log('main', 'loop_event', 'start_count was stopped')


@bot.event
async def on_ready():
    # curtime = strptime(ctime())
    # time_to_start = (curtime[4] - curtime[4] % 7.5 + 7.5) * 60 - (curtime[4] * 60 + curtime[5])
    # print(time_to_start)
    # time.sleep(time_to_start)
    # slow_count.start()
    print('начало работы')
    write_to_log('main', 'launch')
    start_count.start()
    print('start_count запущен')
    write_to_log('main', 'loop_event', 'start_count started')


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
    print('<choose_channel>', [ctx.guild.id, ctx.channel.id])
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
    print('<delete_channel>', [ctx.guild.id, ctx.channel.id])
    with db:
        curs = db.cursor()
        write_to_log('db', 'DELETE', f"from 'servers' where 'id'={ctx.guild.id}")
        curs.execute(f"DELETE FROM servers WHERE server = '{str(ctx.guild.id)}'")
        db.commit()
        curs.close()
    await ctx.reply(
        f'Сервер "{ctx.guild}" был удалён из базы данных, вы можете использовать >choose_channel чтобы выбрать новый канал для этого сервера.')
    write_to_log('commands', 'delete_channel', f"guild_id:'{ctx.guild.id}'")

bot.run(config['token'])
