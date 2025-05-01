from datetime import date

class Person:
    def __init__(self, date_of_birth, height_m, weight_kg, gender):
        self.date_of_birth = date_of_birth
        self.height = height_m
        self.weight = weight_kg
        self.gender = gender.lower()

        today = date.today()
        self.age = today.year - date_of_birth.year - (
            (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
        )

    def calculate_bmr(self):
        if self.gender == "female":
            return 10 * self.weight + 6.25 * self.height * 100 - 5 * self.age - 161
        else:
            return 10 * self.weight + 6.25 * self.height * 100 - 5 * self.age + 5

    def calculate_bmi(self):
        return round(self.weight / (self.height ** 2), 2)
