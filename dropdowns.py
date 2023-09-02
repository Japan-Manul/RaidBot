import discord
from tools import write_to_log, translate, db


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