from functools import wraps

from hitcount.models import HitCount
from hitcount.models import UrlHit


# Create your views here.
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def track_hit_count(view_func):
    """
    Decorator to track hit counts for views.
    Records unique hits based on IP and session.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        update_hit_count(request)
        response = view_func(request, *args, **kwargs)
        return response

    return wrapper


def update_hit_count(request):
    """
    Records a hit for the current request.
    """
    if not request.session.session_key:
        request.session.save()

    s_key = request.session.session_key
    ip = get_client_ip(request)
    request.session[ip] = ip
    request.session[request.path] = request.path

    # get or create UrlHit object for this url
    url, url_object_created = UrlHit.objects.get_or_create(url=request.path)

    # if this is a new UrlHit object, track the hit
    if url_object_created or (ip and request.path not in request.session):
        new_track_object, created = HitCount.objects.get_or_create(
            url_hit=url, ip=ip, session=s_key
        )
        if created:
            url.increase()
