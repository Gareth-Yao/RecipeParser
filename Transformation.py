import InstructionParser
import HTMLParser
from ingredients import *
import json
import random
import os
import sys
import spacy
nlp = spacy.load("en_core_web_sm")
url = "https://www.allrecipes.com/recipe/213654/chicken-asparagus-and-mushroom-skillet/"
def toVeggie(steps):
    replacements = HTMLParser.to_vegetarian(steps['ingredients'])
    new_ingredients = []
    for i in steps['ingredients']:
        if i['name'] in replacements.keys():
            new_ingredients.append(replacements[i['name']])
        else:
            new_ingredients.append(i)
    steps['ingredients'] = new_ingredients

    for s in steps['steps']:
        for i in s['ingredients'].keys():
            if s['ingredients'][i] in replacements.keys():
                s['instruction'] = s['instruction'].replace(i, replacements[s['ingredients'][i]]['name'])
    return steps

def fromVeggie(steps):
    replacements = HTMLParser.from_vegetarian(steps['ingredients'])
    new_ingredients = []
    for i in steps['ingredients']:
        if i['name'] in replacements.keys():
            new_ingredients.append(replacements[i['name']])
        else:
            new_ingredients.append(i)
    steps['ingredients'] = new_ingredients
    for s in steps['steps']:
        for i in s['ingredients'].keys():
            if s['ingredients'][i] in replacements.keys():
                s['instruction'] = s['instruction'].replace(i, replacements[s['ingredients'][i]]['name'])
    return steps

def toItalian(url):
    if not os.path.exists('Italian_Ingredients.json'):
        print("Run StyleOfCuisine.py to generate italian cuisine ingredients first")
        sys.exit()
    with open('Italian_Ingredients.json') as f:
        italian = json.load(f)
    steps = InstructionParser.parseToolsAndCookingMethod(url)
    new_ingredients = []
    protein_subs = list(italian['protein'].keys())
    vegetable_subs = list(italian['vegetables'].keys())
    spice_subs = list(italian['spices'].keys())

    rep_map = {}
    for ing in steps['ingredients']:
        for token in ing['name'].lower().split():
            if token in meats or token in seafood and ing['name'] not in protein_subs:
                rep = random.choice(protein_subs)
                rep_map[ing['name']] = rep
                if rep in [i['name'] for i in new_ingredients]:
                    for i in new_ingredients:
                        if i['name'] == rep:
                            i['quantity'] += ing['quantity']
                        break
                else:
                    ing['name'] = rep
                protein_subs.remove(rep)
                break
            elif token in vegetables and ing['name'] not in vegetable_subs:
                rep = random.choice(vegetable_subs)
                rep_map[ing['name']] = rep
                if rep in [i['name'] for i in new_ingredients]:
                    for i in new_ingredients:
                        if i['name'] == rep:
                            i['quantity'] += ing['quantity']
                        break
                else:
                    ing['name'] = rep
                vegetable_subs.remove(rep)
                break
            elif token in herbs_spices and ing['name'] not in spice_subs:
                rep = random.choice(spice_subs)
                rep_map[ing['name']] = rep
                if rep in [i['name'] for i in new_ingredients]:
                    for i in new_ingredients:
                        if i['name'] == rep:
                            i['quantity'] += ing['quantity']
                        break
                else:
                    ing['name'] = rep
                spice_subs.remove(rep)
                break
        new_ingredients.append(ing)


    method_subs = list(italian['cooking methods'].keys())
    method_subs = method_subs[1:]

    for s in steps['steps']:
        for i in s['ingredients'].keys():
            if s['ingredients'][i] in rep_map.keys():
                s['instruction'] = s['instruction'].replace(i, rep_map[s['ingredients'][i]])
        new_actions = []
        for a in s['action']:
            if a not in method_subs:
                rep = rep_map.get(a, random.choice(method_subs))
                rep_map[a] = rep
                new_actions.append(rep)
                ins = nlp(s['instruction'])
                for token in ins:
                    if token.lemma_ == a:
                        suffix = ''
                        if token.text.endswith('ing'):
                                suffix = 'ing'
                        elif token.text.endswith('ed'):
                                suffix = 'ed'
                        if suffix != '':
                            if rep[-2] in ['a','e','i','o','u']:
                                rep += rep[-1]
                            elif rep[-1] == 'e':
                                rep = rep[:-1]
                            elif rep == 'fry' and suffix == 'ed':
                                rep = 'fri'
                        s['instruction'] = s['instruction'].replace(token.text, rep + suffix)
            else:
                new_actions.append(a)
        s['action'] = new_actions

    steps['main_cooking_method'] = rep_map.get(steps['main_cooking_method'], steps['main_cooking_method'])
    steps['ingredients'] = new_ingredients

    return steps