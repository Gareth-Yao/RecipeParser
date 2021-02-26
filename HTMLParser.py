import requests
from bs4 import BeautifulSoup
import unicodedata
from nltk import pos_tag, word_tokenize
from fuzzywuzzy import fuzz
import re

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


def get_ingredients(all_ingredients): #argument is result["ingredients"] of a recipe
    measure_words=['tablespoon','tbsp','tsp','spoon','cup','quart','pint','slice','piece','round','pound','ounce','gallon','ml','g','pinch','fluid','drop','gill','can','half','halves','head','oz','liter','gram','lb','package']
    ingredients = {}
    for ing in all_ingredients:
        ing = re.sub('\(.*\)', '', ing)
        print(ing)
        descs, ing_info = pos_tag(word_tokenize(ing)), {}
        # quantity
        q = [a[0] for a in descs if a[1] == 'CD']
        q2 = 0 if len(q) == 0 else sum([float(i) for i in q])
        ing_info['quantity'] = int(q2) if q2.is_integer() else q2
        # measurement
        measure = ''
        nouns = [a[0] for a in descs if a[1]=='NN' or a[1]=='NNS' or a[1]=='NNP'] 
        for n in nouns:
            for m in measure_words:
                if fuzz.ratio(n, m) > 70:
                    measure = n
                    break
            if measure != '':
                break
        ing_info['measurement'] = measure
        print(ing_info['quantity'])
        print(ing_info['measurement'])
    # for ing in all_ingredients:
    #     i, descs, q = {}, pos_tag(word_tokenize(ing)), -1
    #     ing = re.sub(r'\([^)]*\)', '', ing)
    #     print(ing)
    #     for token in descs:
    #         if token[1] == 'CD':
    #             q, q_index = token[0], descs.index(token)
    #     i['quantity'] = 0 if q==-1 else q
    #     measure = ''
    #     if q_index + 1 < len(descs):
    #         for m in measure_words:
    #             if fuzz.ratio(m, descs[q_index+1][0]) > 70:
    #                 measure = descs[q_index+1][0]
    #                 break
    #     i['measurement'] = measure
    #     print(i['quantity'])
    #     print(i['measurement'])


trial = 'https://www.allrecipes.com/recipe/200296/salmon-wellington/'
#trial = "https://www.allrecipes.com/recipe/254341/easy-paleo-chicken-marsala/"
result = fetchAndParseHTML(trial)
ingredients_parsed = get_ingredients(result["ingredients"])