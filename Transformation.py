import InstructionParser
import HTMLParser

url = "https://www.allrecipes.com/recipe/254341/easy-paleo-chicken-marsala/"
def toVeggie(url):
    steps = InstructionParser.parseToolsAndCookingMethod(url)
    replacements = HTMLParser.to_vegetarian(steps['ingredients'])
    steps = steps['steps']
    for s in steps:
        for i in s['ingredients'].keys():
            if s['ingredients'][i] in replacements.keys():
                s['instruction'] = s['instruction'].replace(i, replacements[s['ingredients'][i]]['name'])
    print(replacements)

def fromVeggie(url):
    pass

def toItalian(url):
    pass
toVeggie(url)