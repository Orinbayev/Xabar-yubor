from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
import logging
from tokken import BOT_TOKEN
# Loglarni sozlash
logging.basicConfig(level=logging.INFO)


DEFAULT_ADMIN_ID = 6678521239  # Dastlabki adminning Telegram ID sini kiriting

# Adminlar ro'yxatini va kanallar ro'yxatini saqlash
ADMIN_IDS = {DEFAULT_ADMIN_ID}  # Dastlabki adminni qo'shish
CHANNEL_IDS = set()  # Kanal IDlari to'plami

# Bot va Dispatcher obyektlarini yaratamiz
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Tasdiqlash klaviaturasini yaratish
def get_confirmation_keyboard(message_id):
    keyboard = InlineKeyboardMarkup()
    yes_button = InlineKeyboardButton("Ha", callback_data=f"confirm_{message_id}")
    no_button = InlineKeyboardButton("Yo'q", callback_data=f"cancel_{message_id}")
    keyboard.add(yes_button, no_button)
    return keyboard

# /start komandasini qayta ishlash
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply('Assalomu aleykum! Men sizning xabaringizni meni admin qilgan. Kanallarga yuborib beraman.')


# Adminlarni boshqarish komandalar
@dp.message_handler(commands=['add_admin'])
async def add_admin(message: types.Message):
    if message.from_user.id != DEFAULT_ADMIN_ID:
        await message.reply("Sizda admin huquqlari yo'q.")
        return
    
    # Admin ID'sini qo'shish
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Iltimos, admin ID'sini kiriting. Masalan: /add_admin 123456789")
        return
    
    admin_id = int(args[1].strip())
    if admin_id not in ADMIN_IDS:
        ADMIN_IDS.add(admin_id)
        await message.reply(f"Adminlar ro'yxatiga {admin_id} qo'shildi.")
    else:
        await message.reply(f"{admin_id} allaqachon adminlar ro'yxatida mavjud.")

@dp.message_handler(commands=['remove_admin'])
async def remove_admin(message: types.Message):
    if message.from_user.id != DEFAULT_ADMIN_ID:
        await message.reply("Sizda admin huquqlari yo'q.")
        return
    
    # Admin ID'sini o'chirish
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Iltimos, admin ID'sini kiriting. Masalan: /remove_admin 123456789")
        return
    
    admin_id = int(args[1].strip())
    if admin_id in ADMIN_IDS:
        ADMIN_IDS.discard(admin_id)
        await message.reply(f"Adminlar ro'yxatidan {admin_id} o'chirildi.")
    else:
        await message.reply(f"Adminlar ro'yxatida {admin_id} topilmadi.")

@dp.message_handler(commands=['list_admins'])
async def list_admins(message: types.Message):
    if message.from_user.id != DEFAULT_ADMIN_ID:
        await message.reply("Sizda admin huquqlari yo'q.")
        return
    if ADMIN_IDS:
        admins_list = "\n".join(map(str, ADMIN_IDS))
        await message.reply(f"Adminlar ro'yxati:\n{admins_list}")
    else:
        await message.reply("Adminlar ro'yxati bo'sh.")

# Kanal ID olish komandasini qayta ishlash
@dp.message_handler(commands=['get_channel_id'])
async def get_channel_id(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("Sizda admin huquqlari yo'q.")
        return
    
    chat_id = message.chat.id
    await message.reply(f"Sizning kanal ID: {chat_id}")

# Admin komandalar
@dp.message_handler(commands=['add_channel'])
async def add_channel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("Sizda admin huquqlari yo'q.")
        return
    
    # Kanal ID'sini qo'shish
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Iltimos, kanal ID'sini kiriting. Masalan: /add_channel -1001234567890")
        return
    
    channel_id = args[1].strip()
    if not channel_id.startswith('-100'):
        await message.reply("Kanal ID xato. Iltimos, to'g'ri kanal ID'sini kiriting (masalan, -1001234567890).")
        return
    
    CHANNEL_IDS.add(channel_id)
    await message.reply(f"Kanallar ro'yxatiga {channel_id} qo'shildi.")

@dp.message_handler(commands=['remove_channel'])
async def remove_channel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("Sizda admin huquqlari yo'q.")
        return

    # Kanal ID'sini o'chirish
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Iltimos, kanal ID'sini kiriting. Masalan: /remove_channel -1001234567890")
        return
    
    channel_id = args[1].strip()
    if channel_id in CHANNEL_IDS:
        CHANNEL_IDS.discard(channel_id)
        await message.reply(f"Kanallar ro'yxatidan {channel_id} o'chirildi.")
    else:
        await message.reply(f"Kanallar ro'yxatida {channel_id} topilmadi.")

@dp.message_handler(commands=['list_channels'])
async def list_channels(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("Sizda admin huquqlari yo'q.")
        return
    if CHANNEL_IDS:
        channels_list = "\n".join(CHANNEL_IDS)
        await message.reply(f"Kanallar ro'yxati:\n{channels_list}")
    else:
        await message.reply("Kanallar ro'yxati bo'sh.")

# Xabar va media fayllarni qabul qilish va tasdiqlash so'rash
waiting_for_confirmation = {}  # Xabarlarni tasdiqlash uchun saqlash

@dp.message_handler(content_types=types.ContentType.ANY)
async def handle_message(message: types.Message):
    # Xabarni tasdiqlash uchun saqlaymiz
    waiting_for_confirmation[message.message_id] = {
        'type': message.content_type,
        'data': message
    }
    # Tasdiqlash so'rovini yuboramiz
    confirmation_keyboard = get_confirmation_keyboard(message.message_id)
    await message.reply('Ushbu xabarni kanallarga yuborishni tasdiqlaysizmi?', reply_markup=confirmation_keyboard)

# Callback so'rovlarini qayta ishlash
@dp.callback_query_handler(lambda c: c.data.startswith('confirm_') or c.data.startswith('cancel_'))
async def process_callback_query(callback_query: types.CallbackQuery):
    action, message_id = callback_query.data.split('_', 1)
    message_id = int(message_id)
    
    if action == 'confirm':
        message_data = waiting_for_confirmation.pop(message_id, None)
        if message_data:
            message_type = message_data['type']
            message = message_data['data']
            for channel_id in CHANNEL_IDS:
                try:
                    if message_type == 'text':
                        await bot.send_message(chat_id=channel_id, text=message.text)
                    elif message_type == 'photo':
                        await bot.send_photo(chat_id=channel_id, photo=message.photo[-1].file_id, caption=message.caption)
                    elif message_type == 'video':
                        await bot.send_video(chat_id=channel_id, video=message.video.file_id, caption=message.caption)
                    elif message_type == 'audio':
                        await bot.send_audio(chat_id=channel_id, audio=message.audio.file_id, caption=message.caption)
                    elif message_type == 'document':
                        await bot.send_document(chat_id=channel_id, document=message.document.file_id, caption=message.caption)
                    else:
                        await bot.send_message(chat_id=channel_id, text="Qayta ishlanmagan kontent turi.")
                except Exception as e:
                    logging.error(f"{channel_id} kanaliga yuborishda xato yuz berdi: {e}")
            await bot.answer_callback_query(callback_query.id, text="Xabar kanallarga yuborildi.")
        else:
            await bot.answer_callback_query(callback_query.id, text="Xabar topilmadi.")
    elif action == 'cancel':
        waiting_for_confirmation.pop(message_id, None)
        await bot.answer_callback_query(callback_query.id, text="Xabar yuborilmasdan bekor qilindi.")
    

    # Tasdiqlash xabarini o'chirish
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

# Pollingni boshlash
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

