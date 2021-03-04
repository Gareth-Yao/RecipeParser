import HTMLParser
import requests
import InstructionParser
from bs4 import BeautifulSoup
from ingredients import *
Italian = {
    'protein' : {},
    'spices' : {},
    'vegetables' : {},
    'cooking methods' : {}
}

url = 'https://www.allrecipes.com/recipes/723/world-cuisine/european/italian/'
try:
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')

    recipes = soup.findAll("div", {"class": "card__detailsContainer"})
    for recipe in recipes:
        link = recipe.findChildren("a", recursive=True)[0].attrs['href']
        results = HTMLParser.fetchAndParseHTML(link)
        ingredients = HTMLParser.get_ingredients(results['ingredients'])
        steps = InstructionParser.parseToolsAndCookingMethod(link)
        for ing in ingredients:
            if ing['name'].lower() in meats or ing['name'].lower() in seafood:
                Italian['protein'][ing['name'].lower()] = Italian['protein'].get(ing['name'].lower(), 0) + 1
            elif ing['name'].lower() in vegetables:
                Italian['vegetables'][ing['name'].lower()] = Italian['vegetables'].get(ing['name'].lower(), 0) + 1
            elif ing['name'].lower() in herbs_spices:
                Italian['spices'][ing['name'].lower()] = Italian['vegetables'].get(ing['spices'].lower(), 0) + 1
        Italian['cooking methods'][steps['main_cooking_method'].lower()] = Italian['cooking methods'].get(steps['main_cooking_method'].lower(), 0) + 1
    
    print(Italian)

except AttributeError:
    print("Error Fetching Page Information")

