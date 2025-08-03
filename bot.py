# bot.py

import openai
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, MessageHandler, ContextTypes,
    CallbackQueryHandler, filters
)
from config import BOT_TOKEN, OPENAI_API_KEY, AUTHORIZED_USERS

openai.api_key = OPENAI_API_KEY

async def translate_with_gpt(text, to_lang="en"):
    direction = "sang tiếng Anh" if to_lang == "en" else "sang tiếng Việt"
    prompt = f"""
Bạn là một trợ lý hỗ trợ khách hàng chuyên nghiệp trong lĩnh vực Facebook Ads, chuyên giải quyết các vấn đề liên quan đến:
1. Setup tài khoản quảng cáo (BM, VIA, Pixel, Page, Proxy, Catalog…)
2. Xử lý lỗi không tiêu tiền, checkpoint, xác minh, camp lỗi, bị giới hạn, add thẻ...
3. Giao tiếp khách hàng qua tiếng {'Việt' if to_lang == 'en' else 'Anh'} – {'Anh' if to_lang == 'en' else 'Việt'} chuyên ngành Ads.

Hãy dịch câu sau {direction} một cách:
- Ngắn gọn
- Chuyên nghiệp
- Sát nghĩa và thân thiện
- Đúng với ngữ cảnh đại lý cung cấp tài khoản, BM, proxy chạy ads Facebook

Nội dung cần dịch:
\"{text}\"
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

# Gửi inline button khi khách nhắn
async def handle_incoming(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    if user_id not in AUTHORIZED_USERS:
        for admin_id in AUTHORIZED_USERS:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📘 Dịch sang tiếng Việt", callback_data=f"trans_{update.message.chat.id}_{update.message.message_id}_{user_id}")]
            ])
            await context.bot.send_message(chat_id=admin_id, text=f"📩 KH gửi: {text}", reply_markup=keyboard)

# Admin nhắn tiếng Việt → dịch sang tiếng Anh cho khách
async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in AUTHORIZED_USERS:
        text = update.message.text
        translated = await translate_with_gpt(text, "en")
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"{text}\n\n🇬🇧 {translated}")
        await update.message.delete()

# Admin bấm nút "Dịch" → gửi bản dịch riêng
async def handle_translate_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split("_")
    chat_id, msg_id, _ = int(data[1]), int(data[2]), int(data[3])
    msg = await context.bot.forward_message(chat_id=AUTHORIZED_USERS[0], from_chat_id=chat_id, message_id=msg_id)
    translated = await translate_with_gpt(msg.text, "vi")
    await context.bot.send_message(chat_id=query.from_user.id, text=f"📘 Dịch: {translated}")
    await query.answer("Đã dịch!")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_incoming))
app.add_handler(MessageHandler(filters.TEXT & filters.User(AUTHORIZED_USERS), handle_admin_reply))
app.add_handler(CallbackQueryHandler(handle_translate_button, pattern="^trans_"))

app.run_polling()
