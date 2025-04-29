import pytest 

from activitylevel import InactiveNutrition, ModerateNutrition, ActiveNutrition
from person import Person
from rec_water import calc_water_intake
from body_age import BodyAge


tests = {
    "female": (23, 1.8, 88, "female"),
    "male": (23, 1.8, 88, "male"),
    }


def test_bmi_female():
    person = Person(*tests["female"])
    bmi = Person.calculate_bmi(person)
    assert bmi == pytest.approx(27.16,rel=1e-2)

def test_bmi_male():
    person = Person(*tests["male"])
    bmi = Person.calculate_bmi(person)
    assert bmi == pytest.approx(27.16,rel=1e-2)

def test_water_intake():
    female = Person(*tests["female"])
    male = Person(*tests["male"])
    
    assert calc_water_intake(male,InactiveNutrition) == pytest.approx(2.86, 0.1)
    assert calc_water_intake(male,ActiveNutrition) == pytest.approx(3,36, 0.1)
    assert calc_water_intake(male,ModerateNutrition) == pytest.approx(3.11, 0.1)
    assert calc_water_intake(female,InactiveNutrition) == pytest.approx(2.86, 0.1)
    assert calc_water_intake(female,ActiveNutrition) == pytest.approx(3,36, 0.1)
    assert calc_water_intake(female,ModerateNutrition) == pytest.approx(3.11, 0.1)

def test_bmr():
    male = Person(*tests["male"])
    female = Person(*tests["female"])
    bmr_male = Person.calculate_bmr(male)
    bmr_female = Person.calculate_bmr(female)
    assert bmr_male == pytest.approx(1890,1)
    assert bmr_female == pytest.approx(1890-161,1)

def test_bodyage():
    person = Person(*tests["female"])
    bodyage = BodyAge().calculate(person)
    assert bodyage == pytest.approx(25)
    



tests_wrong_input = {
    "wrong age": [(120, 1.8, 88, "female"), (1, 1.8, 88, "female")],
    "wrong height": [(23, 2.6, 88, "female"), (23, 0.5, 88, "female")],
    "wrong weight": [(23, 1.8, 301, "female"), (23, 1.8, 20, "female")]
    }

def test_wrong_age():    
        with pytest.raises(ValueError, match="Age must be between 18 and 100."):
            Person(*tests_wrong_input["wrong age"][0])
            Person(*tests_wrong_input["wrong age"][1])

def test_wrong_height():    
        with pytest.raises(ValueError, match="Height must be between 120 and 250 cm."):
            Person(*tests_wrong_input["wrong height"][0])
            Person(*tests_wrong_input["wrong height"][1])

def test_wrong_weight():    
        with pytest.raises(ValueError, match="Weight must be between 30 and 300 kg."):
            Person(*tests_wrong_input["wrong weight"][0])
            Person(*tests_wrong_input["wrong weight"][1])
