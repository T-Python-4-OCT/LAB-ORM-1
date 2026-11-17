from pathlib import Path, PurePosixPath
from io import BytesIO
import zipfile
import xml.etree.ElementTree as ET
from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image

TYPES = {'.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.webp':'image/webp','.gif':'image/gif','.pdf':'application/pdf','.txt':'text/plain','.docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document','.xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','.pptx':'application/vnd.openxmlformats-officedocument.presentationml.presentation'}
def safe_filename(name):
    name = str(name).replace('\\','/').split('/')[-1]
    return ''.join(c for c in name if c.isprintable() and c not in '<>"')[:200] or 'مرفق'

def validate_upload(file):
    ext = Path(file.name).suffix.lower()
    if ext not in TYPES:
        raise ValidationError('صيغة الملف غير مدعومة.')
    if file.size > settings.MAX_ATTACHMENT_SIZE:
        raise ValidationError('حجم الملف يتجاوز ١٠ ميجابايت.')
    if not file.size:
        raise ValidationError('الملف فارغ.')
    try:
        file.seek(0)
        data = file.read(settings.MAX_ATTACHMENT_SIZE + 1)
        if len(data) > settings.MAX_ATTACHMENT_SIZE:
            raise ValueError()
        if ext in ['.jpg','.jpeg','.png','.webp','.gif']:
            with Image.open(BytesIO(data)) as image:
                expected = {'.jpg':'JPEG','.jpeg':'JPEG','.png':'PNG','.webp':'WEBP','.gif':'GIF'}[ext]
                if image.format != expected or image.width * image.height > 25000000:
                    raise ValueError()
                image.verify()
        elif ext == '.pdf':
            if not data.startswith(b'%PDF-') or b'%%EOF' not in data[-2048:]: raise ValueError()
        elif ext == '.txt':
            text = data.decode('utf-8-sig')
            if any(ord(c) < 32 and c not in '\n\r\t' for c in text): raise ValueError()
        else:
            with zipfile.ZipFile(BytesIO(data)) as archive:
                entries = archive.infolist()
                if len(entries) > 1500 or sum(i.file_size for i in entries) > 50*1024*1024: raise ValueError()
                for i in entries:
                    path = PurePosixPath(i.filename)
                    if path.is_absolute() or '..' in path.parts or '\\' in i.filename or i.flag_bits & 1: raise ValueError()
                    if i.filename.lower().endswith(('.exe','.js','.html','.svg','.bat','.cmd','.sh','vbaproject.bin')): raise ValueError()
                    if i.file_size > 20*1024*1024 or i.file_size > max(i.compress_size,1)*200: raise ValueError()
                expected = {'.docx':'word/document.xml','.xlsx':'xl/workbook.xml','.pptx':'ppt/presentation.xml'}[ext]
                ET.fromstring(archive.read(expected))
                ct = archive.read('[Content_Types].xml')
                if b'macroEnabled' in ct: raise ValueError()
                types = ET.fromstring(ct)
                required_type = {'.docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml','.xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml','.pptx':'application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml'}[ext]
                if not any(node.get('PartName') == '/' + expected and node.get('ContentType') == required_type for node in types): raise ValueError()
        return TYPES[ext]
    except (ValueError, OSError, UnicodeError, zipfile.BadZipFile, KeyError, ET.ParseError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValidationError('محتوى الملف غير صالح أو لا يطابق صيغته.') from exc
    finally:
        file.seek(0)
