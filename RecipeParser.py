import sys
import HTMLParser
import InstructionParser
import Transformation
import keyboard
# def RecipeParser(url, toVegetarian, toHealthy, toItalian):
#     results = HTMLParser.fetchAndParseHTML(url)
#     steps = {}
#     if toItalian:
#         steps = Transformation.toItalian(results)
#     else:
#         steps = InstructionParser.parseToolsAndCookingMethod(results)
#     if toVegetarian:
#         steps = Transformation.toVeggie(steps)
#     else:
#         steps = Transformation.fromVeggie(steps)

#     print("This Recipe Parse will transform", "\"" + results['name'] + "\"", "to:", "Italian" if toItalian else "", "Vegetarian" if toVegetarian else "Non-Vegetarian", "and", "Healthy" if toHealthy else "Non-Healthy")
#     res = HTMLParser.format_ings(steps['ingredients'])
#     print("The Ingredients are: ")
#     for i in res:
#         print(i)
#     print()
#     print("The Steps Are:")
#     counter = 1
#     for s in steps['steps']:
#         print(str(counter) + ".", s['instruction'])
#         counter += 1
def urlinput():
    url = input("Enter recipe url or type 'quit' to exit recipe parser: \n")
    valid = False
    while valid is False:
        if url == "quit":
            sys.exit(0)
        results = HTMLParser.fetchAndParseHTML(url)
        if results == {}:
            url = input("Invalid. Please try another url or type 'quit' to exit recipe parser: ")
        else:
            valid = True
    parserUI(results)
def parserUI(results):
    ingredients = HTMLParser.get_ingredients(results["ingredients"])
    print_ing = "Ingredients:\n"
    for ing in ingredients:
        print_ing += ing + "\n"
    tools_instructions = InstructionParser.parseToolsAndCookingMethod(results)
    active = True
    while active:
        user = input("Enter corresponding number for desired info:\n1: Ingredients and Steps\n2:Tools\n3:Cooking Methods\n4:Transform to vegetarian\n5:Transform from vegetarian")
    
    print(print_ing)

    

if __name__ == '__main__':
    urlinput()

    # url = sys.argv[1]
    # toVegetarian = True
    # toHealthy = True
    # toItalian = True
    # if len(sys.argv) > 2:
    #     toVegetarian = sys.argv[2].lower() == 'True'
    # if len(sys.argv) > 3:
    #     toHealthy = sys.argv[3].lower() == 'True'
    # if len(sys.argv) > 4:
    #     toItalian = sys.argv[4].lower() == 'True'

    # RecipeParser(url, toVegetarian, toHealthy, toItalian)