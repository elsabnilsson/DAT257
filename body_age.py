from person import Person

class BodyAge:
    def calculate(self, person: Person) -> int:
        bmi = person.calculate_bmi()
        adjustment = 0

        if bmi < 18.5:
            adjustment = 1
        elif 18.5 <= bmi < 25:
            adjustment = -1
        elif 25 <= bmi < 30:
            adjustment = 2
        else:  # BMI ≥ 30
            adjustment = 3

        return max(0, round(person.get_age() + adjustment))
