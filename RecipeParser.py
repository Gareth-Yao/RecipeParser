import sys
import HTMLParser
import InstructionParser
import Transformation
def RecipeParser(url, toVegetarian, toHealthy, toItalian):
    results = HTMLParser.fetchAndParseHTML(url)
    steps = {}
    if toItalian:
        steps = Transformation.toItalian(results)
    else:
        steps = InstructionParser.parseToolsAndCookingMethod(results)
    if toVegetarian:
        steps = Transformation.toVeggie(steps)
    else:
        steps = Transformation.fromVeggie(steps)

    print("This Recipe Parse will transform", "\"" + results['name'] + "\"", "to:", "Italian" if toItalian else "", "Vegetarian" if toVegetarian else "Non-Vegetarian", "and", "Healthy" if toHealthy else "Non-Healthy")
    res = HTMLParser.format_ings(steps['ingredients'])
    print("The Ingredients are: ")
    for i in res:
        print(i)
    print()
    print("The Steps Are:")
    counter = 1
    for s in steps['steps']:
        print(str(counter) + ".", s['instruction'])
        counter += 1

if __name__ == '__main__':
    url = sys.argv[1]
    toVegetarian = True
    toHealthy = True
    toItalian = True
    if len(sys.argv) > 2:
        toVegetarian = sys.argv[2].lower() == 'True'
    if len(sys.argv) > 3:
        toHealthy = sys.argv[3].lower() == 'True'
    if len(sys.argv) > 4:
        toItalian = sys.argv[4].lower() == 'True'

    RecipeParser(url, toVegetarian, toHealthy, toItalian)