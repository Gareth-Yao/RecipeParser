import sys
import HTMLParser
import InstructionParser
import Transformation
from textblob import TextBlob
from fuzzywuzzy import fuzz
import time
import spacy
from text_to_num import alpha2digit
from word2number import w2n
from fractions import Fraction
nlp = spacy.load("en_core_web_sm")


questions = [
    'how do i', #search for youtube
    'how long do i', #time
    'when do i',  #which step
    'the ingredients', #show ingredients
    'what is', #Google
    'where can i', #Google
    'thanks', #possible next step
    'yes',
    'no',
    'previous step',
    'next step',
    'go to step', #go to a certain step
    "another recipe",
    'quit'
]
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
            conversation(tools_instructions, ingredients)
            active = False
        elif user == '2':
            print("The first step is: " + tools_instructions["steps"][0]["instruction"] + "\n")
            conversation(tools_instructions, ingredients)
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
def conversation(tools_instructions,ingredients):
    step = 0
    #todo: implement conversation parser that will start after either ingredients or the first step is requested
    while True:
        user = input("What next?")
        prompt = max(questions, key=lambda x : fuzz.token_sort_ratio(user, x))
        score1 = fuzz.token_sort_ratio(user, 'how do i')
        score2 = fuzz.token_sort_ratio(user, 'how long do i')
        if 'how do i' in prompt:
            query = 'https://www.youtube.com/results?search_query=' + user.replace(' ', '+')
            print('Here is the YouTube link for your question: ' + query)
        elif 'what' in prompt or 'where' in prompt or 'who' in user.split() or 'which' in user.split():
            query = user.replace(' ', '+')
            print('Here is a link to Google results for your question:' + "https://www.google.com/search?q=" + query)
        elif 'when' in prompt:
            temp = nlp(user)
            verb_phrase = ""
            noun_phrase = ""
            for token in temp:
                if token.pos_ == 'VERB':
                    verb_phrase += token.text
                    for r in token.rights:
                        if r.pos_ == 'NOUN':
                            noun_phrase += r.text_with_ws
                    break
            noun_phrase = noun_phrase[:-1] if noun_phrase[-1] == ' ' else noun_phrase
            target_step = -1
            for i in range(0,len(tools_instructions['steps'])):
                if verb_phrase in tools_instructions['steps'][i]['instruction'] and noun_phrase in tools_instructions['steps'][i]['ingredients'].keys():
                    target_step = i
            if target_step != -1:
                print('In step ' + str(target_step + 1))
            else:
                print('I cannot find relevant information in the recipe, sorry.')
        elif 'how long' in prompt:
            temp = nlp(user)
            verb_phrase = ""
            noun_phrase = ""
            for token in temp:
                if token.pos_ == 'VERB':
                    verb_phrase += token.text
                    for r in token.rights:
                        if r.pos_ == 'NOUN':
                            noun_phrase += r.text_with_ws
                    break
            noun_phrase = noun_phrase[:-1] if noun_phrase[-1] == ' ' else noun_phrase
            time = 0
            for i in range(0,len(tools_instructions['steps'])):
                if verb_phrase in tools_instructions['steps'][i]['instruction'] and noun_phrase in tools_instructions['steps'][i]['ingredients'].keys():
                    temp2 = nlp(tools_instructions['steps'][i]['instruction'])
                    for token in temp2:
                        if token.ent_type_ == 'TIME' and token.pos_ == "NUM":
                            try:
                                t = w2n.word_to_num(token.text)
                                if "second" in token.head.text:
                                    time += Fraction(t) / 60
                                elif "minute" in token.head.text:
                                    time += Fraction(t)
                                else:
                                    time += Fraction(t) * 60
                            except ValueError:
                                if "second" in token.head.text:
                                    time += Fraction(token.text) / 60
                                elif "minute" in token.head.text:
                                    time += Fraction(token.text)
                                else:
                                    time += Fraction(token.text) * 60
                    break
            if time != 0:
                print('For ' + str(time) + " minutes")
            else:
                print('It is not specified in the recipe. Sorry.')
        elif 'ingredients' in prompt:
            print_ing = "Here is the list of ingredients:\n"
            for ing in ingredients:
                print_ing += ing + "\n"
            print(print_ing)
        elif 'previous step' in prompt or 'go back' in user:
            if step == 0:
                print('You are at the first step.')
                continue
            user2 = input('Do you want to go back to the previous step?')
            prompt = max(questions, key=lambda x: fuzz.token_sort_ratio(user2, x))
            if 'yes' in prompt:
                step -= 1
                print('The previous step is:')
                print(tools_instructions['steps'][step]['instruction'])
        elif 'go to step' in prompt:
            user = alpha2digit(user, lang='en')
            user = nlp(user)
            target_step = 1
            for token in user:
                if token.pos_ == 'NUM':
                    target_step = int(token.text)
            user2 = input('Do you want to go to step ' + str(target_step) + "?")
            prompt = max(questions, key=lambda x: fuzz.token_sort_ratio(user2, x))
            if 'yes' in prompt:
                print("Step " + str(target_step) + ' is:')
                step = target_step - 1
                print(tools_instructions['steps'][step]['instruction'])
        elif 'another recipe' in prompt:
            user2 = input('Would you like to enter another recipe?')
            prompt = max(questions, key=lambda x: fuzz.token_sort_ratio(user2, x))
            if 'yes' in prompt:
                urlinput(False)
        elif 'quit' in prompt:
            print('Have a great meal. Goodbye.')
            sys.exit()
        elif step < len(tools_instructions['steps']):
            user2 = input('Do you want to proceed to the next step?')
            prompt = max(questions, key=lambda x: fuzz.token_sort_ratio(user2, x))
            if 'yes' in prompt:
                step += 1
                print('The next step is:')
                print(tools_instructions['steps'][step]['instruction'])
        else:
            user2 = input('That is the end of the recipe. Would you like to enter another recipe?')
            prompt = max(questions, key=lambda x: fuzz.token_sort_ratio(user2, x))
            if 'yes' in prompt:
                urlinput(False)





    

if __name__ == '__main__':
    urlinput(True)