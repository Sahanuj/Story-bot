from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, CallbackContext
# Conversation states
NAME, PART, AUTHOR, IMAGE, STORY, NOTE = range(6)

# Admin Channel ID (replace with your channel's chat ID)
ADMIN_CHANNEL_ID = -1001234567890  # Replace with your Admin Channel ID

# To store user data
user_data = {}

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("කතාවේ නම :-")
    return NAME

def get_name(update: Update, context: CallbackContext) -> int:
    user_data["name"] = update.message.text
    update.message.reply_text("කොටස :-")
    return PART

def get_part(update: Update, context: CallbackContext) -> int:
    user_data["part"] = update.message.text
    update.message.reply_text("රචකයාගේ නම(ඇත්ත නම වෙන්න ඕන නෑ. කතා ලියන්න බලාපොරොත්තු වන නම) :-")
    return AUTHOR

def get_author(update: Update, context: CallbackContext) -> int:
    user_data["author"] = update.message.text
    update.message.reply_text("කතාවට යොදන්න අවශ්‍ය චායාරූප:")
    return IMAGE

def get_image(update: Update, context: CallbackContext) -> int:
    if update.message.photo:
        user_data["image"] = update.message.photo[-1].file_id
    else:
        user_data["image"] = None
    update.message.reply_text("කතාව (text only):-")
    return STORY

def get_story(update: Update, context: CallbackContext) -> int:
    user_data["story"] = update.message.text
    if not user_data.get("name") or not user_data.get("part") or not user_data.get("story"):
        update.message.reply_text("Please include the name of the story, the part, and the story itself!")
        return ConversationHandler.END
    
    update.message.reply_text("විශේෂ පණිවිඩ(අනිවාර්‍ය නොවේ):-")
    return NOTE

def get_note(update: Update, context: CallbackContext) -> int:
    user_data["note"] = update.message.text if update.message.text else None

    # Forwarding to Admin Channel
    caption = (f"කතාවේ නම: {user_data['name']}\n"
               f"කොටස: {user_data['part']}\n"
               f"රචකයාගේ නම: {user_data['author']}\n"
               f"කතාව:\n{user_data['story']}\n")
    if user_data["note"]:
        caption += f"විශේෂ පණිවිඩ: {user_data['note']}\n"
    
    keyboard = [
        [
            InlineKeyboardButton("Approve", callback_data="approve"),
            InlineKeyboardButton("Reject", callback_data="reject"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if user_data["image"]:
        context.bot.send_photo(
            chat_id=ADMIN_CHANNEL_ID,
            photo=user_data["image"],
            caption=caption,
            reply_markup=reply_markup
        )
    else:
        context.bot.send_message(
            chat_id=ADMIN_CHANNEL_ID,
            text=caption,
            reply_markup=reply_markup
        )
    update.message.reply_text("Your story has been submitted for review.")
    return ConversationHandler.END

def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == "approve":
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Your story was Approved!"
        )
    elif query.data == "reject":
        query.message.reply_text("Add a comment for rejection:")
        context.user_data["reject_msg"] = query.message
        return

def handle_reject_comment(update: Update, context: CallbackContext) -> None:
  
    reject_msg = context.user_data.get("reject_msg")
    if reject_msg:
        comment = update.message.text
        user_id = reject_msg.chat.id  # Get the user ID from the original message
        context.bot.send_message(
            chat_id=user_id,
            text=f"Your story was rejected. Reason: {comment}"
        )
        reject_msg.edit_text(reject_msg.text + f"\n\nRejected. Reason: {comment}")
        del context.user_data["reject_msg"]

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Submission process has been canceled.")
    return ConversationHandler.END

def main() -> None:
    torgan = Application("YOUR_BOT_TOKEN")  # Replace with your bot token


    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.Text & ~filters.command, get_name)],
            PART: [MessageHandler(filters.Text & ~filters.command, get_part)],
            AUTHOR: [MessageHandler(filters.Text & ~filters.command, get_author)],
            IMAGE: [MessageHandler(filters.photo | filters.Text & ~filters.command, get_image)],
            STORY: [MessageHandler(filters.Text & ~filters.command, get_story)],
            NOTE: [MessageHandler(filters.Text & ~filters.command, get_note)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    torgan.add_handler(conv_handler)
    torgan.add_handler(CallbackQueryHandler(button_handler))
    torgan.add_handler(MessageHandler(filters.Text & ~filters.command, handle_reject_comment))

    torgan.run_polling()
    torgan.idle()

if __name__ == "__main__":
    main()
