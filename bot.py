import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes
)
from notion_client import Client as NotionClient

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if not TELEGRAM_TOKEN:
    raise RuntimeError("BOT_TOKEN env var is missing")
if not (NOTION_TOKEN and DATABASE_ID):
    raise RuntimeError("Notion env vars are missing")

notion = NotionClient(auth=NOTION_TOKEN)

user_state = {}
artist_data = {}

QUESTIONS = [
    {"key": "Name", "question": "🧏🏿\n\nYour artist name"},
    {"key": "Country", "question": "🌏\n\nCountry"},
    {"key": "About", "question": "✍️\n\nJust a few words about you + info about upcoming releases, projects and plans"},
    {"key": "Demo", "question": "Any fresh demos to share?\nOnly soundcloud link, please"},
    {"key": "Networks", "question": "👀\n\nSocial networks - ig, yt, bandcamp, tiktok"},
    {"key": "E-mail", "question": "📝\n\nArtist e-mail"},
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Hey there, meet cllb — the music community label that kinda accidentally started itself but stuck around on purpose 🧢 So, are you here to send us smth unpolished, right?"
    )
    keyboard = [[InlineKeyboardButton("definitely", callback_data="consent")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.from_user.id

    if data == "consent":
        consent_text = (
            'Consent *\n\n'
            'By submitting this "form" you consent to the collection and processing of your personal data, which may be transferred and stored outside your country of residence.\n\n'
            'You can withdraw your consent at any time by letting @MilaIgnatevaa know.\n\n'
            '<a href="https://drive.google.com/file/d/1euqwTrqdoG2-9ySB9JivXdTT3Tb_R5sG/view">Privacy and Cookie Policy</a>'
        )
        await query.message.reply_text(consent_text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("i have read and agree", callback_data="artist_name")]
            ])
        )
    elif data == "artist_name":
        user_state[chat_id] = 0  # question index
        artist_data[chat_id] = {}
        await query.message.reply_text(QUESTIONS[0]["question"])
    elif data == "hope_so":
        await query.message.reply_text(
            "🤜🏼 🤛🏿",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("subscribe, your collaba", url="https://linktr.ee/cllllllllllllb")]
            ])
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    text = update.message.text.strip()
    telegram_username = f"@{update.effective_user.username}" if update.effective_user.username else ""
    state = user_state.get(chat_id)

    if isinstance(state, int) and 0 <= state < len(QUESTIONS):
        key = QUESTIONS[state]["key"]
        artist_data.setdefault(chat_id, {})
        artist_data[chat_id][key] = text

        if state == 0:
            artist_data[chat_id]["Telegram"] = telegram_username

        if state + 1 < len(QUESTIONS):
            user_state[chat_id] += 1
            await update.message.reply_text(QUESTIONS[state + 1]["question"])
        else:
            # Save to Notion
            try:
                notion.pages.create(
                    parent={"database_id": DATABASE_ID},
                    properties={
                        "Name": {"title": [{"text": {"content": artist_data[chat_id].get("Name", "")}}]},
                        "Telegram": {"rich_text": [{"text": {"content": artist_data[chat_id].get("Telegram", telegram_username)}}]},
                        "Country": {"rich_text": [{"text": {"content": artist_data[chat_id].get("Country", "")}}]},
                        "About": {"rich_text": [{"text": {"content": artist_data[chat_id].get("About", "")}}]},
                        "Demo": {"rich_text": [{"text": {"content": artist_data[chat_id].get("Demo", "")}}]},
                        "Networks": {"rich_text": [{"text": {"content": artist_data[chat_id].get("Networks", "")}}]},
                        "E-mail": {"rich_text": [{"text": {"content": artist_data[chat_id].get("E-mail", "")}}]},
                    }
                )
            except Exception as e:
                await update.message.reply_text(f"Не удалось записать в Notion: {e}")

            user_state[chat_id] = "final"
            await update.message.reply_text(
                "Good job, man 💅🏽 Promise to text you back if collaba A&R add your track to the shortlist",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("hope so", callback_data="hope_so")]
                ])
            )

def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
