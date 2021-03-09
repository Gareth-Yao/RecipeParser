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
            url = input("Invalid. Please try another url or type 'quit' to exit recipe parser: \n")
        else:
            valid = True
    parserUI(results)
def parserUI(results):
    ingredients = HTMLParser.format_ings(HTMLParser.get_ingredients(results["ingredients"]))
    tools_instructions = InstructionParser.parseToolsAndCookingMethod(results)
    active = True
    while active:
        user = input("Enter corresponding number for desired info:\n1:Ingredients and Steps\n2:Tools\n3:Cooking Methods\n4:Transform to vegetarian\n5:Transform from vegetarian\n6:Transform to healthy\n7:Transform from healthy\n8:Transform to Italian-style\n9:Enter a new recipe\n")
        if int(user) == 1:
            print_ing = "Ingredients:\n"
            for ing in ingredients:
                print_ing += ing + "\n"
            print_steps = "Steps:\n"
            for step in tools_instructions['steps']:
                print_steps += step['instruction'] + "\n"
            print(print_ing+print_steps)
        elif int(user) == 2:
            print_tools = "Tools:\n"
            for tools in tools_instructions['tools']:
                print_tools += tools + "\n"
            print(print_tools)
        else:
            print("Hello")
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