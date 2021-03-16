from nltk.tokenize import sent_tokenize
import requests
from bs4 import BeautifulSoup
import unicodedata
import nltk
from nltk import pos_tag, word_tokenize
from nltk.stem import PorterStemmer
from fuzzywuzzy import fuzz
import re
from ingredients import meats, seafood, vegetarian_subs, herbs_spices, meat_subs, prep_words, measure_words, descriptor_words, extra, vegetables, dairy, oils
import random
import spacy
from spacy.tokenizer import Tokenizer
from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER, CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS
from spacy.util import compile_infix_regex
import copy

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
        url = url.strip()
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
        return {"name": title, "servings": servings, "ingredients": ingredients, "instructions": instructions, "tags" : tags}
    except:
        print("Error Fetching Page Information")
        return {}
    
def get_ingredients(all_ingredients):
    def custom_tokenizer(nlp):
        infixes = (LIST_ELLIPSES+LIST_ICONS+ [ r"(?<=[0-9])[+\-\*^](?=[0-9-])",r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
                al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES),r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
                r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA)])
        infix_re = compile_infix_regex(infixes)
        return Tokenizer(nlp.vocab, prefix_search=nlp.tokenizer.prefix_search, suffix_search=nlp.tokenizer.suffix_search,
                                    infix_finditer=infix_re.finditer, token_match=nlp.tokenizer.token_match, rules=nlp.Defaults.tokenizer_exceptions)
    nlp = spacy.load("en_core_web_sm")
    nlp.tokenizer = custom_tokenizer(nlp)
    ingredients = []
    for ing in all_ingredients:
        descriptors, ing_info = [], {}
        if '(optional)' in ing.lower():
            ing = re.sub('\(optional\)','',ing)
            descriptors.append('optional')
        ing = re.sub('\([^()]*\)','',ing)
        ing = re.sub('  ',' ',ing)
        ing = re.sub('inch pieces', '', ing)
        doc, q = nlp(ing), 0
        for i, token in enumerate(doc):
            if i > 1:
                break
            elif token.pos_=='NUM' and (i == 0 or i == 1):
                q += float(token.text)
        nouns, m = [token.text for token in doc if token.pos_ == 'NOUN' or token.pos_ == 'PROPN' or token.text in extra], ''
        ing_info['quantity'] = q if type(q) is float and q.is_integer() == False else int(q)
        for i, token in enumerate(doc):
            if q==0:
                break
            elif token.text in measure_words or token.text+'s' in measure_words or token.text[:-1] in measure_words and token.text!='cubed' and token.text!='sliced':
                m = token.text
                break
        for noun in nouns:
            for d in descriptor_words:
                if fuzz.ratio(noun, d) > 90:
                    descriptors.append(noun)
        name = ' '.join([n for n in nouns if n != m and n not in descriptors])
        prep = [token.text for token in doc if (token.text in prep_words and token.text not in nouns) or \
            (token.text not in nouns and token.text not in measure_words and token.text not in descriptor_words and token.text!=m and (token.pos_ == 'VERB' or token.pos_ == 'ADV') and token.text!='needed' and token.text!='more')]
        descriptors += [token.text for token in doc if (token.text in descriptor_words and token.text not in descriptors) or token.pos_ == 'ADJ' and token.text != m and token.text not in prep and token.text not in nouns and token.text!='more']
        for i, p in enumerate(prep):
            if p == 'taste':
                prep[i] = 'to taste'
            elif p =='seasoning':
                prep.remove(p)
            elif p =='sour' and 'cream' in name:
                name = p+' '+name
                prep.remove(p)
        for i, d in enumerate(descriptors):
            if d == 'sour' and 'cream' in name:
                name = d+' '+name
                descriptors.remove(d)
                break 
        for i, t in enumerate(doc):
            if t.text in prep and i > 0 and doc[i-1].text=='for':
                descriptors.append('for'+' '+t.text)
                prep.remove(t.text)
        if 'salt' in name and 'pepper' in name and q == 0:
            temp = name.split(' ')
            temp.remove('pepper')
            new_name, name = ' '.join(temp), 'pepper'
            ingredients.append({'quantity': 0, 'measurement': '', 'name': new_name, 'descriptor': [], 'preparation': ['to taste']})
        ing_info['name'] = name
        ing_info['descriptor'] = descriptors
        ing_info['preparation'] = prep
        ing_info['measurement'] = m if m not in prep and m not in ing_info['descriptor'] else ''
        ingredients.append(ing_info)
    return ingredients

def to_vegetarian(ings):
    # converts any recipe w/ meat to vegetarian by substituting the meat ingredeints with vegetarian ones
    replaced, res = vegetarian_subs, {}
    for i, ing in enumerate(ings):
        tokens = ing['name'].lower().split(' ')
        for t in tokens:
            if t in meats or t+'s' in meats or t in seafood or t+'s' in seafood:
                ran = random.choice(replaced)
                m, q = ing['measurement'], ing['quantity']
                ran['measurement'], ran['quantity'] = m if m!= '' else ran['measurement'], q if q!= 0 else ran['quantity']
                res[ing['name']] = ran
                replaced.remove(ran)
                break
    return res

def from_vegetarian(ings):
    # check if vegetarian. if yes, converts a recipe from vegetarian to non vegetarian by adding a meat sub. if no, do nothing
    res, veg, veg_i = {}, True, 0
    for i, ing in enumerate(ings):
        tokens = ing['name'].lower().split(' ')
        for t in tokens:
            if t in meats or t+'s' in meats or t in seafood or t+'s' in seafood:
                veg = False
                break
            elif t in vegetables or t+'s' in vegetables:
                veg_i = i
        if veg == False:
            break
    if veg == True:
        ran = random.choice(meat_subs)
        m, q = ings[veg_i]['measurement'], ings[veg_i]['quantity']
        ran['measurement'], ran['quantity'] = m if m!= '' else ran['measurement'], q if q!= 0 else ran['quantity']
        res[ings[veg_i]['name']] = ran
    return res

def format_ings(ings):
    def dec_to_mixed_frac(dec):
        if isinstance(dec, int): return str(dec)
        n, d = dec.as_integer_ratio()
        a, b = n//d, n%d
        if a == 0: return "{}/{}".format(b,d)
        else: return "{} {}/{}".format(a,b,d)
    res = []
    for ing in ings:
        optional, for_words = False, []
        temp = '' if ing['quantity'] == 0 else dec_to_mixed_frac(ing['quantity'])+' '
        temp += ing['measurement']+' ' if len(ing['measurement']) > 0 else ''
        d, p = ing['descriptor'], ing['preparation']
        if len(d) > 0:
            des_temp = ''
            for des in d:
                if des == 'optional':
                    optional = True
                elif 'for' in des:
                    for_words.append(des)
                else:
                    des_temp += des + ', '
            des_temp = des_temp[:-2] + ' ' if des_temp[-2:]==', ' else des_temp
            temp += des_temp
        temp += ing['name']
        if len(p) > 0:
            temp_prep = ''
            for prep in p:
                if prep == 'finely' or prep == 'thinly' or prep=='freshly':
                    temp_prep += prep + ' '
                elif prep == 'optional':
                    optional = True
                else:
                    temp_prep += prep + ', '
            temp_prep = temp_prep[:-2]
            temp += ', ' + temp_prep
        if len(for_words) > 0:
            temp += ', '+', '.join(for_words)
        if optional:
            temp += ' (optional)'
        res.append(temp.strip())
    return res 

def to_healthy(ings):
    h_ing = copy.deepcopy(ings)
    for i in h_ing:
        if i['name'] in vegetables or i['name'] + 's' in vegetables:
            if 'organic' not in i['descriptor']:
                i['descriptor'].insert(0, 'organic')
        if i['name'] in meats or i['name'] + 's' in meats:
            if 'fatty' in i['descriptor']:
                i['descriptor'].remove('fatty')
            if 'lean' not in i['descriptor']:
                i['descriptor'].insert(0, 'lean')
        if i['name'] in seafood or i['name'] + 's' in seafood:
            if 'frozen' in i['descriptor']:
                i['descriptor'].remove('frozen')
            if 'fresh-caught' not in i['descriptor']:
                i['descriptor'].insert(0, 'fresh-caught')
        if i['name'] in herbs_spices or i['name'] + 's' in herbs_spices:
            if 'fresh' not in i['descriptor']:
                i['descriptor'].insert(0, 'fresh')
        if i['name'] in dairy or i['name'] + 's' in dairy:
            if 'full-fat' in i['descriptor']:
                i['descriptor'].remove('full-fat')
            if 'low-fat' not in i['descriptor']:
                i['descriptor'].insert(0, 'low-fat')
        if i['name'] in oils or i['name'] + 's' in oils:
            i['name'] = 'oil'
            i['descriptor'] = 'vegetable'
        if 'sugar' in i['name']:
            i['name'] = 'honey'
            i['descriptor'] = 'organic'
    return h_ing

def to_unhealthy(ings):
    u_ing = copy.deepcopy(ings)
    for i in u_ing:
        if i['name'] in vegetables or i['name'] + 's' in vegetables:
            if 'organic' in i['descriptor']:
                i['descriptor'].remove('organic')
        if i['name'] in meats or i['name'] + 's' in meats:
            if 'lean' in i['descriptor']:
                i['descriptor'].remove('lean')
            if 'fatty' not in i['descriptor']:
                i['descriptor'].insert(0, 'fatty')
        if i['name'] in seafood or i['name'] + 's' in seafood:
            if 'fresh-caught' in i['descriptor']:
                i['descriptor'].remove('fresh-caught')
            if 'frozen' not in i['descriptor']:
                i['descriptor'].insert(0, 'frozen')
        if i['name'] in herbs_spices or i['name'] + 's' in herbs_spices:
            if 'fresh' in i['descriptor']:
                i['descriptor'].remove('fresh')
        if i['name'] in dairy or i['name'] + 's' in dairy:
            if 'low-fat' in i['descriptor']:
                i['descriptor'].remove('low-fat')
            if 'full-fat' not in i['descriptor']:
                i['descriptor'].insert(0, 'full-fat')
        if i['name'] in oils or i['name'] + 's' in oils:
            i['name'] = 'lard'
            i['descriptor'] = []
        if 'honey' in i['name']:
            i['name'] = 'sugar'
            i['descriptor'] = 'white'
    return u_ing
        

trial = 'https://www.allrecipes.com/recipe/60598/vegetarian-korma/'
#trial = 'https://www.allrecipes.com/recipe/246631/savory-vegetarian-quinoa/'
#trial = 'https://www.allrecipes.com/recipe/270712/air-fryer-coconut-shrimp/'
#trial = 'https://www.allrecipes.com/recipe/221351/german-hamburgers-frikadellen/'
#trial = 'https://www.allrecipes.com/recipe/282792/pinto-bean-and-chicken-casserole/'
#trial = 'https://www.allrecipes.com/recipe/92462/slow-cooker-texas-pulled-pork/'
#trial = 'https://www.allrecipes.com/recipe/261461/stuffed-bell-pepper-rings/'
#trial = 'https://www.allrecipes.com/recipe/244929/lemon-meringue-cheesecake/'
#trial = 'https://www.allrecipes.com/recipe/223042/chicken-parmesan/'
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
#trial = "https://www.allrecipes.com/recipe/254341/easy-paleo-chicken-marsala/"

# result = fetchAndParseHTML(trial)
# ingredients_parsed = get_ingredients(result["ingredients"])
# print(format_ings(ingredients_parsed))
