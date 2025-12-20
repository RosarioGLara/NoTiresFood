# 🍽️ NoTiresFood

**NoTiresFood** is a smart recipe recommendation system designed to reduce food waste by generating recipes based on the ingredients a user already has in their fridge. Ingredients are prioritized by expiration date, ensuring perishable items are used first. The project combines deterministic, rule-based logic with optional AI-assisted recipe generation to produce clear, practical, and easy-to-follow meals.

---

## 🌱 Motivation

Food waste is a global issue often caused by forgotten ingredients and poor meal planning.  
NoTiresFood aims to tackle this problem by helping users cook smarter, using what they already have before it expires, making everyday cooking more sustainable, efficient, and intentional.

---

## ⚙️ How It Works

1. The user inputs ingredients, quantities, and expiration dates.
2. Expired ingredients are automatically removed.
3. Remaining ingredients are ranked by urgency (expiration date).
4. Recipes are matched and scored based on ingredient availability.
5. Recipes that use high-priority ingredients rank higher.
6. An AI model generates step-by-step cooking instructions using the selected ingredients.

---

## ✨ Features

- 🧊 Fridge ingredient tracking with expiration dates  
- ⏰ Expiration-based ingredient prioritization  
- 🧮 Rule-based recipe matching and scoring  
- 🧹 Ingredient normalization and text cleaning  
- 📋 Clear, step-by-step recipe output  
- 🔌 Modular design with optional AI integration  

---

## 🧠 Core Logic

- Ingredient expiration scoring  
- Recipe-to-fridge ingredient matching  
- Missing ingredient penalties  
- Expiration-weighted ranking  
- Deterministic and testable logic before AI involvement  

This approach ensures transparency, reliability, and control over recipe recommendations.


