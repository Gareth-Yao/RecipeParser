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
    measure_words=['tablespoon','tbsp','tsp','spoon','cup','quart','pint','slice','piece','round','pound','ounce','gallon','ml','g','pinch','fluid','drop','gill','can','half','halves','head','oz','liter','gram','lb','package','wedge','sheet']
    descriptor_words=['skin','bone','fine','parts']
    ingredients = []
    for ing in all_ingredients:
        ing = re.sub('\(.*\)', '', ing)
        print(ing)
        descs, ing_info = pos_tag(word_tokenize(ing)), {}
        # quantity
        q = [a[0] for a in descs if a[1] == 'CD']
        q2 = 0 if len(q) == 0 else sum([float(i) for i in q])
        ing_info['quantity'] = q2 if (type(q2) is float and q2.is_integer() == False) else int(q2)
        # measurement
        measure, descriptors = '', []
        nouns = [a[0] for a in descs if (a[1]=='NN' or a[1]=='NNS' or a[1]=='NNP')]
        for n in nouns:
            for m in measure_words:
                if fuzz.ratio(n, m) > 70:
                    measure = n
                    break
            for d in descriptor_words:
                if fuzz.partial_ratio(n, d) > 90:
                    descriptors.append(n)
            if measure!='':
                break
        # name
        other_descs = [d[0] for d in descs if (d[1]=='JJ' or d[1]=='RB') and d[0] != measure]
        if measure!='':
            nouns.remove(measure)
            nouns = [n for n in nouns if n not in descriptors]
        else:
            for d in other_descs:
                for m in measure_words:
                    if fuzz.ratio(d,m) > 70:
                        measure = d
                        other_descs.remove(d)
                        break
        ing_info['measurement'] = measure
        ing_info['name'] = ' '.join(nouns)
        # descriptor
        descriptors.extend(other_descs)
        ing_info['descriptor'] = descriptors
        # preparation
        prep = [a[0] for a in descs if a[1]=='VBD' or a[1]=='VB' or a[1]=='VBN' or a[1]=='VBP']
        for i in range(len(prep)):
            if prep[i] == 'taste':
                prep[i] = 'to taste'
            elif prep[i] == 'needed':
                prep.remove(prep[i])
        ing_info['preparation'] = prep
        print(ing_info)
        print()
        ingredients.append(ing_info)

#trial = 'https://www.allrecipes.com/recipe/55174/baked-brie-with-caramelized-onions/'
trial = "https://www.allrecipes.com/recipe/254341/easy-paleo-chicken-marsala/"
result = fetchAndParseHTML(trial)
ingredients_parsed = get_ingredients(result["ingredients"])