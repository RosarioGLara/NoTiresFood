from flask import Flask, request, jsonify
from logic_recipe_generator import generate_recipes

app = Flask(__name__)

@app.route('/')
def home():
     return "Welcome to the Recipe Generator API!"

@app.route('/generate', methods=['POST'])

def generate():
     data = request.get_json()
     user = data['user']
     ingredients = data['ingredients']
     recipes = generate_recipes(user, ingredients)
     return jsonify(recipes)

if __name__ == '__main__':
     app.run(debug=True)