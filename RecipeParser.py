import sys
import HTMLParser
import InstructionParser
import Transformation
# import keyboard
def RecipeParser(url, toVegetarian, toHealthy, toItalian):
    results = HTMLParser.fetchAndParseHTML(url)
    if len(results) == 0:
        print("Please Provide a valid Recipe URL")
        sys.exit()
    steps = {}
    if toItalian:
        steps = Transformation.toItalian(results)
    else:
        steps = InstructionParser.parseToolsAndCookingMethod(results)
    if toVegetarian:
        steps = Transformation.toVeggie(steps)
    else:
        steps = Transformation.fromVeggie(steps)
    if toHealthy:
        steps['ingredients'] = HTMLParser.to_healthy(steps['ingredients'])
    else:
        steps['ingredients'] = HTMLParser.to_unhealthy(steps['ingredients'])
    print("This Recipe Parse will transform", "\"" + results['name'] + "\"", "to:", "Italian" if toItalian else "", "Vegetarian" if toVegetarian else "Non-Vegetarian", "and", "Healthy" if toHealthy else "Unhealthy")
    res = HTMLParser.format_ings(steps['ingredients'])
    print("The Ingredients are: ")
    for i in res:
        print(i)
    print()
    print("The Tools are:")
    for t in steps['tools']:
        print(t)
    print()
    print("The Primary Cooking Method is:")
    print(steps['main_cooking_method'])
    print()
    print("The Secondary Cooking Methods Are:")
    print(steps['secondary_cooking_methods'])
    print()
    print("The Steps Are:")
    counter = 1

    for s in steps['steps']:
        print(str(counter) + ".", s['instruction'])
        counter += 1

    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please Provide a Recipe URL")
        sys.exit()
    url = sys.argv[1]
    toVegetarian = True
    toHealthy = True
    toItalian = True
    if len(sys.argv) > 2:
        toVegetarian = sys.argv[2].lower() == 'true'
    if len(sys.argv) > 3:
        toHealthy = sys.argv[3].lower() == 'true'
    if len(sys.argv) > 4:
        toItalian = sys.argv[4].lower() == 'true'

    RecipeParser(url, toVegetarian, toHealthy, toItalian)