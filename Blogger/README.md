# Blogger — مقالات كرة القدم

لاب **AB-ORM-1**: مدونة بـ Django فيها صفحتان:

| الرابط | الصفحة |
|---|---|
| `/` | الرئيسية: أحدث المقالات المنشورة (العنوان، النص، تاريخ ووقت النشر) — الأحدث أولاً |
| `/posts/add/` | إضافة مقال جديد (نموذج ModelForm مع التحقق ورسالة نجاح) |

## الموديل `Post`

| الحقل | النوع |
|---|---|
| `title` | `CharField(max_length=2048)` |
| `content` | `TextField()` |
| `is_published` | `BooleanField(default=True)` |
| `published_at` | `DateTimeField(auto_now_add=True)` |

الرئيسية تعرض فقط `is_published=True`، مرتبة بـ `-published_at`.

## التشغيل

```bash
python -m venv venv
venv\Scripts\activate            # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata sample_posts   # اختياري: 6 مقالات تجريبية عن كرة القدم
python manage.py runserver
```

افتح http://127.0.0.1:8000/

- لوحة التحكم (اختياري): `python manage.py createsuperuser` ثم `/admin/`
- الاختبارات: `python manage.py test`

## ما استخدمناه من الدروس

- **Templates & Inheritance:** `base.html` فيه الناف بار والفوتير والرسائل، والصفحات تمدّه بـ `{% extends %}`، والأجزاء المشتركة في `partials/` عبر `{% include %}`.
- **Static files:** CSS و JS والشعار ونقش الملعب عبر `{% static %}`.
- **Dynamic URLs:** كل الروابط بـ `{% url 'main:home' %}` و `{% url 'main:add_post' %}` و `redirect("main:home")`.
- **ORM:** `Post.objects.filter(is_published=True).order_by("-published_at")` و `form.save()`.
- **Forms:** `ModelForm` مع `{% csrf_token %}` وعرض الأخطاء تحت الحقول.
- **Messages framework:** رسالة «تم نشر المقال» بعد الحفظ.

## هيكل المشروع

```
Blogger/
├── manage.py
├── requirements.txt
├── Blogger/            settings.py · urls.py · wsgi.py · asgi.py
└── main/
    ├── models.py       Post
    ├── forms.py        PostForm
    ├── views.py        home · add_post
    ├── urls.py         app_name = "main"
    ├── admin.py        تسجيل Post في لوحة التحكم
    ├── tests.py
    ├── migrations/0001_initial.py
    ├── fixtures/sample_posts.json
    ├── templates/main/ base.html · home.html · add_post.html · partials/
    └── static/main/    css/style.css · js/main.js · img/ (logo, favicon, pitch)
```
