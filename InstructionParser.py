from textblob import TextBlob
import textblob.download_corpora as download_corpora
import HTMLParser
import spacy
download_corpora.main()
nlp = spacy.load("en_core_web_sm")
target_preps = ["in","with","on"]
cooking_methods = ["cook","bake","fry","roast","grill","steam","poach","simmer","broil","blanch","braise","stew"]
def parseToolsAndCookingMethod(url):
    instructions = HTMLParser.fetchAndParseHTML(url)["instructions"]
    verbs = {}
    tools = set() #Could use ingredients to filter out
    for i in instructions:
        instruction = nlp(i)
        for s in instruction.sents:
            method = ""
            time = 1
            for token in s:
                if (token.dep_ == "ROOT" or token.dep_ == "nsubj") and token.lemma_ in cooking_methods:
                    method = token.lemma_
                elif token.pos_ == "NOUN" and token.head.text in target_preps:
                    tools.add(token.text)
                elif token.pos_ == "NUM" and token.ent_type_ == "TIME":
                    if "second" in token.head.text:
                        time += int(token.text) / 60
                    elif "minute" in token.head.text:
                        time += int(token.text)
                    else:
                        time += int(token.text) * 60
            if method != "":
                verbs[method] = verbs.get(method, 0) + time
    ans = (max(verbs.items(), key=lambda key : key[1])[0], tools)
    return ans


x = nlp("Bake in the preheated oven for 1 hour")
for s in x.sents:
    for token in s:
        print(x)
parseToolsAndCookingMethod("https://www.allrecipes.com/recipe/16348/baked-pork-chops-i/")
