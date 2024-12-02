import random
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from deep_translator import GoogleTranslator 
from config import MONGO_DB_URI as MONGO_URL
from pymongo import MongoClient
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup

WORD_MONGO_URL = "mongodb+srv://BADMUNDA:BADMYDAD@badhacker.i5nw9na.mongodb.net/"
translator = GoogleTranslator()  
chatdb = MongoClient(MONGO_URL)
worddb = MongoClient(WORD_MONGO_URL)
status_db = chatdb["ChatBotStatusDb"]["StatusCollection"]
chatai = worddb["Word"]["WordDb"]
lang_db = chatdb["ChatLangDb"]["LangCollection"]


CHATBOT_ON = [
    [
        InlineKeyboardButton(text="Enable", callback_data="enable_chatbot"),
        InlineKeyboardButton(text="Disable", callback_data="disable_chatbot"),
    ],
]

def generate_language_buttons(languages):
    buttons = []
    current_row = []
    for lang, code in languages.items():
        current_row.append(InlineKeyboardButton(lang.capitalize(), callback_data=f'setlang_{code}'))
        if len(current_row) == 4:  
            buttons.append(current_row)
            current_row = []  
    if current_row:  
        buttons.append(current_row)
    return InlineKeyboardMarkup(buttons)

def get_chat_language(chat_id):
    chat_lang = lang_db.find_one({"chat_id": chat_id})
    return chat_lang["language"] if chat_lang and "language" in chat_lang else None

 
# Enable/Disable Command
@Client.on_message(filters.command("chatbot"))
async def manage_chatbot(client: Client, message: Message):
    chat_id = message.chat.id
    args = message.text.split()

    if len(args) > 1 and args[1].lower() in ["on", "off"]:
        if args[1].lower() == "on":
            status_db.update_one({"chat_id": chat_id}, {"$set": {"status": "enabled"}}, upsert=True)
            await message.reply_text("Chatbot has been **enabled** for this chat.")
        elif args[1].lower() == "off":
            status_db.update_one({"chat_id": chat_id}, {"$set": {"status": "disabled"}}, upsert=True)
            await message.reply_text("Chatbot has been **disabled** for this chat.")
    else:
        await message.reply_text(
            "Choose an option to enable/disable chatbot.",
            reply_markup=InlineKeyboardMarkup(CHATBOT_ON),
        )
    
@Client.on_message((filters.text | filters.sticker | filters.photo | filters.video | filters.audio))
async def chatbot_response(client: Client, message: Message):
    chat_status = status_db.find_one({"chat_id": message.chat.id})
    if chat_status and chat_status.get("status") == "disabled":
        return

    if message.text:
        if any(message.text.startswith(prefix) for prefix in ["!", "/", ".", "?", "@", "#"]):
            return

    if (message.reply_to_message and message.reply_to_message.from_user.id == client.me.id):
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)

        reply_data = await get_reply(message.text if message.text else "")
        
        if reply_data:
            response_text = reply_data["text"]
            chat_lang = get_chat_language(message.chat.id)

            
            if not chat_lang or chat_lang == "en":
                translated_text = response_text  
            else:
                translated_text = GoogleTranslator(source='auto', target=chat_lang).translate(response_text)
            if reply_data["check"] == "sticker":
                await message.reply_sticker(reply_data["text"])
            elif reply_data["check"] == "photo":
                await message.reply_photo(reply_data["text"])
            elif reply_data["check"] == "video":
                await message.reply_video(reply_data["text"])
            elif reply_data["check"] == "audio":
                await message.reply_audio(reply_data["text"])
            else:
                await message.reply_text(translated_text)
        else:
            await message.reply_text("**what??**")

    if message.reply_to_message:
        await save_reply(message.reply_to_message, message)

async def save_reply(original_message: Message, reply_message: Message):
    if reply_message.sticker:
        is_chat = chatai.find_one(
            {
                "word": original_message.text,
                "text": reply_message.sticker.file_id,
                "check": "sticker",
            }
        )
        if not is_chat:
            chatai.insert_one(
                {
                    "word": original_message.text,
                    "text": reply_message.sticker.file_id,
                    "check": "sticker",
                }
            )
    elif reply_message.photo:
        is_chat = chatai.find_one(
            {
                "word": original_message.text,
                "text": reply_message.photo.file_id,
                "check": "photo",
            }
        )
        if not is_chat:
            chatai.insert_one(
                {
                    "word": original_message.text,
                    "text": reply_message.photo.file_id,
                    "check": "photo",
                }
            )
    elif reply_message.video:
        is_chat = chatai.find_one(
            {
                "word": original_message.text,
                "text": reply_message.video.file_id,
                "check": "video",
            }
        )
        if not is_chat:
            chatai.insert_one(
                {
                    "word": original_message.text,
                    "text": reply_message.video.file_id,
                    "check": "video",
                }
            )
    elif reply_message.audio:
        is_chat = chatai.find_one(
            {
                "word": original_message.text,
                "text": reply_message.audio.file_id,
                "check": "audio",
            }
        )
        if not is_chat:
            chatai.insert_one(
                {
                    "word": original_message.text,
                    "text": reply_message.audio.file_id,
                    "check": "audio",
                }
            )
    elif reply_message.text:
        is_chat = chatai.find_one(
            {"word": original_message.text, "text": reply_message.text}
        )
        if not is_chat:
            chatai.insert_one(
                {
                    "word": original_message.text,
                    "text": reply_message.text,
                    "check": "none",
                }
            )

async def get_reply(word: str):
    is_chat = list(chatai.find({"word": word}))
    if not is_chat:
        is_chat = list(chatai.find())
    if is_chat:
        random_reply = random.choice(is_chat)
        return random_reply
    return None

@Client.on_callback_query(filters.regex("enable_chatbot|disable_chatbot"))
async def toggle_chatbot(client: Client, callback_query):
    chat_id = callback_query.message.chat.id
    action = "enabled" if callback_query.data == "enable_chatbot" else "disabled"
    status_db.update_one({"chat_id": chat_id}, {"$set": {"status": action}}, upsert=True)

    await callback_query.answer(f"Chatbot {action} successfully!", show_alert=True)
    await callback_query.message.edit_text(
        f"Chatbot has been **{action}** for this chat."
    )
