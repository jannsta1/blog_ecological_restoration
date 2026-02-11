from django import template
from django.contrib.messages import constants as msg_constants
from django.contrib.messages.storage.fallback import FallbackStorage
from django.db.models import QuerySet

register = template.Library()


@register.filter()
def set_banner_color(messages: QuerySet) -> str:
    """
    Sets the banner color based on the number of items in the queryset.
    """
    if not isinstance(messages, QuerySet) and not isinstance(messages, FallbackStorage):
        raise ValueError(
            "The 'set_banner_color' filter expects a QuerySet or FallbackStorage."
        )

    levels = [m.level for m in messages]
    levels.sort()

    if not levels:
        return (
            "bg-[var(--color-background)]"  # Default to green if there are no messages
        )

    match levels[0]:
        case msg_constants.ERROR:
            return "bg-red-500"
        case msg_constants.WARNING:
            return "bg-yellow-500"
        case msg_constants.SUCCESS:
            return "bg-green-500"
        case _:
            return "bg-[var(--color-background)]"  # Default to transparent for other message levels
