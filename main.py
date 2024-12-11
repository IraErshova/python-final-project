import logging
import spoonacular
import constants

from config import BOT_API
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def build_markup():
    reply_keyboard = [
        [constants.RECIPE_CATEGORY, constants.WINE_CATEGORY],
        [constants.DONE],
    ]
    return ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    await update.message.reply_text(
        "Hi! This is YourRecipiesBot and I help you to find a perfect recipe based on ingredients you have in your fridge. "
        "Or maybe you want to choose a wine for your meal, just let me know and I'll help you!",
        reply_markup=build_markup(),
    )

    return constants.CHOOSING_CATEGORY


async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask user for info based on the selected option."""
    text = update.message.text
    context.user_data["choice"] = text
    message = ""
    if text == constants.RECIPE_CATEGORY:
        message = "Send me a list of ingredients you have in your fridge, please"
    elif text == constants.WINE_CATEGORY:
        message = "Send me a meal you are going to have and I recommend you a wine"

    await update.message.reply_text(f"Do you want to {text.lower()}? I would love to help you with that!\n{message}")

    return constants.TYPING_REPLY


async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get the info based on user's input."""
    user_data = context.user_data
    text = update.message.text
    category = user_data["choice"]
    user_data[category] = text
    del user_data["choice"]
    if category == constants.RECIPE_CATEGORY and text:
        return await get_recipe(update, text)
    elif category == constants.WINE_CATEGORY:
        return await get_wine(update, text)


async def get_recipe(update: Update, search_text: str):
    response = await spoonacular.search_recipe_by_ingredients(search_text)

    await update.message.reply_text(
        response,
        reply_markup=build_markup(),
    )

    return constants.CHOOSING_CATEGORY


async def get_wine(update: Update, search_text: str):
    response = await spoonacular.search_wine_by_meal(search_text)
    await update.message.reply_text(
        response,
        reply_markup=build_markup(),
    )

    return constants.CHOOSING_CATEGORY


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """end the conversation."""
    user_data = context.user_data
    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_API).build()

    # Add conversation handler with the states CHOOSING_CATEGORY, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            constants.CHOOSING_CATEGORY: [
                MessageHandler(
                    filters.Regex(f"^({constants.RECIPE_CATEGORY}|{constants.WINE_CATEGORY})$"), regular_choice
                )
            ],
            constants.TYPING_CHOICE: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex(f"^{constants.DONE}$")), regular_choice
                )
            ],
            constants.TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex(f"^{constants.DONE}$")),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex(f"^{constants.DONE}$"), done)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
