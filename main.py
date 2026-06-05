import asyncio
import os
import random

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ChatPermissions
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# хранение капчи в памяти
captcha = {}

# ---------------- CAPTCHA ----------------
def make_captcha(user_id):
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    result = a + b
    captcha[user_id] = result

    kb = InlineKeyboardBuilder()
    options = [result, result+1, result-1]
    random.shuffle(options)

    for opt in options:
        kb.button(text=str(opt), callback_data=f"cap:{user_id}:{opt}")

    kb.adjust(3)
    return kb.as_markup(), f"🤖 Реши: {a} + {b} = ?"

# ---------------- NEW USER ----------------
@dp.message(F.new_chat_members)
async def new_user(message: Message):
    for user in message.new_chat_members:

        await bot.restrict_chat_member(
            message.chat.id,
            user.id,
            permissions=ChatPermissions(can_send_messages=False)
        )

        kb, text = make_captcha(user.id)

        await message.answer(
            f"👋 Привет {user.full_name}\n\n{text}",
            reply_markup=kb
        )

# ---------------- CHECK CAPTCHA ----------------
@dp.callback_query(F.data.startswith("cap:"))
async def check(call: CallbackQuery):
    _, uid, answer = call.data.split(":")
    uid = int(uid)
    answer = int(answer)

    if call.from_user.id != uid:
        return await call.answer("Это не твоя капча", show_alert=True)

    if captcha.get(uid) != answer:
        return await call.answer("❌ Неверно", show_alert=True)

    await bot.restrict_chat_member(
        call.message.chat.id,
        uid,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True
        )
    )

    await call.message.edit_text("✅ Доступ открыт!")

# ---------------- START ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())