from django.db import models


class ImpactType(models.TextChoices):
    SHORT = "SHORT", "Short (≈2h)"  # e.g. simple sugars
    MEDIUM = "MEDIUM", "Medium (≈4h)"  # e.g. complex carbs
    LONG = "LONG", "Long (≈6h)"  # e.g. high fat + carbs like pizza


class MealType(models.TextChoices):
    BREAKFAST = "BREAKFAST", "Breakfast"
    LUNCH = "LUNCH", "Lunch"
    DINNER = "DINNER", "Dinner"
    SNACK = "SNACK", "Snack"


class MealEntity(models.Model):
    """
    Meal Data Model (Pythonic style)

    Mirrors Kotlin MealEntity fields:
      - user_id: Int
      - description: String?
      - created_at_utc: Long
      - meal_time_utc: Long
      - calories: Int? = 0
      - carbohydrates: Int = 0
      - proteins: Int? = 0
      - fats: Int? = 0
      - impact_type: ImpactType (SHORT, MEDIUM, LONG)
      - meal_type: MealType (BREAKFAST, LUNCH, DINNER, SNACK)
      - is_valid: Boolean = true
      - image_id: String
      - recommendation: String?
      - reasoning: String?
      - source_id: String? = null
    """

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    created_at_utc = models.DateTimeField()
    meal_time_utc = models.DateTimeField()
    calories = models.IntegerField(null=True, blank=True, default=0)
    carbohydrates = models.IntegerField(default=0)
    proteins = models.IntegerField(null=True, blank=True, default=0)
    fats = models.IntegerField(null=True, blank=True, default=0)
    impact_type = models.CharField(
        max_length=10,
        choices=ImpactType.choices,
        default=ImpactType.MEDIUM,
    )
    meal_type = models.CharField(
        max_length=10,
        choices=MealType.choices,
        default=MealType.SNACK,
    )
    is_valid = models.BooleanField(default=True)
    image_id = models.CharField(null=True, max_length=255, blank=True)
    recommendation = models.TextField(null=True, blank=True)
    reasoning = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=100, default="Unknown")
    source_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user_id"]),
        ]
        ordering = ["-meal_time_utc"]

    def __str__(self):
        return f"{self.get_meal_type_display()} for {self.user.username} at {self.meal_time_utc:%Y-%m-%d %H:%M}"
