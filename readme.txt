In a new virtual environment, pip install -r requirements.txt
Run
    RecipeParser.py {recipe_url} {to_vegetarian} {to_healthy} {to_italian}

The latter three arguments are string/boolean
The default is all three are true. If to_vegetarian or to_healthy are false, the program will transform the recipe
to non-vegetarian and non-healthy. to_italian being false won't do anything.
