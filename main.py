import os
import logging
import recipes

from rich import print_json
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Load environment variables from .env file
load_dotenv()

# Access environment variables
BOT_API = os.getenv('BOT_API')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

find_recipe_category = "Find a recipe"
find_wine_category = "Find a wine"
done = "Done"
reply_keyboard = [
    [find_recipe_category, find_wine_category],
    [done],
]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data: dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    await update.message.reply_text(
        "Hi! This is YourRecipiesBot and I help you to find a perfect recipe based on ingredients you have in your fridge. "
        "Or maybe you want to choose a wine for your meal, just let me know and I'll help you!",
        reply_markup=markup,
    )

    return CHOOSING


async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    context.user_data["choice"] = text
    message = ""
    if text == find_recipe_category:
        message = "Send me a list of ingredients you have in your fridge, please"
    elif text == find_wine_category:
        message = "Send me a meal you are going to have and I recommend you a wine"

    await update.message.reply_text(f"Do you want to {text.lower()}? I would love to help you with that! \n {message}")

    return TYPING_REPLY


async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    category = user_data["choice"]
    user_data[category] = text
    del user_data["choice"]
    if category == find_recipe_category and text:
        return await show_recipe(update, text)
    elif category == find_wine_category:
        return await show_wine(update, text)


async def show_recipe(update: Update, search_text: str):
    response = await recipes.search_recipe_by_ingredients(search_text)
    count = len(response)

    await update.message.reply_text(
        f"Neat! Look, I've found {count} recipes",
        reply_markup=markup,
    )

    return CHOOSING


async def show_wine(update: Update, search_text: str):
    response = await recipes.search_wine_by_meal(search_text)

    await update.message.reply_text(
        f"Neat! Look what I've found",
        reply_markup=markup,
    )

    return CHOOSING


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text(
        f"I learned these facts about you: {facts_to_str(user_data)}Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_API).build()

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex(f"^({find_recipe_category}|{find_wine_category})$"), regular_choice
                )
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex(f"^{done}$")), regular_choice
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex(f"^{done}$")),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex(f"^{done}$"), done)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
