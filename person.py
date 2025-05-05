from datetime import date

class Person:
    def __init__(self, dob, height_m, weight_kg, gender, goal_weight=None):
        self.dob = dob
        today = date.today()
        self.age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        self.goal_weight = goal_weight
        
        if not (18 <= self.age <= 100):
            raise ValueError("Age must be between 18 and 100.")
        if not (1.2 <= height_m <= 2.5):
            raise ValueError("Height must be between 120 and 250 cm.")
        if not (30 <= weight_kg <= 300):
            raise ValueError("Weight must be between 30 and 300 kg.")

        self.height = height_m
        self.weight = weight_kg
        self.gender = gender.lower()
        
    def lose_weight(self):
        return self.goal_weight is not None and self.weight > self.goal_weight

    def gain_weight(self):
        return self.goal_weight is not None and self.weight < self.goal_weight

    def get_age(self):
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    def calculate_bmr(self):
        base = 10 * self.weight + 6.25 * self.height * 100 - 5 * self.age
        if self.gender == "female":
            base -= 161
        else:
            base += 5

        if self.lose_weight():
            return base * 0.8
        elif self.gain_weight():
            return base * 1.2
        else:
            return base

    def calculate_bmi(self):
        return round(self.weight / (self.height ** 2), 2)
    

