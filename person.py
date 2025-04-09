class Person:
    def __init__(self, age, height_m, weight_kg, gender):
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
