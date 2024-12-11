import requests
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY')


async def search_recipe_by_ingredients(ingredients: str):
    # ingredients - string - A comma-separated list of ingredients that the recipes should contain.
    # number - number - The maximum number of recipes to return (between 1 and 100). Defaults to 10.
    # ranking - number - Whether to maximize used ingredients (1) or minimize missing ingredients (2) first.
    payload = {'ingredients': ingredients, 'number': 3, 'ranking': 2}
    headers = {'x-api-key': SPOONACULAR_API_KEY}
    r = requests.get('https://api.spoonacular.com/recipes/findByIngredients', params=payload, headers=headers)
    return r.json()


async def search_wine_by_meal(meal: str):
    # food - string - This can be a dish ("steak"), an ingredient ("salmon"), or a cuisine ("italian").
    payload = {'food': meal}
    headers = {'x-api-key': SPOONACULAR_API_KEY}
    r = requests.get('https://api.spoonacular.com/food/wine/pairing', params=payload, headers=headers)
    return format_wine_response(r.json())


def format_wine_response(response) -> str:
    print(response)
    default_message = "Could not find anything, try again with another search"

    if not response or not isinstance(response, dict):
        return default_message
    if response.get('status') == 'failure':
        return default_message
    if response.get('pairingText'):
        return response.get('pairingText')
