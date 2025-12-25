import asyncio
import re
from datetime import datetime
from aiogram import Router, Bot, F
from aiogram.enums import ChatAction, ParseMode, ChatType
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from telegramify_markdown import markdownify
from telegramify_markdown.customize import get_runtime_config

from bot.api.deepseek import call_deepseek_api
from bot.api.currency import get_currency_rates
from bot.api.joke import get_random_joke

markdown_symbol = get_runtime_config().markdown_symbol
markdown_symbol.head_level_1 = ""
markdown_symbol.head_level_2 = ""
markdown_symbol.head_level_3 = ""

router = Router()

def escape_markdown(text: str) -> str:
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def get_main_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💱 Курс валют", callback_data="currency"),
            InlineKeyboardButton(text="😄 Случайная шутка", callback_data="joke")
        ],
        [
            InlineKeyboardButton(text="🕐 Текущее время", callback_data="time")
        ]
    ])
    return keyboard


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    keyboard = get_main_keyboard()
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}! Добро пожаловать в Deepseek bot.\n"
        f"Задавай вопросы, и я с радостью на них отвечу!\n\n"
        f"Также доступны дополнительные функции:",
        reply_markup=keyboard
    )

@router.message(
    (F.chat.type == ChatType.PRIVATE)
    | F.text.contains("DeepSeek")
    | (F.reply_to_message & F.reply_to_message.from_user)
)
async def handle_deepseek(message: Message, bot: Bot):
    chat_id = message.chat.id
    text = message.text.strip()

    async def show_typing():
        while True:
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await asyncio.sleep(4)

    typing_task = asyncio.create_task(show_typing())
    try:
        reply = await call_deepseek_api(text)
    except Exception as e:
        escaped_error = escape_markdown(str(e))
        await message.reply(f"Ошибка при обращении к DeepSeek: {escaped_error}")
        return
    finally:
        typing_task.cancel()

    tg_md = markdownify(reply, max_line_length=None, normalize_whitespace=False)
    await message.reply(tg_md, parse_mode=ParseMode.MARKDOWN_V2)


@router.callback_query(F.data == "currency")
async def handle_currency_callback(callback: CallbackQuery) -> None:
    await callback.answer("Получаю курс валют...")
    result = await get_currency_rates()
    keyboard = get_main_keyboard()
    await callback.message.edit_text(result, reply_markup=keyboard)


@router.callback_query(F.data == "joke")
async def handle_joke_callback(callback: CallbackQuery) -> None:
    await callback.answer("Получаю шутку...")
    result = await get_random_joke()
    keyboard = get_main_keyboard()
    await callback.message.edit_text(result, reply_markup=keyboard)


@router.callback_query(F.data == "time")
async def handle_time_callback(callback: CallbackQuery) -> None:
    now = datetime.now()
    
    # Форматируем время для разных часовых поясов
    moscow_time = now.strftime("%H:%M:%S")
    date = now.strftime("%d.%m.%Y")
    weekday = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"][now.weekday()]
    
    result = f"🕐 Текущее время (Москва):\n\n"
    result += f"📅 Дата: {date}\n"
    result += f"⏰ Время: {moscow_time}\n"
    result += f"📆 День недели: {weekday}\n"
    
    keyboard = get_main_keyboard()
    await callback.answer()
    await callback.message.edit_text(result, reply_markup=keyboard)