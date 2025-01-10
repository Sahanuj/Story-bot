from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Replace with your bot token and admin channel ID
BOT_TOKEN = "7501736452:AAFvT-wcT5pk1yIc2EfTLeYiQDZGCxxS46A"
ADMIN_CHANNEL_ID = "-1002440310761"

# States for the ConversationHandler
(NAME, PART, AUTHOR, PHOTO, STORY, MESSAGE) = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the bot and ask for the story name."""
    await update.message.reply_text("කතාවේ නම: -")
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the name of the story."""
    context.user_data["name"] = update.message.text
    await update.message.reply_text("කොටස: -")
    return PART


async def get_part(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the part of the story."""
    context.user_data["part"] = update.message.text
    await update.message.reply_text("රචකයාගේ නම (ඇත්ත නම වෙන්න ඕන නෑ. කතා ලියන්න බලාපොරොත්තු වන නම): -")
    return AUTHOR


async def get_author(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the author's name."""
    context.user_data["author"] = update.message.text
    await update.message.reply_text("කතාවට යොදන්න අවශ්‍ය චායාරූප: -")
    return PHOTO


async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the photo for the story."""
    if update.message.photo:
        context.user_data["photo"] = update.message.photo[-1].file_id
    else:
        context.user_data["photo"] = None
    await update.message.reply_text("කතාව (text only): -")
    return STORY


async def get_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the story text."""
    context.user_data["story"] = update.message.text
    await update.message.reply_text("විශේෂ පණිවිඩ (අනිවාර්‍ය නොවේ): -")
    return MESSAGE


async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the optional message."""
    context.user_data["message"] = update.message.text if update.message.text else "No special message provided."

    # Validate required fields
    if not (context.user_data["name"] and context.user_data["part"] and context.user_data["story"]):
        await update.message.reply_text("Please provide all required fields: කතාවේ නම, කොටස, and කතාව.")
        return ConversationHandler.END

    # Forward data to Admin Channel
    keyboard = [
        [
            InlineKeyboardButton("Approve", callback_data="approve"),
            InlineKeyboardButton("Reject", callback_data="reject"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = (
        f"කතාවේ නම: {context.user_data['name']}\n"
        f"කොටස: {context.user_data['part']}\n"
        f"රචකයාගේ නම: {context.user_data['author']}\n"
        f"කතාව: {context.user_data['story']}\n"
        f"විශේෂ පණිවිඩ: {context.user_data['message']}"
    )

    if context.user_data["photo"]:
        await context.bot.send_photo(
            chat_id=ADMIN_CHANNEL_ID,
            photo=context.user_data["photo"],
            caption=caption,
            reply_markup=reply_markup,
        )
    else:
        await context.bot.send_message(
            chat_id=ADMIN_CHANNEL_ID,
            text=caption,
            reply_markup=reply_markup,
        )

    await update.message.reply_text("Your story has been submitted for review.")
    return ConversationHandler.END


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Admin's button clicks."""
    query = update.callback_query
    await query.answer()

    if query.data == "approve":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("The story was approved.")
        # Notify the user (implement user notification if needed)
    elif query.data == "reject":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("Please provide a reason for rejection:")
        context.user_data["rejection_query"] = query
        return MESSAGE


async def rejection_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle rejection reason."""
    reason = update.message.text
    rejection_query = context.user_data.get("rejection_query")

    if rejection_query:
        await rejection_query.message.reply_text(f"The story was rejected. Reason: {reason}")
        # Notify the user (implement user notification if needed)

    return ConversationHandler.END


def main():
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler for user input
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT, get_name)],
            PART: [MessageHandler(filters.TEXT, get_part)],
            AUTHOR: [MessageHandler(filters.TEXT, get_author)],
            PHOTO: [MessageHandler(filters.PHOTO | filters.TEXT, get_photo)],
            STORY: [MessageHandler(filters.TEXT, get_story)],
            MESSAGE: [MessageHandler(filters.TEXT, get_message)],
        },
        fallbacks=[],
    )

    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT, rejection_reason))

    # Start the bot
    application.run_polling()


if __name__ == "__main__":
    main()
