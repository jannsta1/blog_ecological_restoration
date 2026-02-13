from django.http import HttpResponseRedirect
# Create your views here.


def change_theme(request, **kwargs):
    if "is_dark_theme" not in request.session:
        request.session["is_dark_theme"] = True
    else:
        request.session["is_dark_theme"] = not request.session.get("is_dark_theme")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
