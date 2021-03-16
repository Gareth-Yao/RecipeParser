import sys
import HTMLParser
import InstructionParser
import Transformation
import time

def urlinput(first):
    if first: #detects if it's the first time looping
        url = input("Hi, my name is Eugene, and I'll be your virtual assistant today. Please enter an All-Recipe url to get started or type 'quit' to exit. \n")
    else:
        url = input("Sure, let's look at another recipe. Please enter an All-Recipe url or type 'quit' to exit.\n")
    valid = False
    while valid is False:
        if url == "quit":
            print("Goodbye!")
            time.sleep(2) #pause to let the print message display before quitting
            sys.exit(0)
        results = HTMLParser.fetchAndParseHTML(url)
        if results == {}:
            url = input("I'm sorry, it looks like the url is invalid. Please try another url or type 'quit' to exit recipe parser: \n")
        else:
            valid = True
    parserUI(results)
def parserUI(results):
    ingredients = HTMLParser.format_ings(HTMLParser.get_ingredients(results["ingredients"]))
    tools_instructions = InstructionParser.parseToolsAndCookingMethod(results)
    active = True
    first = True
    while active is True:
        if first:
            user = input("I've found the recipe for \"" + results["name"] + "\". Would you like to: [1] look at the ingredients, [2] look at the steps, [3] enter another recipe, or [4] quit the conversation? \n")
        else:
            user = input("I'm sorry, I couldn't process that input. Would you like to: [1] look at the ingredients, [2] look at the steps, [3] enter another recipe, or [4] quit the conversation? \n")
        if user == '1':
            print_ing = "Here is the list of ingredients:\n"
            for ing in ingredients:
                print_ing += ing + "\n"
            print(print_ing)
            conversation(results)
            active = False
        elif user == '2':
            print("The first step is: " + tools_instructions["steps"][0]["instruction"] + "\n")
            conversation(results)
            active = False
        elif user == '3':
            urlinput(False)
            active = False
        elif user == '4':
            print("Goodbye!")
            time.sleep(2)
            sys.exit(0)
        else:
            first = False
def conversation(results):
    print("What next?")
    #todo: implement conversation parser that will start after either ingredients or the first step is requested            

    

if __name__ == '__main__':
    urlinput(True)