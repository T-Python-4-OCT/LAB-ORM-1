import re
import unicodedata
from django.core.exceptions import ValidationError

def validate_publisher_name(value):
    if not value or not value.strip():
        raise ValidationError('اسم الناشر مطلوب.')
    val = value.strip()
    if len(val) < 2:
        raise ValidationError('يجب أن يحتوي اسم الناشر على حرفين على الأقل.')
    if len(val) > 150:
        raise ValidationError('اسم الناشر لا يجب أن يتجاوز 150 حرفاً.')
    
    # Check for digits (Western digits 0-9 and Arabic-Indic digits ٠-٩)
    if re.search(r'[\d٠-٩]', val):
        raise ValidationError('لا يمكن استخدام الأرقام في اسم الناشر.')
    
    if any(not (unicodedata.category(c)[0] in ['L', 'M'] or c in " '-’") for c in val):
        raise ValidationError('اسم الناشر يجب أن يحتوي على حروف ومسافات فقط، ويمكن استخدام الشرطة أو الفاصلة العليا.')

    # Must contain at least one alphabetic letter (Unicode letter category)
    if not re.search(r'[^\W\d_]', val, re.UNICODE):
        raise ValidationError('يجب أن يتكون اسم الناشر من حروف، ويمكن استخدام المسافات والفواصل المسموح بها.')

def validate_article_title(value):
    if not value or not value.strip():
        raise ValidationError('عنوان المقال مطلوب.')
    val = value.strip()
    if len(val) < 5:
        raise ValidationError('يجب أن يتكون العنوان من 5 أحرف على الأقل.')
    if len(val) > 2048:
        raise ValidationError('تجاوز العنوان الحد الأقصى المسموح.')
    
    # Must contain at least one alphabetic letter (rejects titles consisting only of numbers or symbols)
    if not re.search(r'[^\W\d_]', val, re.UNICODE):
        raise ValidationError('لا يمكن أن يتكون العنوان من أرقام أو رموز فقط.')

def validate_article_content(value):
    if not value or not value.strip():
        raise ValidationError('محتوى المقال مطلوب.')
    val = value.strip()
    
    # Check minimum length of non-whitespace characters (>= 30)
    non_ws_chars = [c for c in val if not c.isspace()]
    if len(non_ws_chars) < 30:
        raise ValidationError('يجب ألا يقل محتوى المقال عن 30 حرفًا فعليًا.')
    
    # Must contain at least one alphabetic letter (rejects numbers-only or symbols-only content)
    if not re.search(r'[^\W\d_]', val, re.UNICODE):
        raise ValidationError('يجب أن يحتوي المحتوى على نص مكتوب، وليس أرقامًا أو رموزًا فقط.')
