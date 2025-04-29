class Person:
    def __init__(self, age, height_m, weight_kg, gender):
        if not (18 <= age <= 100):
            raise ValueError("Age must be between 18 and 100.")
        if not (1.2 <= height_m <= 2.5):
            raise ValueError("Height must be between 120 and 250 cm.")
        if not (30 <= weight_kg <= 300):
            raise ValueError("Weight must be between 30 and 300 kg.")
        
        self.age = age
        self.height = height_m
        self.weight = weight_kg
        self.gender = gender.lower()

    def calculate_bmr(self):
        if self.gender == "female":
            return 10 * self.weight + 6.25 * self.height * 100 - 5 * self.age - 161
        else:
            return 10 * self.weight + 6.25 * self.height * 100 - 5 * self.age + 5
        
        
    def calculate_bmi(self):
        return round(self.weight / (self.height ** 2), 2)
