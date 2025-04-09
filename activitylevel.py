from nutrition import NutritionStrategy


class InactiveNutrition(NutritionStrategy):
    def get_activity_factor(self):
        return 1.2

class ModerateNutrition(NutritionStrategy):
    def get_activity_factor(self):
        return 1.5

class ActiveNutrition(NutritionStrategy):
    def get_activity_factor(self):
        return 1.7
