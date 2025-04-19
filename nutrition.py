from abc import ABC, abstractmethod
from person import Person

class NutritionStrategy(ABC):
    @abstractmethod
    def get_activity_factor(self):
        pass
        
    def calculate_macros(self, person: Person):
        calories = round(person.calculate_bmr() * self.get_activity_factor(), 1)
        protein = round((calories * 0.30) / 4, 1)
        fat = round((calories * 0.30) / 9, 1)
        carbs = round((calories * 0.40) / 4, 1)
        return calories, protein, fat, carbs
    
    def meal_spli(self, calories, protein, fat, carbs):
        meals = {
            "Breakfast": 0.25,
            "Lunch": 0.30,
            "Dinner": 0.30,
            "Snack": 0.15,   
        }
        
        meal_plan = {}
        
        for meal, factor in meals.items():
            meal_plan[meal] = {
                "calories": round(calories * factor, 1),
                "protein": round(protein * factor, 1),
                "fat": round(fat * factor, 1),
                "carbs": round(carbs * factor, 1)
            }
            
        return meal_plan
