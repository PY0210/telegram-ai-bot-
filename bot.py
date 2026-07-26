import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

user_history = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 你好，我是 AI 助手，有什么可以帮助你？")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_history:
        user_history[user_id] = [
            {
                "role": "system",
                "content": "你是一位聪明、友好、幽默的AI助手。"
            }
        ]

    user_history[user_id].append(
        {
            "role": "user",
            "content": text
        }
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=user_history[user_id]
    )

    answer = response.choices[0].message.content

    user_history[user_id].append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    if len(user_history[user_id]) > 20:
        user_history[user_id] = (
            user_history[user_id][:1]
            + user_history[user_id][-19:]
        )

    await update.message.reply_text(answer)

def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
    )

    print("Bot Running...")
    app.run_polling()

if name == "__main__":
    main()
