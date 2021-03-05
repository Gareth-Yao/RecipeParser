import requests
from bs4 import BeautifulSoup
import unicodedata
from nltk import pos_tag, word_tokenize
from fuzzywuzzy import fuzz
import re
from ingredients import meats, seafood, vegetarian_subs, herbs_spices, meat_subs, measure_words, descriptor_words
import random
import spacy

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
    
def get_ingredients(all_ingredients):
    nlp = spacy.load("en_core_web_sm")
    ingredients = []
    for ing in all_ingredients:
        descriptors, ing_info = [], {}
        if '(optional)' in ing.lower():
            ing = re.sub('\(optional\)\040','',ing)
            descriptors.append('optional')
        ing = re.sub('\(.*\)\040', '', ing)
        doc = nlp(ing)
        nums, nouns = [token.text for token in doc if token.pos_ == 'NUM'], [token.text for token in doc if token.pos_ == 'NOUN' or token.pos_ == 'PROPN']
        q, m = sum([float(i) for i in nums]) if len(nums) > 0 else 0, ''
        ing_info['quantity'] = q if type(q) is float and q.is_integer() == False else int(q)
        print(ing)
        for i, token in enumerate(doc):
            if len(nums) < 1:
                break
            elif token.text in measure_words or token.text+'s' in measure_words or token.text[:-1] in measure_words:
                m = token.text
                break
        # for token in doc:
        #     print(token, token.pos_)
        for noun in nouns:
            for d in descriptor_words:
                if fuzz.ratio(noun, d) > 80:
                    descriptors.append(noun)
        ing_info['measurement'] = m 
        ing_info['name'] = ' '.join([n for n in nouns if n != m and n not in descriptors])
        ing_info['descriptor'] = [token.text for token in doc if token.pos_ == 'ADJ']
        ing_info['descriptor'] += descriptors 
        ing_info['preparation'] = [token.text for token in doc if token.pos_ == 'VERB' or token.pos_ == 'ADV'] 
        ingredients.append(ing_info)
        print(ing_info)
    return ingredients
'''
def get_ingredients(all_ingredients): #argument is result["ingredients"] of a recipe
    measure_words=['tablespoon','teaspoon','tbsp','tsp','spoon','cup','quart','pint','slice','piece','round','pound','ounce','gallon','ml','g','pinch','fluid','drop','gill','can','half','halves','head','oz','clove','fillet','filet','bottle','liter','gram','lb','package','wedge','sheet','cube','stalk','thirds']
    descriptor_words=['optional','skin','bone','fine','parts','dried','ground']
    ingredients = []
    for ing in all_ingredients:
        measure, descriptors = '', []
        if '(optional)' in ing.lower():
            ing = re.sub('\(optional\)','',ing)
            descriptors.append('optional')
        ing = re.sub('\(.*\)', '', ing)
        descs, ing_info = pos_tag(word_tokenize(ing)), {}
        # quantity
        q = [a[0] for a in descs if a[1] == 'CD']
        q2 = 0 if len(q) == 0 else sum([float(i) for i in q])
        ing_info['quantity'] = q2 if (type(q2) is float and q2.is_integer() == False) else int(q2)
        # measurement
        nouns = [a[0] for a in descs if ((a[1]=='NN' or a[1]=='NNS' or a[1]=='NNP') or a[0] in herbs_spices or a[0]=='can' or a[0]=='cans' or a[0] in seafood or a[0] in meats) and a[0] not in descriptor_words]
        for n in nouns:
            for m in measure_words:
                if fuzz.ratio(n, m) > 80 and n != 'inch':
                    measure = n
                    break
            for d in descriptor_words:
                if fuzz.partial_ratio(n, d) > 90:
                    descriptors.append(n)
                    break
            if measure!='':
                break
        # name
        other_descs = [d[0] for d in descs if (d[1]=='JJ' or d[1]=='RB' or d[0] in descriptor_words) and d[0] != measure and d[0] not in nouns]
        if measure!='':
            nouns.remove(measure)
            nouns = [n for n in nouns if n not in descriptors]
        else:
            for d in other_descs:
                for m in measure_words:
                    if fuzz.ratio(d,m) > 95:
                        measure = d
                        other_descs.remove(d)
                        break
        nouns = [n for n in nouns if n!='piece' and n!='pieces' and n!='inch' and n!='inches' and n!='thirds']
        ing_info['measurement'] = measure
        ing_info['name'] = ' '.join(nouns)
        # descriptor
        descriptors.extend(other_descs)
        ing_info['descriptor'] = descriptors
        # preparation
        prep = [a[0] for a in descs if (a[1]=='VBD' or a[1]=='VB' or a[1]=='VBN' or a[1]=='VBP') and a[0] not in descriptors and a[0] not in nouns]
        for i in range(len(prep)):
            if prep[i] == 'taste':
                prep[i] = 'to taste'
            elif prep[i] == 'needed':
                prep.remove(prep[i])
        ing_info['preparation'] = prep
        ingredients.append(ing_info)

    return ingredients
'''

def to_vegetarian(ings):
    # converts any recipe w/ meat to vegetarian by substituting the meat ingredeints with vegetarian ones
    replaced, res = vegetarian_subs, {}
    for i, ing in enumerate(ings):
        tokens = ing['name'].lower().split(' ')
        for t in tokens:
            if t in meats or t+'s' in meats or t in seafood or t+'s' in seafood:
                ran = random.choice(replaced)
                ran['measurement'], ran['quantity'] = ing['measurement'], ing['quantity']
                res[ing['name']] = ran
                replaced.remove(ran)
                break
    return res

def from_vegetarian(ings):
    # check if vegetarian. if yes, converts a recipe from vegetarian to non vegetarian by adding a meat sub. if no, do nothing
    for i, ing in enumerate(ings):
        tokens = ing['name'].lower().split(' ')
        for t in tokens:
            if t in meats or t+'s' in meats or t in seafood or t+'s' in seafood:
                return ings
    ings.append(random.choice(meat_subs))
    return ings



#trial = 'https://www.allrecipes.com/recipe/231808/grandmas-ground-beef-casserole/'
#trial = 'https://www.allrecipes.com/recipe/47247/chili-rellenos-casserole/'
#trial = 'https://www.allrecipes.com/recipe/218901/beef-enchiladas-with-spicy-red-sauce/'
#trial = 'https://www.allrecipes.com/recipe/89965/vegetarian-southwest-one-pot-dinner/'
#trial = 'https://www.allrecipes.com/recipe/156232/my-special-shrimp-scampi-florentine/'
#trial = 'https://www.allrecipes.com/recipe/268026/instant-pot-corned-beef/'
#trial = 'https://www.allrecipes.com/recipe/110447/melt-in-your-mouth-broiled-salmon/'
#trial = 'https://www.allrecipes.com/recipe/268514/instant-pot-dr-pepper-pulled-pork/'
#trial = 'https://www.allrecipes.com/recipe/269652/tuscan-pork-tenderloin/'
#trial = 'https://www.allrecipes.com/recipe/158440/sophies-shepherds-pie/'
#trial = 'https://www.allrecipes.com/recipe/25678/beef-stew-vi/'
#trial = 'https://www.allrecipes.com/recipe/234799/poor-mans-stroganoff/'
#trial = 'https://www.allrecipes.com/recipe/55174/baked-brie-with-caramelized-onions/'
trial = "https://www.allrecipes.com/recipe/254341/easy-paleo-chicken-marsala/"

result = fetchAndParseHTML(trial)
ingredients_parsed = get_ingredients(result["ingredients"])
#veg = to_vegetarian(ingredients_parsed)
#non_veg = to_vegetarian(ingredients_parsed)
#print(veg)

