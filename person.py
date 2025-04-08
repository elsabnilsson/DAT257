class Person:
    def __init__(self, age, height_m, weight_kg):
        self.age = age
        self.height = height_m
        self.weight = weight_kg

    def calculate_bmr(self):
        return 10 * self.weight + 6.25 * self.height * 100 - 5 * self.age + 5

    def calculate_bmi(self):
        return round(self.weight / (self.height ** 2), 2)
