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
