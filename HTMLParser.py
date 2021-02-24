import requests
from bs4 import BeautifulSoup
import unicodedata

def convertUnicode(s):
    newStr = ""
    for c in s:
        try:
            name = unicodedata.name(c)
            newC = c
            if name.startswith("VULGAR"):
                newC = unicodedata.numeric(c)
            newStr += str(newC)
        except ValueError:
            newStr += c
            continue

    return newStr


def fetchAndParseHTML(url):
    try:
        html_text = requests.get(url).text
        soup = BeautifulSoup(html_text, 'html.parser')
        title = soup.find("h1", {"class" : "headline"},text=True).text
        servings = soup.find("div", {"class" : "recipe-manually-adjust-servings"}).attrs['data-init-servings-size']
        ingredients = soup.find("fieldset", {"class" : "ingredients-section__fieldset"}).findChildren("li", recursive=True)
        ingredients = [convertUnicode(' '.join(i.text.replace('\n', '').strip().split()).lower()) for i in ingredients]
        instructions = soup.find("fieldset", {"class" : "instructions-section__fieldset"}).findChildren("div", attrs={"section-body"}, recursive=True)
        instructions = [convertUnicode(' '.join(i.text.replace('\n', '').strip().split()).lower()) for i in instructions]
        tags = soup.find("nav", {"class": "breadcrumbs__container"}).findChildren("a", recursive=True)
        tags = [' '.join(i.text.replace('\n', '').strip().split()).lower() for i in tags]
        tags = [i.replace(' recipes', '') for i in tags if i != 'home' and i != 'recipes']
        return {"name": title, "servings": servings, "ingredients": ingredients, "instructions": instructions, 'tags' : tags}
    except AttributeError:
        print("Error Fetching Page Information")
        return {}



trial = "https://www.allrecipes.com/recipe/254341/easy-paleo-chicken-marsala/"
fetchAndParseHTML(trial)