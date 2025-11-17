from django import forms

from .models.usersettings import UserSettings


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = [
            "timezone",
            "theme",
            "preferred_unit",
            "glucose_target_very_low",
            "glucose_target_low",
            "glucose_target_high",
            "glucose_target_very_high",
        ]

        widgets = {
            "timezone": forms.TextInput(attrs={"class": "form-control"}),
            "theme": forms.Select(attrs={"class": "form-control"}),
            "preferred_unit": forms.Select(attrs={"class": "form-control"}),
            "glucose_target_very_low": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "glucose_target_low": forms.NumberInput(attrs={"class": "form-control"}),
            "glucose_target_high": forms.NumberInput(attrs={"class": "form-control"}),
            "glucose_target_very_high": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
        }
