import requests
from bs4 import BeautifulSoup
import unicodedata
from nltk import pos_tag, word_tokenize
from fuzzywuzzy import fuzz
import re
from ingredients import meats, seafood, vegetarian_subs, herbs_spices, meat_subs, herbs, spices, veggies, l_f, grains, l_m, h_subs, u_subs, italian_herbs, other_herbs, italian_proteins, other_proteins, italian_pasta, other_noodles, other_oils, other_vinegars
import random
import copy

kitchen_tools = ["oven", "stove", "burner", "grill", "toaster", "pan", "non-stick pan", "pot", "dutch oven",
                 "knife", "chef's knife", "paring knife", "garlic press", "spoon", "bowl", "whisk", "grater",
                 "microwave", "skillet", "saucepan", "baking tray", "baking dish", "baking pan", "cake pan",
                 "baking sheet", "cookie sheet", "mixer", "strainer", "colander", "sifter", "blender", "food processor",
                 "foil", "alunimum foil", "parchment paper", "wax paper", "slow cooker", "rice cooker", "sous vide", "crock pot",
                 "zester", "juicer", "casserole dish", "dish"]
                
primary_methods = ["bake", "broil", "boil", "sautee", "poach", "fry", "stir fry", "brown", "heat", "grill", "simmer", "reduce",
                   "slow cook", "cook", "sous vide", "sear", "toast", "microwave", "warm"]

secondary_methods = ["chop", "slice", "dice", "mince", "grate", "zest", "mix", "stir", "combine", "fold", "pour", "whisk", "beat",
                     "juice", "squeeze", "strain", "sift", "drain", "add", "blend", "scoop", "top", "spoon", "cover", "uncover",
                     "discard", "reserve", "preheat", "melt"]

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
    measure_words=['tablespoon','teaspoon','tbsp','tsp','spoon','cup','quart','pint','slice','piece','round','pound','ounce','gallon','ml','g','pinch','fluid','drop','gill','can','half','halves','head','oz','clove','fillet','filet','bottle','liter','gram','lb','package','wedge','sheet','cube','stalk','thirds']
    descriptor_words=['optional','skin','bone','fine','parts','dried','ground', 'fresh', 'organic']
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
        print(ing_info)
    return ingredients

def parseSteps(steps, ingredients):
    # Do we want the list of ingredients for each step to be just
    # ingredient names or the actual dict?
    #TODO
    step_tools = []
    step_p_methods = []
    step_s_methods = []
    split_steps = []

    for s in steps:
        step = word_tokenize(s)
        split_step = {'ingredients':[], 'tools':[], 'primary methods':[], 'secondary methods':[], 'times':[]}
        for i, w in enumerate(step):
            if i < len(step) - 1:
                bigram = w + " " + step[i+1]
                if bigram in kitchen_tools:
                    if bigram not in step_tools:
                        step_tools.append(bigram)
                    if bigram not in split_step['tools']:
                        split_step['tools'].append(bigram)
                if bigram in primary_methods:
                    if bigram not in step_p_methods:
                        step_p_methods.append(bigram)
                    if bigram not in split_step['primary methods']:
                        split_step['primary methods'].append(bigram)
                if bigram in secondary_methods:
                    if bigram not in step_s_methods:
                        step_s_methods.append(bigram)
                    if bigram not in split_step['secondary methods']:
                        split_step['secondary methods'].append(bigram)
                # if ingredients is just list of names
                if bigram in ingredients:
                    if bigram not in split_step['ingredients']:
                        split_step['ingredients'].append(bigram)
                # if ingredients should be dict
                """
                ing = next((i for i in ingredients if i["name"] == bigram), False) # append ingredients[bigram]
                if ing:
                    if ing["name"] not in [n['name'] for n in split_step['ingredients']]:
                        split_step['ingredients'].append(ing)
                """

            if w in kitchen_tools:
                skip = False
                try:
                    if step[i-1] + " " + w in kitchen_tools:
                        skip = True
                        if step[i-1] + " " + w not in step_tools:
                            step_tools.append(step[i-1] + " " + w)
                        if step[i-1] + " " + w not in split_step['tools']:
                            split_step['tools'].append(step[i-1] + " " + w)
                except Exception:
                    pass
                try:
                    if w + " " + step[i+1] in kitchen_tools:
                        skip = True
                        if w + " " + step[i+1] not in step_tools:
                            step_tools.append(w + " " + step[i+1])
                        if w + " " + step[i+1] not in split_step['tools']:
                            split_step['tools'].append(w + " " + step[i+1])
                except Exception:
                    pass
                if not skip:
                    if w not in step_tools:
                        step_tools.append(w)
                    if w not in split_step['tools']:
                        split_step['tools'].append(w)

            if w in primary_methods:
                skip = False
                try:
                    if step[i-1] + " " + w in primary_methods:
                        skip = True
                        if step[i-1] + " " + w not in step_p_methods:
                            step_p_methods.append(step[i-1] + " " + w)
                        if step[i-1] + " " + w not in split_step['primary methods']:
                            split_step['primary methods'].append(step[i-1] + " " + w)
                except Exception:
                    pass
                try:
                    if w + " " + step[i+1] in primary_methods:
                        skip = True
                        if w + " " + step[i+1] not in step_p_methods:
                            step_p_methods.append(w + " " + step[i+1])
                        if w + " " + step[i+1] not in split_step['primary methods']:
                            split_step['primary methods'].append(w + " " + step[i+1])
                except Exception:
                    pass
                if not skip:
                    if w not in step_p_methods:
                        step_p_methods.append(w)
                    if w not in split_step['primary methods']:
                        split_step['primary methods'].append(w)

            if w in secondary_methods:
                skip = False
                try:
                    if step[i-1] + " " + w in secondary_methods:
                        skip = True
                        if step[i-1] + " " + w not in step_s_methods:
                            step_s_methods.append(step[i-1] + " " + w)
                        if step[i-1] + " " + w not in split_step['secondary methods']:
                            split_step['secondary methods'].append(step[i-1] + " " + w)
                except Exception:
                    pass
                try:
                    if w + " " + step[i+1] in secondary_methods:
                        skip = True
                        if w + " " + step[i+1] not in step_s_methods:
                            step_s_methods.append(w + " " + step[i+1])
                        if w + " " + step[i+1] not in split_step['secondary methods']:
                            split_step['secondary methods'].append(w + " " + step[i+1])
                except Exception:
                    pass
                if not skip:
                    if w not in step_s_methods:
                        step_s_methods.append(w)
                    if w not in split_step['secondary methods']:
                        split_step['secondary methods'].append(w)

            # if ingredients is dict
            """
            ing = next((i for i in ingredients if i["name"] == w), False)
            if ing:
                skip = False
                ing2 = next((i2 for i2 in ingredients if i2["name"] == step[i-1] + " " + w), False)
                if ing2:
                    if ing2["name"] not in [n['name'] for n in split_step['ingredients']]:
                        split_step['ingredeints'].append(ing2)
                        skip = True
                ing2 = next((i2 for i2 in ingredients if i2 == w + " " + step[i+1]), False)
                if ing2:
                    if ing2["name"] not in [n['name'] for n in split_step['ingredients']]:
                        split_step['ingredeints'].append(ing2)
                        skip = True
                if not skip:
                    if ing["name"] not in [n['name'] for n in split_step['ingredients']]:
                        split_step['ingredients'].append(ing)
            """
            # if ingredients is just a list
            if w in ingredients:
                skip = False
                try:
                    if step[i-1] + " " + w in ingredients:
                        skip = True
                        if step[i-1] + " " + w not in split_step['ingredients']:
                            split_step['ingredients'].append(step[i-1] + " " + w)
                except Exception:
                    pass
                try:
                    if w + " " + step[i+1] in ingredients:
                        skip = True
                        if w + " " + step[i+1] not in split_step['ingredients']:
                            split_step['ingredients'].append(w + " " + step[i+1])
                except Exception:
                    pass
                if not skip:
                    if w not in split_step['ingredients']:
                        split_step['ingredients'].append(w)

            if w == 'hour' or w == 'hours':
                split_step['times'].append(step[i-1] + " " + w)

            if w == 'minute' or w == 'minutes':
                split_step['times'].append(step[i-1] + " " + w)

            if w == 'second' or w == 'seconds':
                split_step['times'].append(step[i-1] + " " + w)

        split_steps.append(split_step)

    return step_tools, step_p_methods, step_s_methods, split_steps

def to_vegetarian(ings):
    # converts any recipe w/ meat to vegetarian by substituting the meat ingredeints with vegetarian ones
    replaced = vegetarian_subs
    for i, ing in enumerate(ings):
        tokens = ing['name'].lower().split(' ')
        for t in tokens:
            if t in meats or t+'s' in meats or t in seafood or t+'s' in seafood:
                ran = random.choice(replaced)
                ran['measurement'], ran['quantity'] = ing['measurement'], ing['quantity']
                ings[i] = ran
                replaced.remove(ran)
                break
    return ings

def from_vegetarian(ings):
    # check if vegetarian. if yes, converts a recipe from vegetarian to non vegetarian by adding a meat sub. if no, do nothing
    for i, ing in enumerate(ings):
        tokens = ing['name'].lower().split(' ')
        for t in tokens:
            if t in meats or t+'s' in meats or t in seafood or t+'s' in seafood:
                return ings
    ings.append(random.choice(meat_subs))
    return ings

def to_healthy(ings, steps):
    h_ing = copy.deepcopy(ings)
    for i in h_ing:
        #i2 = copy.deepcopy(i)
        if i['name'] in herbs:
            try:
                i['descriptor'].remove('dried')
            except Exception:
                pass
            if 'fresh' not in i['descriptor']:
                i['descriptor'].insert(0, 'fresh')
        if i['name'] in spices:
            if 'ground' not in i['descriptor']:
                i['descriptor'].insert(0, 'ground')
            if 'fresh' not in i['descriptor']:
                i['descriptor'].insert(0, 'fresh')
        if i['name'] in veggies:
            if 'organic' not in i['descriptor']:
                i['descriptor'].insert(0, 'organic')
        if i['name'] in l_f:
            try:
                i['descriptor'].remove('full-fat')
            except Exception:
                pass
            if 'low-fat' not in i['descriptor']:
                i['descriptor'].insert(0, 'low-fat')
        if i['name'] == 'rice':
            try:
                i['descriptor'].remove('white')
            except Exception:
                pass
            if 'brown' not in i['descriptor']:
                i['descriptor'].append('brown')
        if i['name'] in grains:
            try:
                i['descriptor'].remove('white')
            except Exception:
                pass
            if 'grain' not in i['descriptor']:
                i['descriptor'].insert(0, 'grain')
            if 'whole' not in i['descriptor']:
                i['descriptor'].insert(0, 'whole')
        if i['name'] in l_m:
            try:
                i['descriptor'].remove('fatty')
            except Exception:
                pass
            if 'lean' not in i['descriptor']:
                i['descriptor'].insert(0, 'lean')
        if i['name'] in list(h_subs.keys()):
            i['descriptor'] = h_subs[i['name']][1]
            i['name'] = h_subs[i['name']][0]
    h_stp = copy.deepcopy(steps)
    for s in h_stp:
        # dict
        """
        for i in s['ingredients']:
            if i['name'] in list(h_subs.keys()):
                i['name'] = h_subs[i['name']][0]
                i['descriptor'] = []
        """
        # list
        s['ingredients'] = [h_subs[i][0] if i in h_subs else i for i in s['ingredients']]
    return h_ing, h_stp

def to_unhealthy(ings, steps):
    u_ing = copy.deepcopy(ings)
    for i in u_ing:
        #i2 = copy.deepcopy(i)
        if i['name'] in herbs:
            try:
                i['descriptor'].remove('fresh')
            except Exception:
                pass
            if 'dried' not in i['descriptor']:
                i['descriptor'].insert(0, 'dried')
        if i['name'] in spices:
            try:
                i['descriptor'].remove('fresh')
                i['descriptor'].remove('ground')
            except Exception:
                pass
        if i['name'] in veggies:
            try:
                i['descriptor'].remove('organic')
            except Exception:
                pass
        if i['name'] in l_f:
            try:
                i['descriptor'].remove('low-fat')
            except Exception:
                pass
            if 'full-fat' not in i['descriptor']:
                i['descriptor'].insert(0, 'full-fat')
        if i['name'] == 'rice':
            try:
                i['descriptor'].remove('brown')
            except Exception:
                pass
            if 'white' not in i['descriptor']:
                i['descriptor'].append('white')
        if i['name'] in grains:
            try:
                i['descriptor'].remove('whole')
                i['descriptor'].remove('grain')
            except Exception:
                pass
            if 'white' not in i['descriptor']:
                i['descriptor'].insert(0, 'white')
        if i['name'] in l_m:
            try:
                i['descriptor'].remove('lean')
            except Exception:
                pass
            if 'fatty' not in i['descriptor']:
                i['descriptor'].insert(0, 'fatty')
        if i['name'] in list(u_subs.keys()):
            i['descriptor'] = u_subs[i['name']][1]
            i['name'] = u_subs[i['name']][0]
    u_stp = copy.deepcopy(steps)
    for s in u_stp:
        s['ingredients'] = [u_subs[i][0] if i in u_subs else i for i in s['ingredients']]
    return u_ing, u_stp

def transform_italian(ings, steps):
    #curr_i = [i['name'] for i in ings]
    i_ing = copy.deepcopy(ings)
    i_stp = copy.deepcopy(steps)
    h_switch = italian_herbs
    m_switch = italian_proteins
    p_switch = italian_pasta
    switch_dict = {}
    for i in [i2['name'] for i2 in ings]:
        if i in h_switch:
            h_switch.remove(i)
        if i in m_switch:
            m_switch.remove(i)
        if i in p_switch:
            p_switch.remove(i)
    for ing in i_ing:
        if ing['name'] in other_herbs:
            if len(h_switch) > 0:
                s = random.choice(h_switch)
                switch_dict[ing['name']] = s
                ing['name'] = s
                h_switch.remove(s)
            else:
                continue
        if ing['name'] in other_proteins:
            if len(m_switch) > 0:
                s = random.choice(m_switch)
                switch_dict[ing['name']] = s
                ing['name'] = s
                m_switch.remove(s)
            else:
                continue
        if ing['name'] in other_noodles:
            if len(p_switch) > 0:
                s = random.choice(p_switch)
                switch_dict[ing['name']] = s
                ing['name'] = s
                p_switch.remove(s)
            else:
                continue
        if ing['name'] in other_oils:
            switch_dict[ing['name']] = 'olive oil'
            ing['name'] = 'olive oil'
        if ing['name'] in other_vinegars:
            switch_dict[ing['name']] = 'balsamic vinegar'
            ing['name'] = 'balsamic vinegar'
    for st in i_stp:
        st['ingredients'] = [switch_dict[i] if i in switch_dict else i for i in st['ingredients']]
    return i_ing, i_stp


trial = 'https://www.allrecipes.com/recipe/231808/grandmas-ground-beef-casserole/'
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
result = fetchAndParseHTML(trial)
ingredients_parsed = get_ingredients(result["ingredients"])
# make ingredients in each step a dict
#s_tools, s_primary_methods, s_secondary_methods, split_steps = parseSteps(result['instructions'], ingredients_parsed)
# make ingredients in each step a list
s_tools, s_primary_methods, s_secondary_methods, split_steps = parseSteps(result['instructions'], [i['name'] for i in ingredients_parsed])
h_ing, h_st = to_healthy(ingredients_parsed, split_steps)
u_ing, u_st = to_unhealthy(ingredients_parsed, split_steps)
i_ing, i_st = transform_italian(ingredients_parsed, split_steps)
veg = to_vegetarian(ingredients_parsed)
#non_veg = from_vegetarian(ingredients_parsed)
print(veg)