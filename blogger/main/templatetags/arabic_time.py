"""Template filter that says how long ago a post was published, in correct Arabic.

Django's naturaltime writes "منذ 3 دقيقة", which is wrong Arabic (it should be "منذ 3 دقائق").
Use it in a template:  {% load arabic_time %}  then  {{ post.published_at|ago }}
"""

from django import template
from django.utils import timezone

register = template.Library()

# (one, two, 3 to 10, 11 and more)
UNITS = [
    (365 * 24 * 60 * 60, ("سنة", "سنتين", "سنوات", "سنة")),
    (30 * 24 * 60 * 60, ("شهر", "شهرين", "أشهر", "شهراً")),
    (7 * 24 * 60 * 60, ("أسبوع", "أسبوعين", "أسابيع", "أسبوعاً")),
    (24 * 60 * 60, ("يوم", "يومين", "أيام", "يوماً")),
    (60 * 60, ("ساعة", "ساعتين", "ساعات", "ساعة")),
    (60, ("دقيقة", "دقيقتين", "دقائق", "دقيقة")),
]


def arabic_count(number: int, words: tuple) -> str:
    """1 دقيقة -> "دقيقة", 2 -> "دقيقتين", 3..10 -> "3 دقائق", 11+ -> "11 دقيقة"."""
    one, two, few, many = words
    if number == 1:
        return one
    if number == 2:
        return two
    if number <= 10:
        return f"{number} {few}"
    return f"{number} {many}"


@register.filter
def ago(value):
    """A datetime -> "الآن", "منذ دقيقة", "منذ 3 دقائق", "منذ ساعتين", "منذ 5 أيام" ..."""
    if not value:
        return ""
    seconds = int((timezone.now() - value).total_seconds())
    if seconds < 60:
        return "الآن"
    for size, words in UNITS:
        if seconds >= size:
            return "منذ " + arabic_count(seconds // size, words)
    return "الآن"
