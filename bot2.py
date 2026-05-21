import asyncio
import time
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8853939811:AAFNwFlKK3kYRs82IR48Mi7aQ5jIEbom9Hw"
ADMIN_ID = 1365397494

CRYPTO_WALLET = "TKAxF8bdq1svp2y5C2VE1f1FyVYMZsUvQv"
NETWORK = "TRON (TRC20)"
PRICE = "49.99$"
DAYS = 30

bot = Bot(token=TOKEN)
dp = Dispatcher()

conn = sqlite3.connect("users.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    expires INTEGER
)
""")
conn.commit()


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Купить доступ", callback_data="buy")],
        [InlineKeyboardButton(text="📌 Проверить статус", callback_data="status")]
    ])


def pay_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid")]
    ])


@dp.message()
async def start(message: types.Message):
    await message.answer(
        "👋 VIP бот\n\n"
        f"💰 Цена: {PRICE}\n"
        f"⏳ Доступ: {DAYS} дней\n\n"
        "Нажмите кнопку ниже:",
        reply_markup=main_menu()
    )


@dp.callback_query(F.data == "buy")
async def buy(call: types.CallbackQuery):
    await call.message.answer(
        f"💳 Оплата\n\n"
        f"Сеть: {NETWORK}\n"
        f"Кошелёк:\n{CRYPTO_WALLET}\n\n"
        f"Сумма: {PRICE}\n\n"
        "После оплаты нажмите кнопку:",
        reply_markup=pay_menu()
    )


@dp.callback_query(F.data == "paid")
async def paid(call: types.CallbackQuery):
    await bot.send_message(
        ADMIN_ID,
        f"🧾 Новая заявка\nUser: {call.from_user.id}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="✅ Approve",
                callback_data=f"approve:{call.from_user.id}"
            )]
        ])
    )

    await call.message.answer("⏳ Заявка отправлена админу")


@dp.callback_query(F.data.startswith("approve:"))
async def approve(call: types.CallbackQuery):
    user_id = int(call.data.split(":")[1])
    expires = int(time.time()) + DAYS * 86400

    cur.execute("REPLACE INTO users VALUES (?, ?)", (user_id, expires))
    conn.commit()

    invite_link = "https://t.me/+cRJemA0vh8A5YjIy"

    await bot.send_message(
        user_id,
        f"✅ Доступ выдан!\n\nВот ссылка на канал:\n{invite_link}\n\n⏳ Доступ на {DAYS} дней"
    )

    await call.message.answer("Подтверждено")


@dp.callback_query(F.data == "status")
async def status(call: types.CallbackQuery):
    cur.execute("SELECT expires FROM users WHERE user_id=?", (call.from_user.id,))
    row = cur.fetchone()

    if not row:
        await call.message.answer("❌ У вас нет доступа")
        return

    if row[0] > int(time.time()):
        await call.message.answer("✅ Доступ активен")
    else:
        await call.message.answer("❌ Доступ истёк")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
