
from django import template
from django.utils.safestring import mark_safe
import bleach

register = template.Library()


@register.filter
def safe_html(value):

    allowed_tags = [
        'p', 'br', 'b', 'strong', 'i', 'em', 'u',
        'h2', 'h3', 'h4', 'ul', 'ol', 'li',
        'blockquote', 'span', 'div'
    ]

    cleaned_content = bleach.clean(
        value or '',
        tags=allowed_tags,
        attributes={},
        strip=True
    )

    return mark_safe(cleaned_content)
