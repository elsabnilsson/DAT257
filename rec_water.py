from person import Person

def calc_water_intake(person: Person, activity_level: str):
    water_intake = person.weight * 0.0325 # base water intake in liters

    if activity_level == "moderate":
        extra_water = 0.25
    elif activity_level == "active":
        extra_water = 0.5
    else:
        extra_water = 0
    
    total_water_intake = water_intake + extra_water

    return round(total_water_intake, 1)
