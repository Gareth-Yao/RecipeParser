import sys
import HTMLParser
import InstructionParser
import Transformation
from fuzzywuzzy import fuzz
import time
import spacy
from text_to_num import alpha2digit
from word2number import w2n
from fractions import Fraction
from InstructionParser import kitchen_tools, cooking_methods, secondary_methods
nlp = spacy.load("en_core_web_sm")


questions = [
    'how do i', #search for youtube
    'how to', #search for youtube
    'how long do i', #time
    'when do i',  #which step
    'the ingredients', #show ingredients
    'what is', #Google
    'what are', #Google
    "what's", #Google
    "what're", #Google
    'where can i', #Google
    'where are', #Google
    'where is', #Google
    'thanks', #possible next step
    'yes',
    'sure',
    'ok',
    'no',
    'previous step',
    'next step',
    'go to step', #go to a certain step
    'jump to step',
    'bring me to step',
    'take me to step',
    'show me step',
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
            user = input("I've found the recipe for \"" + results["name"] + "\".\nMAIN MENU:\n\n[1] look at the ingredients\n[2] look at the steps\n[3] enter another recipe\n[4] quit the conversation?\n\n")
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
    print("CONVERSATION MODE")
    step = 0
    #todo: implement conversation parser that will start after either ingredients or the first step is requested
    while True:
        user = input("What next? ")
        prompt = max(questions, key=lambda x : fuzz.token_sort_ratio(user, x))
        score1 = fuzz.token_sort_ratio(user, 'how do i')
        score2 = fuzz.token_sort_ratio(user, 'how long do i')
        if user == '':
            pass
        elif 'another recipe' in prompt or user == '3':
            user2 = input('Would you like to enter another recipe? ')
            prompt = max(questions, key=lambda x: fuzz.token_sort_ratio(user2, x))
            if 'yes' in prompt or 'sure' in prompt or 'ok' in prompt:
                urlinput(False)
        elif 'quit' in prompt or user == '4':
            print('Have a great meal. Goodbye.')
            sys.exit()
        elif 'how do i' in prompt or 'how to' in prompt:
            vague = True
            q_ = False
            methods = cooking_methods + secondary_methods
            for m in methods:
                if m in user:
                    query = 'https://www.youtube.com/results?search_query=' + user.replace(' ', '+')
                    vague = False
                    q_ = True
                    break
            if vague:
                if len(tools_instructions['steps'][step]['action']) > 0:
                    query = 'https://www.youtube.com/results?search_query=how+to+' + tools_instructions['steps'][step]['action'][0].replace(' ', '+')
                    q_ = True
                elif  len(tools_instructions['steps'][step]['secondary_action']) > 0:
                    query = 'https://www.youtube.com/results?search_query=how+to+' + tools_instructions['steps'][step]['secondary_action'][0].replace(' ', '+')
                    q_ = True
            if q_:
                print('Here is the YouTube link for your question: ' + query)
            else:
                print("Sorry, I'm not sure. Can you be more specific?")
        elif 'what' in prompt:
            if 'this' in user or 'that' in user:
                try:
                    query = 'https://www.google.com/search?q=what+is+' + tools_instructions['steps'][step]['tools'][0].replace(' ', '+')
                    print('Here is a link to Google results for your question: ' + query)
                except Exception:
                    print("Sorry, I'm not sure. Can you be more specific?")
            elif 'these' in user or 'those' in user:
                try:
                    query = 'https://www.google.com/search?q=what+are+' + [i['name'] for i in tools_instructions['steps'][step]['ingredients']][0].replace(' ', '+')
                    print('Here is a link to Google results for your question: ' + query)
                except Exception:
                    print("Sorry, I'm not sure. Can you be more specific?")
            else:
                query = user.replace(' ', '+')
                print('Here is a link to Google results for your question: ' + "https://www.google.com/search?q=" + query)
        elif 'where' in prompt or 'who' in user.split() or 'which' in user.split():
            query = user.replace(' ', '+')
            print('Here is a link to Google results for your question: ' + "https://www.google.com/search?q=" + query)
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
            user2 = input('Do you want to go back to the previous step? ')
            prompt = max(questions, key=lambda x: fuzz.token_sort_ratio(user2, x))
            if 'yes' in prompt or 'sure' in prompt or 'ok' in prompt:
                step -= 1
                print('The previous step is:')
                print(tools_instructions['steps'][step]['instruction'])
        elif 'go to step' in prompt or 'jump to step' in prompt or 'bring me to step' in prompt or 'take me to step' in prompt or 'show me step' in prompt:
            user = alpha2digit(user, lang='en')
            user = nlp(user)
            target_step = 1
            for token in user:
                if token.pos_ == 'NUM' or token.ent_type_ == 'ORDINAL':
                    target_step = int(token.text if token.pos_ == 'NUM' else token.text[:-2])
            user2 = input('Do you want to go to step ' + str(target_step) + "? ")
            prompt = max(questions, key=lambda x: fuzz.token_sort_ratio(user2, x))
            if 'yes' in prompt or 'sure' in prompt or 'ok' in prompt:
                try:
                    valid_step = tools_instructions['steps'][target_step-1]['instruction']
                    step = target_step-1
                    print("Step " + str(target_step) + ' is:')
                    print(valid_step)
                except:
                    print('Please enter valid step number.')
        elif step < len(tools_instructions['steps']):
            user2 = input('Do you want to proceed to the next step? ')
            prompt = max(questions, key=lambda x: fuzz.token_sort_ratio(user2, x))
            if 'yes' in prompt or 'sure' in prompt or 'ok' in prompt:
                step += 1
                print('The next step is:')
                print(tools_instructions['steps'][step]['instruction'])
            elif 'no' in prompt:
                user3 = input('Do you want to go back to the previous step? ')
                prompt = max(questions, key=lambda x: fuzz.token_sort_ratio(user3, x))
                if 'yes' in prompt or 'sure' in prompt or 'ok' in prompt:
                    step -= 1
                    print('The previous step is:')
                    print(tools_instructions['steps'][step]['instruction'])
        else:
            user2 = input('That is the end of the recipe. Would you like to enter another recipe? ')
            prompt = max(questions, key=lambda x: fuzz.token_sort_ratio(user2, x))
            if 'yes' in prompt or 'sure' in prompt or 'ok' in prompt:
                urlinput(False)





    

if __name__ == '__main__':
    urlinput(True)