import pytest 

from activitylevel import InactiveNutrition, ModerateNutrition, ActiveNutrition
from person import Person
from rec_water import calc_water_intake
from body_age import BodyAge


def test_