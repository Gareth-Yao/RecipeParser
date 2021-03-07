import HTMLParser
import spacy
from fractions import Fraction
from fuzzywuzzy import fuzz
from word2number import w2n

nlp = spacy.load("en_core_web_sm")
target_preps = ["in","with","on","of"]
non_tool = ["top","meat","side","sides",'heat']
cooking_methods = ["bake","fry","roast","grill","steam","poach","simmer","broil","blanch","braise","stew"]
secondary_cooking_methods = ["cook","stir"]


def parseToolsAndCookingMethod(url, replaceEmptyMainMethod = True):
    results = HTMLParser.fetchAndParseHTML(url)
    instructions = results["instructions"]
    ingredients_parsed = HTMLParser.get_ingredients(results["ingredients"])
    ingredients = set([i['name'] for i in ingredients_parsed])
    steps = []
    verbs = {}
    secondary_verbs = {}
    tools = set()
    for i in instructions:
        instruction = nlp(i)
        for s in instruction.sents:
            method = []
            secondary_method = []
            time = 1
            step = {}
            step['secondary_action'] = []
            step['action'] = []
            step['instruction'] = s.text
            step['tools'] = []
            step['ingredients'] = {}
            for token in s:
                if token.pos_ == "NOUN":
                    full_tool = ""
                    for left in token.lefts:
                        if left.text != 'the':
                            full_tool += left.text_with_ws
                    full_tool += token.text_with_ws
                    full_tool = full_tool[:-1] if len(full_tool) != 0 and not full_tool[-1].isalnum() else full_tool
                    for ing in ingredients:
                        if ing in s.text:
                            step['ingredients'].update({ing: ing})
                            break
                        #len(set(ing.split()).intersection(full_tool.split())) > 0 and not (any(fuzz.token_sort_ratio(i,full_tool) > 80 for i in step['ingredients'].keys())) and ing not in step['ingredients'].values()
                        elif fuzz.token_set_ratio(ing, full_tool) > 80:
                            step['ingredients'].update({full_tool : ing})
                            break

                if (token.dep_ == "ROOT" or token.dep_ == "nsubj" or token.dep_ == 'dep' or token.left_edge == token) and token.lemma_ in cooking_methods:
                    method.append(token.lemma_)
                elif (token.dep_ == "ROOT" or token.dep_ == "nsubj") and token.lemma_ in secondary_cooking_methods:
                    secondary_method.append(token.lemma_)
                elif token.pos_ == "NOUN" and (token.dep_ == 'dobj' or token.head.text in target_preps) and token.text not in non_tool and token.ent_type_ == '':
                    full_tool = ""
                    for left in token.lefts:
                        if left.text != 'the':
                            full_tool += left.text_with_ws
                    full_tool += token.text_with_ws
                    full_tool = full_tool[:-1] if len(full_tool) != 0 and not full_tool[-1].isalnum() else full_tool
                    right = ""
                    for r in token.rights:
                        right += r.text_with_ws
                    right = right[:-1] if len(right) != 0 and not right[-1].isalnum() else right
                    if 'of' in right or 'in' in right or any(len(set(ing.split()).intersection(full_tool.split())) > 0 for ing in ingredients):
                        continue
                    tools.add(full_tool)
                    step['tools'].append(full_tool)
                elif token.pos_ == "NUM" and token.ent_type_ == "TIME":
                    try:
                        t = w2n.word_to_num(token.text)
                        if "second" in token.head.text:
                            time +=  Fraction(t) / 60
                        elif "minute" in token.head.text:
                            time +=  Fraction(t)
                        else:
                            time += Fraction(t) * 60
                    except ValueError:
                        if "second" in token.head.text:
                            time +=  Fraction(token.text) / 60
                        elif "minute" in token.head.text:
                            time +=  Fraction(token.text)
                        else:
                            time += Fraction(token.text) * 60


            if len(method) != 0:
                for m in method:
                    verbs[m] = verbs.get(m, 0) + time
                step['action'] = method
            if len(secondary_method) != 0:
                for m in secondary_method:
                    secondary_verbs[m] = secondary_verbs.get(m, 0) + time
                step['secondary_action'] = secondary_method

            steps.append(step)
    secondary_cooking_method = max(secondary_verbs.items(), key=lambda key : key[1])[0] if len(secondary_verbs.keys()) != 0 else ''
    if replaceEmptyMainMethod:
        main_cooking_method = max(verbs.items(), key=lambda key: key[1])[0] if len(verbs.keys()) != 0 else secondary_cooking_method
    else:
        main_cooking_method = max(verbs.items(), key=lambda key: key[1])[0] if len(verbs.keys()) != 0 else ''
    ans = {'main_cooking_method' : main_cooking_method,
           'secondary_cooking_method' : secondary_cooking_method,
           'ingredients' : ingredients_parsed,
           'tools' : tools,
           'steps' : steps}
    print(ans)
    return ans




# steps = parseToolsAndCookingMethod("https://www.allrecipes.com/recipe/254341/easy-paleo-chicken-marsala/")
