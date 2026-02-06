from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def admin_home(request):
    if request.user.profile.location.name != "Austin":
        return render(request, "403.html")

    return render(request, "admin/dashboard.html")
