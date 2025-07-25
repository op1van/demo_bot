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
