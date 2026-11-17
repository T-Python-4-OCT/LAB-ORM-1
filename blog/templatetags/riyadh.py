from zoneinfo import ZoneInfo
from django import template
from django.utils import timezone
from django.utils.formats import date_format
register=template.Library()
@register.filter
def riyadh_date(value):
    if not value:return ''
    value=timezone.localtime(value,ZoneInfo('Asia/Riyadh'))
    return date_format(value,'j F Y')+'، '+date_format(value,'g:i A')

@register.filter
def english_date(value):
    if not value:return ''
    from django.utils.translation import override
    with override('en'):
        if hasattr(value, 'hour'):
            value = timezone.localtime(value, ZoneInfo('Asia/Riyadh'))
            return date_format(value,'d M Y, H:i',use_l10n=False)
        return date_format(value,'d M Y',use_l10n=False)
