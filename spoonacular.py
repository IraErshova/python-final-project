import requests
from config import SPOONACULAR_API_KEY

async def search_recipe_by_ingredients(ingredients: str):
    # ingredients - string - A comma-separated list of ingredients that the recipes should contain.
    # number - number - The maximum number of recipes to return (between 1 and 100). Defaults to 10.
    # ranking - number - Whether to maximize used ingredients (1) or minimize missing ingredients (2) first.
    payload = {'ingredients': ingredients, 'number': 3, 'ranking': 2}
    headers = {'x-api-key': SPOONACULAR_API_KEY}
    r = requests.get('https://api.spoonacular.com/recipes/findByIngredients', params=payload, headers=headers)
    return format_recipe_response(r.json())


async def search_wine_by_meal(meal: str):
    # food - string - This can be a dish ("steak"), an ingredient ("salmon"), or a cuisine ("italian").
    payload = {'food': meal}
    headers = {'x-api-key': SPOONACULAR_API_KEY}
    r = requests.get('https://api.spoonacular.com/food/wine/pairing', params=payload, headers=headers)
    return format_wine_response(r.json())


def format_wine_response(response) -> str:
    default_message = "Could not find anything, try again with another search"

    if not response or not isinstance(response, dict):
        return default_message
    if response.get('status') == 'failure':
        return default_message
    if response.get('pairingText'):
        return response.get('pairingText')
    else:
        return default_message


def format_recipe_response(response) -> str:
    print(response)
    if not list or not isinstance(response, list) or len(response) == 0:
        return "Could not find anything, try again with another search"

    formatted_recipes = "Neat! Look what I've found:\n\n"
    for recipe in response:
        recipe_title = recipe['title']
        missed_ingredients = [ingredient['name'] for ingredient in recipe['missedIngredients']]
        used_ingredients = [ingredient['original'] for ingredient in recipe['usedIngredients']]

        # Format the recipe details
        formatted_recipe = f"Recipe Title: {recipe_title}\n"
        formatted_recipe += "Missed Ingredients:\n"
        formatted_recipe += "\n".join(f"- {ingredient}" for ingredient in missed_ingredients)
        formatted_recipe += "\nUsed Ingredients:\n"
        formatted_recipe += "\n".join(f"- {ingredient}" for ingredient in used_ingredients)
        formatted_recipe += "\n\n"  # Separate recipes with an extra newline

        formatted_recipes += formatted_recipe

    return formatted_recipes
