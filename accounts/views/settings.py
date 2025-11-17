from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.forms import UserSettingsForm
from accounts.models.usersettings import UserSettings


@login_required
def user_settings_view(request):
    # Create user settings automatically if missing
    settings_obj, created = UserSettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            return redirect("accounts:user_settings")
    else:
        form = UserSettingsForm(instance=settings_obj)

    return render(request, "accounts/user_settings.html", {"form": form})
