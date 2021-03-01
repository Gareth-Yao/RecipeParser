from textblob import TextBlob
import textblob.download_corpora as download_corpora
import HTMLParser
import spacy
from fuzzywuzzy import fuzz
download_corpora.main()
nlp = spacy.load("en_core_web_sm")
target_preps = ["in","with","on","of"]
non_tool = ["top","meat","side","sides",'heat']
cooking_methods = ["bake","fry","roast","grill","steam","poach","simmer","broil","blanch","braise","stew"]
secondary_cooking_methods = ["cook","stir"]
def parseToolsAndCookingMethod(url):
    results = HTMLParser.fetchAndParseHTML(url)
    instructions = results["instructions"]
    ingredients_parsed = HTMLParser.get_ingredients(results["ingredients"])
    ingredients = [i['name'] for i in ingredients_parsed]
    verbs = {}
    tools = set() #Could use ingredients to filter out
    for i in instructions:
        instruction = nlp(i)
        for s in instruction.sents:
            method = ""
            secondary_method = ""
            time = 1
            for token in s:
                if token.lemma_ == 'simmer':
                    spacy.explain('dep')
                    print()
                if (token.dep_ == "ROOT" or token.dep_ == "nsubj" or token.dep_ == 'dep' or token.left_edge == token) and token.lemma_ in cooking_methods:
                    method = token.lemma_
                elif (token.dep_ == "ROOT" or token.dep_ == "nsubj") and token.lemma_ in secondary_cooking_methods:
                    secondary_method = token.lemma_
                elif token.pos_ == "NOUN" and (token.dep_ == 'dobj' or token.head.text in target_preps) and token.text not in non_tool and token.ent_type_ == '':
                    full_tool = ""
                    for left in token.lefts:
                        if left.text != 'the':
                            full_tool += left.text + " "
                    full_tool += token.text
                    right = ""
                    for r in token.rights:
                        right += r.text + " "
                    right = right[:-1]
                    if 'of' in right or 'in' in right or any(len(set(ing.split()).intersection(full_tool.split())) > 0 for ing in ingredients):
                        continue
                    tools.add(full_tool)
                elif token.pos_ == "NUM" and token.ent_type_ == "TIME":
                    if "second" in token.head.text:
                        time += int(token.text) / 60
                    elif "minute" in token.head.text:
                        time += int(token.text)
                    else:
                        time += int(token.text) * 60
            if method != "":
                verbs[method] = verbs.get(method, 0) + time
            elif secondary_method != "":
                verbs[secondary_method] = verbs.get(secondary_method, 0) + 1
    ans = (max(verbs.items(), key=lambda key : key[1])[0], tools)
    return ans


print(parseToolsAndCookingMethod("https://www.allrecipes.com/recipe/254341/easy-paleo-chicken-marsala/"))
