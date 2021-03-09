import sys
import HTMLParser
import InstructionParser
import Transformation

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
        user = input("Enter corresponding number for desired info:\n1:Ingredients and Steps\n2:Tools\n3:Cooking Methods\n4:Transform to vegetarian\n5:Transform from vegetarian\n6:Transform to healthy\n7:Transform to unhealthy\n8:Transform to Italian-style\n9:Enter a new recipe\n'quit':Quit\n")
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
        elif int(user) == 3:
            print_methods = "Methods:\n"
            print_methods += tools_instructions['main_cooking_method'] + ' (main), '
            print_methods += tools_instructions['secondary_cooking_method'] + ' (secondary)\n'
            print(print_methods)
        elif int(user) == 4:
            if HTMLParser.to_vegetarian(HTMLParser.get_ingredients(results["ingredients"])) == {}:
                print("Recipe is already vegetarian!")
            else:
                to_veg = Transformation.toVeggie(tools_instructions)
                new_ing = HTMLParser.format_ings(to_veg['ingredients'])
                print_ing = "Ingredients:\n"
                for ing in new_ing:
                    print_ing += ing + "\n"
                print(print_ing)
        elif int(user) == 5:
            if HTMLParser.from_vegetarian(HTMLParser.get_ingredients(results["ingredients"])) == {}:
                print("Recipe isn't vegetarian!")
            else:
                from_veg = Transformation.fromVeggie(tools_instructions)
                new_ing = HTMLParser.format_ings(from_veg['ingredients'])
                print_ing = "Ingredients:\n"
                for ing in new_ing:
                    print_ing += ing + "\n"
                print(print_ing)
        elif int(user) == 6:
            healthy = HTMLParser.to_healthy(HTMLParser.get_ingredients(results["ingredients"]))
            healthy = HTMLParser.format_ings(healthy)
            print_ing = "Ingredients:\n"
            for ing in healthy:
                print_ing += ing + "\n"
            print(print_ing)
        elif int(user) == 7:
            healthy = HTMLParser.to_unhealthy(HTMLParser.get_ingredients(results["ingredients"]))
            healthy = HTMLParser.format_ings(healthy)
            print_ing = "Ingredients:\n"
            for ing in healthy:
                print_ing += ing + "\n"
            print(print_ing)
        elif int(user) == 8:
            italian = Transformation.toItalian(results)
            res = HTMLParser.format_ings(italian['ingredients'])
            print_ing = "Ingredients:\n"
            for ing in res:
                print_ing += ing + "\n"
            print(print_ing)
        elif int(user) == 9:
            urlinput()
        else:
            print("Hello")
    print(print_ing)

    

if __name__ == '__main__':
    urlinput()