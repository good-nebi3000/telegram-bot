import asyncio
import datetime
from gc import callbacks

from aiogram import Router,Bot, Dispatcher,F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart, Command

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import sqlite3

def init_database():
    conn = sqlite3.connect('avia_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            name TEXT,
            date TEXT,
            time TEXT
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


database = {}

BOT_TOKEN = '8407223370:AAFQh9_Z5nTNwCfkXh9j3gjwUTl667ZZxVs'
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
class SELECT(StatesGroup):
    for_name = State()
    for_data = State()
    for_time = State()
    for_count = State()
    for_country = State()


@dp.message(Command('start'))
async def start1(message:Message,state: FSMContext):
    await state.set_state(SELECT.for_name)
    await message.answer('Введите фио')



@dp.message(SELECT.for_name)
async def start(message:Message,state: FSMContext):
    if len(message.text.split()) != 3:
        await message.answer('Вводите только fio!')
        return

    await state.update_data(name=message.text)
    data = await state.get_data()
    print(data)
    await state.set_state(SELECT.for_data)
    await message.answer('Укажите дату бронирования')

@dp.message(SELECT.for_data)
async def start2(message:Message,state: FSMContext):
    date = message.text.split('/')
    if len(date) == 3:
        validate = [num.isdigit() for num in date]
        if False in validate:
            await message.answer('❌ Некорректные данные')
            return
    else:
        await message.answer('❌ Некорректные данные\n\nПример: 10/05/2025')
        return

    await state.update_data(date=message.text)
    data = await state.get_data()
    print(data)
    await state.set_state(SELECT.for_time)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="08:00", callback_data="time_08:00"),
             InlineKeyboardButton(text="08:30", callback_data="time_08:30")],
            [InlineKeyboardButton(text="14:00", callback_data="time_14:00"),
             InlineKeyboardButton(text="14:30", callback_data="time_14:30")],
        ]
    )

    await message.answer("Выберите время рейса:", reply_markup=keyboard)



@dp.callback_query(StateFilter(SELECT.for_time),F.data.in_(["time_08:00","time_08:30","time_14:00","time_14:30"]))
async def start3(callback:CallbackQuery,state: FSMContext):
    await state.update_data(time=callback.data)
    data = await state.get_data()
    print(data)
    if callback.data:
       await callback.message.answer(f'вы выбрали время:{callback.data}')
    await state.set_state(SELECT.for_count)
    await callback.message.answer('введите Кол-во билетов')

@dp.message(SELECT.for_count)
async def start2(message:Message,state: FSMContext):
    num = message.text
    if num != 0:
        await message.answer('вы успешно зареганы')
    data = await state.get_data()

    conn = sqlite3.connect('avia_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
                INSERT INTO bookings (user_id, username, name, date, time)
                VALUES (?, ?, ?, ?, ?)
            ''', (
        data['user_id'],
        data['username'],
        data['name'],
        data['date'],
        data['time'],

    ))
    conn.commit()
    booking_id = cursor.lastrowid
    conn.close()



async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
