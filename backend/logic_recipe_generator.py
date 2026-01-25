import datetime
import json
import re
from google import genai
import os
import time
class Ingredient:
     def __init__(self, name, expiration_date, quantity):
          self.name = name
          self.expiration_date = expiration_date
          self.quantity = quantity

     def __repr__(self):
          return f"{self.name} (Expires: {self.expiration_date}, Quantity: {self.quantity})"
     
def parse_steps(text):
     lines = text.strip().split('\n')
     steps = []
     for line in lines:
          match = re.match(r'^\d+\.\s*(.*)', line)
          if match:
               steps.append(match.group(1).strip())
     return steps

def validate_steps(text, ingredients):
     #parse steps
     steps = parse_steps(text)
     if not (5 <= len(steps) <= 7):
          return False, "The recipe must contain between 5 to 7 steps."
     
     for step in steps:
          for word in normalize_ingredient_name(step).split():
               if word not in ingredients:
                    return False, f"The step contains an ingredient '{word}' that is not available."
     return True, steps

def call_api(recipes):
     #genai.configure(api_key="AIzaSyBMtsoAbBd-B7rW3pT3Skg2asBTzwkQ8aA")
     client = genai.Client(api_key="AIzaSyB-OP3UAiUndss8ssLGAZ10Fx0NgOU1N0s")
     if recipes:
          with open('recipes.json', 'r') as file:
               all_recipes = json.load(file)
          
          final_recipes = []
          for name, values in recipes:
               missing_ings = ', '.join(values[1]) if values[1] else 'None'
               matched_ings = ', '.join(values[2]) if values[2] else 'None'
               difficulty = values[3]
               steps = all_recipes[[r['name'] for r in all_recipes].index(name)]['steps']
               #print(f"Recipe: {name}\n  Difficulty: {difficulty}\n  Missing Ingredients: {missing_ings}\n  Matched Ingredients: {matched_ings}\n")
               prompt = f"You are a helpful cooking assistant. Create an easy, step-by-step recipe. The recipe is called '{name}'. It has a difficulty level of '{difficulty}'. The rules are: Use only available ingredients. If an ingredient is missing, suggest alternatives or omit it. Use 5-7 steps and keep language beginner friendly, based on the following steps generate the recipe: {steps}"
               response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
               #print("Generated Recipe Instructions:")
               #print(response.text)
               valid, result = validate_steps(response.text, values[2])
               
               if not valid:
                    repair_prompt = f"The following recipe steps are invalid due to {result}. Please rewrite the recipe using from 5 to 7 steps, use only available ingredients: {', '.join(values[2])}. No extra text."
                    repair_response = client.models.generate_content(model="gemini-2.5-flash", contents=repair_prompt)
                    response = repair_response.text
                    response = parse_steps(response)
                    result = response
               
               recipe = {
                    "name": name,
                    "difficulty": difficulty,
                    "missing_ingredients": list(values[1]),
                    "matched_ingredients": list(values[2]),
                    "steps": result
               }
               final_recipes.append(recipe)
               time.sleep(12)
          path = os.path.join(os.getcwd(), "generated_recipes.json")
          with open(path, 'w') as outfile:
               json.dump(final_recipes, outfile, indent=4)
          
          #print(f"Generated recipes have been saved to {path}")
          

def date_diff(exp_date, current_date):
     year_diff = exp_date[0] - current_date[0]
     month_diff = exp_date[1] - current_date[1]
     day_diff = exp_date[2] - current_date[2]
     return year_diff * 365 + month_diff * 30 + day_diff

def ingredient_key(ingredients):
     ingredient_dict = dict()
     for ingredient in ingredients:
          #roprint(ingredient)
          ing = normalize_ingredient_name(ingredient[0].name)
          ing = ingredient_to_tokens(ing)
          ingredient_dict[tuple(ing)] = ingredient
     return ingredient_dict

def singularize(name):
     if name.endswith("ies"):
          return name[:-3] + "y"
     if name.endswith("es"):
          return name[:-2]
     if name.endswith("s") and len(name) > 3:
          return name[:-1]
     return name

def ingredient_to_tokens(name):
     return set(name.lower().split())

def normalize_ingredient_name(name):
     stop_words = {"tbsp", "tsp", "cup", "cups", "kg", "g", "ml",
    "tablespoon", "teaspoon", "grams", "liter", "liters", "pound", "pounds",
    "ounce", "ounces", "package", "packages", "can", "cans", "bunch", "bunches",
    "slice", "slices", "clove", "cloves", "pinch", "dash", "large", "small", "medium"}
     name = name.lower()
     name = re.sub(r"\d+\/?\d*", "", name)
     tokens = name.split()
     tokens = [singularize(token) for token in tokens if token not in stop_words and len(token)>2]
     return " ".join(tokens)

def token_matching(recipe_name, recipe_ingredients, ingredients_set, ingredients):
     fridge_tokens = [set(k) for k, v in ingredients_set.items()]
     score_recipe = dict()
     matched_ingredients = set()
     missused_ingredients = set()
     score = 0
     for recipe_ing in recipe_ingredients:
          recipe_tokens = ingredient_to_tokens(recipe_ing)
          found = False
          for f_tokens in fridge_tokens:
               if recipe_tokens & f_tokens:
                    score+=2
                    found = True
                    ingredient = ingredients_set[tuple(f_tokens)]
                    exp_date = date_diff(ingredient[0].expiration_date, datetime.datetime.now().date().timetuple()[:3])
                    if exp_date < 3:
                         score+=3
                    elif exp_date < 7:
                         score+=2
                    else:
                         score+=1
                    matched_ingredients.add(ingredient[0].name)
                    break
          if not found:
               score-=1
               missused_ingredients.add(recipe_ing)
     return score, missused_ingredients, matched_ingredients

def find_recipes(ingredients):
     try:
          with open('recipes.json', 'r') as file:
               recipes = json.load(file)
          recipe_valid = dict()
          for recipe in recipes:
               recipe_ingredients = [normalize_ingredient_name(ing) for ing in recipe['ingredients']]
               ingredients_set = ingredient_key(ingredients)
               score_recipe, missused_ingredients, matched_ingredients = token_matching(recipe['name'], recipe_ingredients, ingredients_set, ingredients)
               if score_recipe > 0:
                    difficulty = recipe['difficulty'].lower()
                    recipe_valid[recipe['name']] = [score_recipe, missused_ingredients, matched_ingredients, difficulty]
          #print(recipe_valid.items())
          sorted_recipes = sorted(recipe_valid.items(), key=lambda x: x[1], reverse=True)
          #print("Recommended Recipes:")
          """for recipe, values in sorted_recipes[:5]:
               print(f"{recipe} - Score: {values[0]}, Missed Ingredients: {values[1]}, Matched Ingredients: {values[2]}")"""
          return sorted_recipes[:5]
     except FileNotFoundError:
          #print("Recipes file not found.")
          return []

def check_allergies(ingredients, allergies):
     for ing in ingredients:
          if ing in allergies:
               ingredients.remove(ing)
     return ingredients

def prioritize_ingredients(ingredients, allergies):
     #clean expired ingredients
     ingredients = check_allergies(ingredients, allergies)
     current_date = datetime.datetime.now().date()
     current = [int(i) for i in str(current_date).split("-")]
     diff_dict = dict()
     expired = {i:False for i in ingredients}
     for ingredient in ingredients:
          exp_date = ingredient.expiration_date
          year_diff = exp_date[0] - current[0]
          month_diff = exp_date[1] - current[1]
          day_diff = exp_date[2] - current[2]
          diff = year_diff * 365 + month_diff * 30 + day_diff
          if diff < 0:
               #print(f"Removing expired ingredient: {ingredient}")
               expired[ingredient] = True
               continue
          diff_dict[ingredient] = diff
     ingredients = [i for i in ingredients if not expired[i]]
     #print("Valid ingredients after removing expired ones:", ingredients)

     #prioritize by expiration date
     sorted_ingredients = sorted(diff_dict.items(), key=lambda x: x[1])
     #print("Prioritized ingredients by expiration date:", sorted_ingredients)
     return sorted_ingredients

def generate_recipes(user,ingredients_input):
     ingredients = []

     for ing in ingredients_input:
          ingredients.append(Ingredient(ing['name'], ing['expiration_date'], ing['quantity']))

     prioritized_ingredients = prioritize_ingredients(ingredients)
     recipes = find_recipes(prioritized_ingredients)
     call_api(recipes)

     with open("generated_recipes.json", 'r') as file:
          return json.load(file)

def __init__():
     print('Select all your current ingredients:')
     ingredients = []
     allergies = []
     while True:
          ing = input('Ingredient: ')
          exp_date = input('Exp_date: ')
          quantity = input('Quantity: ')
          ingredients.append(Ingredient(ing, exp_date, quantity))
     
     print('Add your ingredient allergies: ')
     while True:
          ing = input('Ingredient: ')
          allergies.append(ingredient)
