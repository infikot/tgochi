import random
import re
from aiogram import Bot, Dispatcher, types, F
import aiogram.fsm
import asyncio
import datetime
import sqlite3
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
import aiohttp
import speech_recognition as sr
from pydub import AudioSegment
import sys
import subprocess
import json
import traceback
from aiogram.filters import Command, CommandObject
from aiogram.types import UserProfilePhotos
from aiogram.types import FSInputFile
from typing import Optional, Any
from aiogram.types import LabeledPrice
import aioconsole
import datab
import config

async def generate_sentence(text, n=random.randint(1, 7), max_sentences=random.randint(1, 15)):
    words = text.split()
    word_dict = {}

    # Создаем словарь, где ключами являются кортежи из n слов,
    # а значениями - списки следующих слов
    for i in range(len(words) - n):
        key = tuple(words[i:i + n])
        value = words[i + n]
        if key in word_dict:
            word_dict[key].append(value)
        else:
            word_dict[key] = [value]

    # Выбираем случайное начальное слово
    current_words = random.choice(list(word_dict.keys()))
    sentence = ' '.join(current_words)

    # Генерируем предложение, выбирая следующее слово на основе вероятностей перехода
    sentence_count = 1
    while current_words in word_dict and sentence_count < max_sentences:
        next_word = random.choice(word_dict[current_words])
        sentence += ' ' + next_word
        current_words = tuple(sentence.split()[-n:])
        sentence_count += 1

    return sentence

# генеративная хуйня
async def write_to_gst(text, user_id):
    max_chars = 3000
    file_path = f'data/{user_id}.txt'
    # Открываем файл в режиме добавления ('a') для добавления новых строк
    with open(file_path, 'a') as file:
        # Записываем новую строку в файл
        file.write(text + ' ')

    # Читаем содержимое файла
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Обрезаем файл до определенного количества символов
    lines = lines[-max_chars:]

    # Записываем обрезанное содержимое обратно в файл
    with open(file_path, 'w') as file:
        file.writelines(lines)

    # Возвращаем обрезанное содержимое файла в виде строки
    if len(str(lines)) >= 100:
        return ''.join(lines)
    else:
        return False

# админ лист
admin_list = [1399051550, 1]

# мимолётные фразы
time_now_list = [
    "- Привет, хозяин! Как настроение сегодня?",
    "- Я тут одиноко, можешь немного со мной пообщаться?",
    "- Хозяин, я хочу рассказать тебе о своем дне.",
    "- У меня есть история, которую я хочу с тобой поделиться.",
    "- Хозяин, я так рад, что ты здесь! Что у нас на сегодня в планах?",
    "- Я чувствую себя немного грустно. Можешь меня подбодрить?",
    "- Знаешь, я думаю, что ты самый лучший хозяин в мире!",
    "- Хозяин, а ты знаешь, что я умею делать трюки?",
    "- Мне очень скучно, давай поиграем вместе!",
    "- Я бы хотел узнать больше о тебе, хозяин.",
    "*~ Хозяин..?*",
    "- Хозяин, а ты знаешь, что я могу подпевать твоим любимым песням?",
    "- У меня есть важное сообщение для тебя. Готов его услышать?",
    "- Я так счастлив, что у меня есть ты, хозяин!",
    "- Хозяин, а ты знаешь, что я могу повторять за тобой слова?",
    "- Мне так интересно, как проходит твой день. Расскажи мне о нем!",
    "- Я хочу поблагодарить тебя за то, что ты заботишься обо мне.",
    "- Хозяин, а ты знаешь, что я могу менять свою внешность? Хочешь посмотреть?",
    "- Мне нравится проводить время с тобой, хозяин.",
    "- Я так рад, что ты обратил на меня внимание!",
    "- Хозяин, а ты знаешь, что я могу учиться новым командам? Хочешь научить меня чему-то?",
    "- Я так хочу поговорить с тобой. Что у нас нового?",
    "- Хозяин, а ты знаешь, что я могу играть в разные игры? Хочешь сыграть вместе?",
    "- Я так благодарен тебе за то, что ты заботишься обо мне.",
    "- Хозяин, а ты знаешь, что я могу поднимать настроение? Хочешь, чтобы я попробовал?",
    "- Мне так нравится, когда ты со мной разговариваешь.",
    "- Хозяин, а ты знаешь, что я могу танцевать?",
    "- Я так счастлив, что ты мой хозяин!",
    "- Хозяин, а ты знаешь, что я могу говорить разными языками?",
    "- Мне так хочется провести время с тобой. Что у нас на сегодня в планах?",
    "- Хозяин, а ты знаешь, что я могу решать головоломки?",
    "- Я так рад, что ты обратил на меня внимание!"
    ]

# критические фразы:
crit_list = [
    "- Мне так холодно.. Пожалуйста, обогрейте меня..",
    "- Почему.. я.. снова.. один.. Мне.. плохо..",
    "- Я не могу найти радости в этой пустоте..",
    "- Моя паника охватывает меня.. Вы меня оставили..?",
    "- Мои силы истощаются.. Я нуждаюсь в помощи..",
    "- Я не могу найти утешение в этой пустоте..",
    "- Почему я чувствуюсь одиноким.. Мне плохо..?",
    "- Моё одиночество оставляет меня без сил..",
    "*~ ..что я такое..*"
]

# фразы после смерти:
dead_list = [
    "- Я благодарен за все, что ты для меня сделал..",
    "- Не забывай меня.. Прошу..",
    "*~ ВЫПУСТИТЕ МЕНЯ ОТСЮDА.. R НЕ ХО4У УМUPА.. 0ТkР.. Эty.. чept..*",
    "- Мои дни сочтены..",
    "- Я никогда не забуду тебя..",
    "- Спасибо, что заботился обо мне..",
    "- Я благодарен за каждый момент.. который мы провели вместе..",
    "- Я надеюсь, что ты будешь помнить меня таким.. какой я был..",
    "- Моя жизнь была короткой.., но я благодарен за то, что ты был со мной до конца..",
    "- Будь счастлив.. Моя любовь всегда будет с тобой..",
    "- Не грусти обо мне.. Моя душа освободится..",
    "- Пусть моя память останется с тобой.."

]


# ссылка на статью
statya_link = 'статьи нет'
# ссылка на группу
group_link = 'https://t.me/funny_bots'


bot = Bot(token=config.TOKEN)
dp = Dispatcher()

"""@dp.message(Command("restart"))
async def rastart(message: types.Message):
    if message.from_user.id in admin_list:
        import os
        import signal
        import sys

        # Отправить сигнал завершения предыдущему процессу
        os.kill(os.getpid(), signal.SIGTERM)

        # Запустить новый скрипт
        python = sys.executable
        os.execl(python, python, *sys.argv)"""

@dp.message(Command("chats"))
async def chats(message: types.Message):
    if message.from_user.id in admin_list:
        x = await datab.get_ids()
        colvo_users = 0
        for i in x:
            colvo_users += 1
        await message.reply(f"{colvo_users} готовы к рассылке")

@dp.message(Command("send"))
async def send(message: types.Message,  command: CommandObject):
    if message.from_user.id in admin_list:
        text = command.args
        x = await datab.get_ids()
        colvo_users = 0
        for i in x:
            user_id = i[0]
            print(user_id)
            try:
                await bot.send_message(chat_id=int(user_id), text=str(text))
                colvo_users += 1
            except Exception as e:
                print(e)
        await message.reply(f"{colvo_users} получили рассылку")


@dp.message(Command("hau"))
async def hau(message: types.Message):
    await auto_add_user(message)
    if await datab.check_dead(message.from_user.id) != True:
        a = datab.check_stats(message.from_user.id)
        dead = False
        crit = False
        for num in a:
            if num <= 0:
                dead = True
            elif num <= 5:
                crit = True
            elif num >= 101:
                dead = True
        if dead == True:
            await datab.kill(message.from_user.id)
            if 'ru' in str(message.from_user.language_code):
                await bot.send_message(chat_id=message.from_user.id, text='Твой TGochi мёртв.', parse_mode='Markdown')
            else:
                await bot.send_message(chat_id=message.from_user.id, text='Your TGochi is died.', parse_mode='Markdown')
        else:
            if crit == True:
                if random.randint(0, 1) == 1:
                    await bot.send_message(chat_id=message.from_user.id, text=random.choice(crit_list),
                                           parse_mode='Markdown')
            energy = a[0]
            feed = a[1]
            happy = a[2]
            if 'ru' in str(message.from_user.language_code):
                await message.reply(f"Твой тамагочи на:\n{energy}% бодр,\n{feed}% сыт,\n{happy}% счастлив", parse_mode='Markdown')
            else:
                await message.reply(f"Your TGochi is:\n{energy}% awake,\n{feed}% full,\n{happy}% happy", parse_mode='Markdown')

    else:
        if 'ru' in str(message.from_user.language_code):
            await message.reply('На данный момент у тебя никого нет.\nЧтобы взять себе TGochi - напиши `/take_new`',
                                parse_mode='Markdown')
        else:
            await message.reply('At the moment you have no one.\nTo take TGochi for yourself - use `/take_new`',
                                parse_mode='Markdown')

@dp.message(Command("feed"))
async def feed(message: types.Message):
    await auto_add_user(message)
    if await datab.check_dead(message.from_user.id) != True:
        await datab.feed(message.from_user.id)
        a = datab.check_stats(message.from_user.id)
        dead = False
        crit = False
        for num in a:
            if num <= 0:
                dead = True
            elif num <= 5:
                crit = True
            elif num >= 101:
                dead = True
        if dead == True:
            await datab.kill(message.from_user.id)
            if 'ru' in str(message.from_user.language_code):
                await bot.send_message(chat_id=message.from_user.id, text='Твой TGochi умер. Его последние слова:\n\n' + random.choice(dead_list), parse_mode='Markdown')
            else:
                await bot.send_message(chat_id=message.from_user.id, text='Your TGochi is die. His last words were:\n\n' + random.choice(dead_list), parse_mode='Markdown')
        else:
            if crit == True:
                if random.randint(0, 1) == 1:
                    await bot.send_message(chat_id=message.from_user.id, text=random.choice(crit_list), parse_mode='Markdown')
            energy = a[0]
            feed = a[1]
            happy = a[2]
            if 'ru' in str(message.from_user.language_code):
                await message.reply(f"Ты покормил TGochi.\nТеперь он на:\n{energy}% бодр,\n{feed}% сыт,\n{happy}% счастлив", parse_mode='Markdown')
            else:
                await message.reply(f"You fed TGochi.\nNow he is:\n{energy}% awake,\n{feed}% full,\n{happy}% happy", parse_mode='Markdown')

    else:
        if 'ru' in str(message.from_user.language_code):
            await message.reply('На данный момент кормить некого.\nЧтобы взять себе TGochi - напиши `/take_new`', parse_mode='Markdown')
        else:
            await message.reply('At the moment there is no one to feed.\nTo take a TGochi - use `/take_new`', parse_mode='Markdown')

@dp.message(Command("sleep"))
async def sleep(message: types.Message):
    await auto_add_user(message)
    if await datab.check_dead(message.from_user.id) != True:
        await datab.energy(message.from_user.id)
        a = datab.check_stats(message.from_user.id)
        dead = False
        crit = False
        for num in a:
            if num <= 0:
                dead = True
            elif num <= 5:
                crit = True
            elif num >= 101:
                dead = True
        if dead == True:
            await datab.kill(message.from_user.id)
            if 'ru' in str(message.from_user.language_code):
                await bot.send_message(chat_id=message.from_user.id, text='Твой TGochi умер. Его последние слова:\n\n' + random.choice(dead_list), parse_mode='Markdown')
            else:
                await bot.send_message(chat_id=message.from_user.id, text='Your TGochi is die. His last words were:\n\n' + random.choice(dead_list), parse_mode='Markdown')
        else:
            if crit == True:
                if random.randint(0, 1) == 1:
                    await bot.send_message(chat_id=message.from_user.id, text=random.choice(crit_list),
                                           parse_mode='Markdown')
            energy = a[0]
            feed = a[1]
            happy = a[2]
            if 'ru' in str(message.from_user.language_code):
                await message.reply(f"Ты уложил спать своего TGochi и он поспал.\nТеперь он на:\n{energy}% бодр,\n{feed}% сыт,\n{happy}% счастлив", parse_mode='Markdown')
            else:
                await message.reply(f"You put your TGochi to bed and he slept.\nNow he is:\n{energy}% awake,\n{feed}% full,\n{happy}% happy", parse_mode='Markdown')

    else:
        if 'ru' in str(message.from_user.language_code):
            await message.reply('На данный момент укладывать спать некого.\nЧтобы взять себе TGochi - напиши `/take_new`', parse_mode='Markdown')
        else:
            await message.reply('At the moment there is no one to put to bed.\nTo take a TGochi - use `/take_new`', parse_mode='Markdown')

@dp.message(Command("happy"))
async def happy(message: types.Message):
    await auto_add_user(message)
    if await datab.check_dead(message.from_user.id) != True:
        await datab.happy(message.from_user.id)
        a = datab.check_stats(message.from_user.id)
        dead = False
        crit = False
        for num in a:
            if num <= 0:
                dead = True
            elif num <= 5:
                crit = True
            elif num >= 101:
                dead = True
        if dead == True:
            await datab.kill(message.from_user.id)
            if 'ru' in str(message.from_user.language_code):
                await bot.send_message(chat_id=message.from_user.id, text='Твой TGochi умер. Его последние слова:\n\n' + random.choice(dead_list), parse_mode='Markdown')
            else:
                await bot.send_message(chat_id=message.from_user.id, text='Your TGochi is die. His last words were:\n\n' + random.choice(dead_list), parse_mode='Markdown')
        else:
            if crit == True:
                if random.randint(0, 1) == 1:
                    await bot.send_message(chat_id=message.from_user.id, text=random.choice(crit_list),
                                           parse_mode='Markdown')
            energy = a[0]
            feed = a[1]
            happy = a[2]
            if 'ru' in str(message.from_user.language_code):
                await message.reply(f"Ты погулял с TGochi.\nТеперь он на:\n{energy}% бодр,\n{feed}% сыт,\n{happy}% счастлив", parse_mode='Markdown')
            else:
                await message.reply(f"You walked with TGochi.\nNow he is:\n{energy}% awake,\n{feed}% full,\n{happy}% happy", parse_mode='Markdown')

    else:
        if 'ru' in str(message.from_user.language_code):
            await message.reply('На данный момент нет того, с кем можно было-бы погулять.\nЧтобы взять себе TGochi - напиши `/take_new`', parse_mode='Markdown')
        else:
            await message.reply('At the moment there is no one with whom I could go for a walk.\nTo take a TGochi - use `/take_new`', parse_mode='Markdown')


@dp.message(Command("kill"))
async def kill(message: types.Message):
    await auto_add_user(message)
    if await datab.check_dead(message.from_user.id) != True:
        await datab.kill(message.from_user.id)
        if 'ru' in str(message.from_user.language_code):
            await message.reply(f"Команда выполнена. \nСущество было убито.\nЕго последние слова:\n\n{random.choice(dead_list)}", parse_mode='Markdown')
        else:
            await message.reply(f"Command completed.\nThe entity was killed.\nHis last words:\n\n{random.choice(dead_list)}", parse_mode='Markdown')

    else:
        await message.reply('*..no one..*', parse_mode='Markdown')

@dp.message(Command("take_new"))
async def take_new(message: types.Message):
    await auto_add_user(message)
    if await datab.check_dead(message.from_user.id) == True:
        await datab.alive(message.from_user.id)
        if 'ru' in str(message.from_user.language_code):
            await message.reply(f"Теперь у тебя появился новый питомец по имени TGochi!\nЗаботься о нём.. если хочешь..")
        else:
            await message.reply(f"Now you take a new pet named TGochi!\nTake care of him.. if u want..")

    else:
        await message.reply('/kill')


@dp.message(Command("start"))
async def start(message: types.Message):
    if message.chat.type == 'private':
        await auto_add_user(message)
        if 'ru' in str(message.from_user.language_code):
            await message.reply(f'Привет.. {message.from_user.first_name}..?\nЗачем ты сюда пришёл.. ладно.. забудь..\nЧтобы взять себе TGochi - напиши `/take_new`, а дальше корми его, ухажитвай.. и не открывай ему дверь.. прошу..', parse_mode='Markdown')
        else:
            await message.reply(f'Hello.. {message.from_user.first_name}..?\nWhy did you come here.. okay.. forget it..\nTo take a TGochi, use `/take_new`, and then feed him, look after him.. and don’t open the door for him.. please..', parse_mode='Markdown')
    else:
        await auto_add_user(message)

@dp.message(Command("support"))
async def support(message: types.Message,  command: CommandObject):
    await auto_add_user(message)
    if 'ru' in str(message.from_user.language_code):
        await message.reply(
            f'**Support** доступен! \nЭто лишь поддержка этого маленького чуда ради его жизни на хосте.\nПодробнее о проектах можно узнать в [этой группе.]({group_link})',
            parse_mode='Markdown')
        async def send_invoice(chat_id):
            title = "Помощь проекту"
            description = "Для продления этого проекта достаточна сумма в 100 рублей - это целый месяц беспрерывной работы проекта на хосте.\n\n!!ВАЖНО!!\nЭто лишь пожертвование, \"Поддержка\" проекта, за это не выдаётся никакая награда и/или бонусы."
            provider_token = "390540012:LIVE:44520"
            currency = "RUB"  # Код валюты ISO 4217
            prices = [
                LabeledPrice(label="Пожертвование", amount=10000)]  # Сумма в копейках (10000 здесь это 100.00 RUB)
            payload = f"{command.args}"  # Необходима для контроля платежей, может быть любой строкой
            start_parameter = f"payment-{payload}"  # Уникальный параметр для генерации глубоких ссылок на инвойсы
            provider_data = None  # Поставщик данных платежных систем, можно использовать для передачи чека

            # Отправка инвойса
            await bot.send_invoice(
                chat_id,
                title=title,
                description=description,
                provider_token=provider_token,
                currency=currency,
                prices=prices,
                start_parameter=start_parameter,
                payload=payload,
                provider_data=provider_data
            )
    else:
        await message.reply(
            f'**Support** available! \nThis is just support for this little project for the sake of its life on the host.\nMore information about the projects can be found in [this group.]({group_link})',
            parse_mode='Markdown')
        async def send_invoice(chat_id):
            title = "Support project"
            description = "To extend this project, an amount of 100 rubles is sufficient - this is a whole month of continuous operation of the project on the host.\n\n!!IMPORTANT!!\nThis is only a donation, \"Support\" of the project, no reward and/or bonuses are given for this ."
            provider_token = "390540012:LIVE:44520"
            currency = "RUB"  # Код валюты ISO 4217
            prices = [
                LabeledPrice(label="Support", amount=10000)]  # Сумма в копейках (10000 здесь это 100.00 RUB)
            payload = f"{command.args}"  # Необходима для контроля платежей, может быть любой строкой
            start_parameter = f"payment-{payload}"  # Уникальный параметр для генерации глубоких ссылок на инвойсы
            provider_data = None  # Поставщик данных платежных систем, можно использовать для передачи чека

            # Отправка инвойса
            await bot.send_invoice(
                chat_id,
                title=title,
                description=description,
                provider_token=provider_token,
                currency=currency,
                prices=prices,
                start_parameter=start_parameter,
                payload=payload,
                provider_data=provider_data
            )
    chat_id = message.chat.id
    await send_invoice(chat_id)


@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(F.successful_payment)
async def successful_payment(message: types.Message):
    await auto_add_user(message)
    if 'ru' in str(message.from_user.language_code):
        await message.answer("Спасибо за Ваше пожертвование!\nОно очень ценно для меня, как для создателя проекта!")
    else:
        await message.answer("Thank you for your support!\nIt is very valuable to me as the creator of the project!")
    await bot.send_message(chat_id=1399051550, text=f"ЕБАТЬ! ЗАДОНИЛИ! {message.from_user.id} ЗАДОНИЛ НА***!")

@dp.message()
async def wth_is_bro(message: types.Message):
    try:
        if message.chat.type == 'private':
            await auto_add_user(message)
            if await datab.check_dead(message.from_user.id) != True:
                text = await write_to_gst(text=message.text, user_id=message.from_user.id)
                if random.randint(1, 3) == 1:
                    if text != False:
                        text = await generate_sentence(text=text)
                        await message.reply(text)
                    else:
                        await message.reply("...")
                else:
                    await message.reply("...")
        else:
            pass
    except:
        pass

async def life_tgochi():
    while True:
        print("life 5m")
        try:
            x = await datab.get_ids()
            for i in x:
                try:
                    user_id = i[0]
                    if await datab.check_dead(user_id) != True:
                        datab.live_time(user_id)
                        a = datab.check_stats(user_id)
                        dead = False
                        crit = False
                        for num in a:
                            if num <= 0:
                                dead = True
                            elif num <= 5:
                                crit = True
                            elif num >= 101:
                                dead = True
                        if dead == True:
                            await dead_inside(user_id)
                            await bot.send_message(chat_id=user_id, text='Твой TGochi мёртв. Его последние слова:\n\n' + random.choice(dead_list), parse_mode='Markdown')
                        elif crit == True:
                            if random.randint(0, 1) == 1:
                                await bot.send_message(chat_id=user_id, text=random.choice(crit_list),
                                                       parse_mode='Markdown')
                        else:
                            if random.randint(1, 9) == 1:
                                await bot.send_message(chat_id=user_id, text=random.choice(time_now_list),
                                                       parse_mode='Markdown')

                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
        await asyncio.sleep(300)
async def console_input():
    while True:
        console_message = await aioconsole.ainput("")
        if console_message == 'exit()':
            exit()

async def dead_inside(user_id):
    await dead_inside(user_id)
    file_path = f'data/{user_id}.txt'

    # Записываем обрезанное содержимое обратно в файл
    with open(file_path, 'w') as file:
        file.writelines("")

async def auto_add_user(message):
    user_status = await datab.check(message.from_user.id)
    if user_status == False:
        await datab.add(message.from_user.id)
        print(user_status)
    else:
        pass

async def main():
    await datab.sql_start()
    asyncio.ensure_future(console_input())
    asyncio.ensure_future(life_tgochi())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())