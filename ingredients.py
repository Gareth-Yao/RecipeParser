meats = [
    'pork',
    'poultry',
    'seafood',
    'liver',
    'chicken',
    'beef',
    'lamb',
    'venison',
    'buffalo',
    'bear',
    'turtle',
    'goat',
    'deer',
    'turkey',
    'goose',
    'sausage',
    'ostrich',
    'kangaroo',
    'duck',
    'foie gras',
    'rabbit',
    'bison',
    'bear',
    'heart',
    'calf',
    'calves',
    'horse',
    'caribou',
    'marrow',
    'bone',
    'tripe',
    'squirrel',
    'snake',
    'pigeon',
    'hen',
    'gizzard',
    'ostrich',
    'organ',
    'pheasant',
    'quail',
    'squab',
    'emu',
    'mutton'
]

seafood = [
    'fish','shellfish','roe','crustacean','seaweed','anchovies',
    'basa','bass','cod','sablefish','blowfish','bluefish','bream','brill',
    'butter fish', 'catfish', 'dogfish', 'dorade', 'eel', 'flounder', 'grouper',
    'haddock', 'hake',' halibut', 'herring', 'dory', 'lamprey', 'mackerel',
    'mahi', 'mullet', 'monkfish','parrotfish','roughy','toothfish','perch','pike',
    'pilchard','pollock','pomfret','pompano','sablefish','salmon','sardine','sanddab',
    'shad','shark','skate','smelt','snakehead','snapper','sole','sprat','sturgeon','caviar',
    'tilapia','tilefish','trout','tuna','turbot','wahoo','whitefish','whiting','witch',
    'ikura','lumpfish','kazunoko','masago','topiko','flying fish','crab','crawfish','crayfish','lobster','shrimp',
    'prawn','cockle','cuttlefish','clam','loco','mussel','octopus','oyster','periwinkle','scallop',
    'squid','conch','snail','nautilus','sea cucumber','sea urchin','urchin','jellyfishh','sea fig'
]

herbs = ['basil', 'cilantro', 'parsley', 'rosemary', 'thyme', 'dill', 'oregano']

spices = ['black pepper', 'nutmeg', 'ginger']

veggies = ['onion', 'bell pepper', 'potato', 'sweet potato', 'broccoli']

vegetarian_subs = [
    {
        'quantity':8, 'measurement':'ounces', 'name': 'tofu', 'descriptor': ['firm'], 'preparation': ['drained']
    },
    {
        'quantity':8, 'measurement':'ounces', 'name': 'Beyond Meat', 'descriptor': [], 'preparation': []
    },
    {
        'quantity':8, 'measurement':'ounces', 'name': 'mushrooms', 'descriptor': [], 'preparation': []
    },
    {
        'quantity':8, 'measurement':'ounces', 'name': 'tempeh', 'descriptor': [], 'preparation': []
    },
    {
        'quantity':8, 'measurement':'ounces', 'name': 'eggplants', 'descriptor': [], 'preparation': []
    },
    {
        'quantity':8, 'measurement':'ounces', 'name': 'seitan', 'descriptor': [], 'preparation': []
    },
    {
        'quantity':8, 'measurement':'ounces', 'name': 'cauliflowers', 'descriptor': [], 'preparation': []
    },
    {
        'quantity':8, 'measurement':'ounces', 'name': 'lentils', 'descriptor': [], 'preparation': []
    },
    {
        'quantity':8, 'measurement':'ounces', 'name': 'black beans', 'descriptor': [], 'preparation': []
    },
    {
        'quantity':8, 'measurement':'ounces', 'name': 'legumes', 'descriptor': [], 'preparation': []
    }
]

herbs_spices = [
    'cheese', 'gravy','sauce','tomato','chili','garlic','rosemary','ginger','parsley','cumin','nutmeg','coriander','paprika','chives',
    'oregano','thyme','basil','salt','pepper','dill','cardamom','allspice','cayenne','cayenne pepper','saffron',
    'anise','chervil','celery','sage','tarragon','chicory','lovage','marjoram','vanilla','clove','prosciutto','carrots','carrot','sour cream'
]

l_f = ['cheese', 'yogurt', 'mayonnaise', 'mayo', 'cream cheese', 'sour cream', 'cottage cheese', 'ricotta', 'mozzarella', 'feta']

grains = ['bread', 'flour', 'breadcrumbs']

l_m = ['beef', 'turkey', 'chicken', 'pork']

h_subs = {'butter' : ['vegetable oil', []], 'sugar' : ['honey', []], 'milk' : ['milk', ['skim']], 'cream' : ['milk', ['skim']]}

u_subs = {'vegetable oil' : ['butter', ['full-fat']], 'honey' : ['corn syrup', ['high-fructose']],
          'canola oil' : ['butter', ['full-fat']], 'olive oil' : ['butter', ['full-fat']],
          'margerine' : ['butter', ['full-fat']], 'sugar' : ['corn syrup', ['high-fructose']],
          'sweetener' : ['corn syrup', ['high-fructose']], 'milk' : ['milk', ['whole']]}

meat_subs = [
    {
        'quantity':8, 'measurement':'ounces', 'name': 'beef', 'descriptor': ['ground'], 'preparation': []
    },
    {
        'quantity':8, 'measurement':'ounces', 'name': 'shrimp', 'descriptor': [], 'preparation': ['deveined','peeled']
    },
    {
        'quantity':8, 'measurement':'ounces', 'name': 'chicken', 'descriptor': [], 'preparation': []
    },
    {
        'quantity':8, 'measurement':'ounces', 'name': 'sausage', 'descriptor': [], 'preparation': ['cut']
    },
    {
        'quantity':8, 'measurement':'ounces', 'name': 'lamb', 'descriptor': [], 'preparation': []
    },
    {
        'quantity':8, 'measurement':'ounces', 'name': 'tuna', 'descriptor': [], 'preparation': ['shredded']
    },
]

italian_herbs = ["oregano", "basil", "sage", "rosemary", "parsley", "thyme", "pepper flakes"]
other_herbs = ["borage", "bay laurel", "caraway", "catnip", "chevril", "chives", "cilantro", "dill",
               "epazote", "fennel", "lavendar", "lemon grass", "lemon balm", "lemon verbena", "lovage",
               "mint", "nasturtium", "sorrel", "taragon", "cumin", "corriander", "cinnamon", "ginger",
               "nutmeg"]

#italian_shellfish_s = ["mussel"]
#italian_shellfish_p = ["mussels"]
#other_shellfish_s = ["clam", "oyster"]
#other_shellfish_p = ["clams", "oysters"]

italian_proteins = ["veal", "sauage"] # panchetta, prosciutto
other_proteins = ["beef", "chicken", "turkey", "pork", "ham", "lamb", "goat"]

italian_pasta = ["spaghetti", "linguine", "fettuccini", "macaroni", "rigatoni",
                 "penne", "fusilli", "farfalle"]
other_noodles = ["egg noodles", "rice noodles", "ramen noodles", "ramen", "oil noodles",
                 "yi mein", "saang mein", "cellophane noodles", "lai fun", "rice vermicelli",
                 "wonton noodles", "udon noodles", "udon", "soba", "somen", "wanko soba", "yakisoba",
                 "bakmi", "sevai", "paomo"]

other_oils = ["canola oil", "vegetable oil", "peanut oil", "sesame oil", "chili oil", "butter",
              "margarine", "lard", "palm oil", "corn oil", "coconut oil", "grapeseed oil", "avocado oil"]
other_vinegars = ["wine vinegar", "apple cider vinegar", "rice vinegar", "vinegar", "malt vinegar", "white wine vinegar", "red wine vinegar"]