from django import template
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags
from django.utils.text import Truncator

from html import unescape

from blog.forms import sanitize_content


register = template.Library()


@register.filter
def rich_content(value):
    cleaned = sanitize_content(value or "")
    return mark_safe(cleaned)


@register.filter
def post_excerpt(value, length=180):
    # Remove HTML tags
    plain_text = strip_tags(value or "")

    # Convert HTML entities to regular characters
    plain_text = unescape(plain_text)

    # Normalize whitespace
    plain_text = " ".join(plain_text.split())

    # Shorten content
    return Truncator(plain_text).chars(int(length))