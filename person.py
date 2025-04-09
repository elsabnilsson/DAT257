class Person:
    def __init__(self, age, height_m, weight_kg):
        if height_m < 0 or height_m > 3:
            raise ValueError("Wrong input")
        if weight_kg < 0 or weight_kg > 300:
            raise ValueError("Wrong input")
        if age < 0 or age > 130:
            raise ValueError("Wrong input")
        
        
        self.age = age
        self.height = height_m
        self.weight = weight_kg

    def calculate_bmr(self):
        return 10 * self.weight + 6.25 * self.height * 100 - 5 * self.age + 5

    def calculate_bmi(self):
        return round(self.weight / (self.height ** 2), 2)
