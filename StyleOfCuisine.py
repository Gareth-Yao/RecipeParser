import HTMLParser
import requests
import InstructionParser
from bs4 import BeautifulSoup
from ingredients import *
import json
Italian = {
    'protein' : {},
    'spices' : {},
    'vegetables' : {},
    'cooking methods' : {}
}

url = 'https://www.allrecipes.com/recipes/723/world-cuisine/european/italian/'
page2 = 'https://www.allrecipes.com/recipes/723/world-cuisine/european/italian/?page='
root = 'https://www.allrecipes.com/'

def getMoreData(pageNum):
    temp = page2
    temp += str(pageNum)
    try:
        html_text = requests.get(temp).text
        soup = BeautifulSoup(html_text, 'html.parser')
        recipes = soup.findAll("a", {"class": "tout__titleLink"})
        for recipe in recipes:
            link = root + recipe.attrs['href']
            results = HTMLParser.fetchAndParseHTML(link)
            ingredients = HTMLParser.get_ingredients(results['ingredients'])
            steps = InstructionParser.parseToolsAndCookingMethod(link, replaceEmptyMainMethod=False)
            for ing in ingredients:
                if ing['name'].lower() in meats or ing['name'].lower() in seafood:
                    Italian['protein'][ing['name'].lower()] = Italian['protein'].get(ing['name'].lower(), 0) + 1
                elif ing['name'].lower() in vegetables:
                    Italian['vegetables'][ing['name'].lower()] = Italian['vegetables'].get(ing['name'].lower(), 0) + 1
                elif ing['name'].lower() in herbs_spices:
                    Italian['spices'][ing['name'].lower()] = Italian['spices'].get(ing['name'].lower(), 0) + 1
            Italian['cooking methods'][steps['main_cooking_method'].lower()] = Italian['cooking methods'].get(
                steps['main_cooking_method'].lower(), 0) + 1
    except AttributeError:
        print("Error Fetching Page Information")

try:
    for i in range(2, 6):
        getMoreData(2)
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')

    recipes = soup.findAll("div", {"class": "card__detailsContainer"})
    for recipe in recipes:
        link = recipe.findChildren("a", recursive=True)[0].attrs['href']
        results = HTMLParser.fetchAndParseHTML(link)
        ingredients = HTMLParser.get_ingredients(results['ingredients'])
        steps = InstructionParser.parseToolsAndCookingMethod(link, replaceEmptyMainMethod=False)
        for ing in ingredients:
            if ing['name'].lower() in meats or ing['name'].lower() in seafood:
                Italian['protein'][ing['name'].lower()] = Italian['protein'].get(ing['name'].lower(), 0) + 1
            elif ing['name'].lower() in vegetables:
                Italian['vegetables'][ing['name'].lower()] = Italian['vegetables'].get(ing['name'].lower(), 0) + 1
            elif ing['name'].lower() in herbs_spices:
                Italian['spices'][ing['name'].lower()] = Italian['spices'].get(ing['name'].lower(), 0) + 1
        Italian['cooking methods'][steps['main_cooking_method'].lower()] = Italian['cooking methods'].get(steps['main_cooking_method'].lower(), 0) + 1
    print(Italian)
    with open('Italian_Ingredients.json','w') as f:
            json.dump(Italian, f, indent=4)

except AttributeError:
    print("Error Fetching Page Information")

