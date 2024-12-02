import asyncio

from BADMUSIC import app
from pyrogram import filters
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

@app.on_message(filters.command(["repo"]))
async def start(client: Client, message: Message):
    await message.reply_video(
        video=f"https://envs.sh/Ygb.mp4",
        caption=f"❤️ ʜᴇʏ {message.from_user.mention}",
        reply_markup=InlineKeyboardMarkup(
            [
               [
            InlineKeyboardButton(
                text="☆ ᴏᴡɴᴇʀ 💗 ", url=f"https://t.me/ll_ITZ_NAWAB_HERE_ll"
            ),
            InlineKeyboardButton(
                text="☆ ɢʀᴏᴜᴘ 💗", url=f"https://t.me/SIDHI_SUPPORT"
            ),
        ],
          [
            InlineKeyboardButton(
                text="☆ ᴄʜᴀɴɴᴇʟ 💗 ", url=f"https://t.me/TG_BIO_STYLE"
            ),
            InlineKeyboardButton(
                text="☆ ʀᴇᴘᴏ 💗", url=f"https://t.me/SIDHI_MUSIC/20"
            ),
        ],
                [
                    InlineKeyboardButton(
                        "✯ ᴄʟᴏsᴇ ✯", callback_data="close"
                    )
                ],
            ]
        )
    )
  
