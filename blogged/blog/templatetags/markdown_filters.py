import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def render_markdown(text: str) -> str:
    """
    Converts markdown text to HTML.
    """
    return mark_safe(markdown.markdown(text, extensions=["fenced_code"]))
    # for more extensions see https://python-markdown.github.io/extensions/
