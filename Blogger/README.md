# Blogger — مقالات كرة القدم

لاب **AB-ORM-1**: مدونة بـ Django فيها صفحتان:

| الرابط | الصفحة |
|---|---|
| `/` | الرئيسية: أحدث 3 مقالات منشورة فقط، وزر «عرض كل المقالات» |
| `/posts/` | كل المقالات المنشورة، من الأحدث إلى الأقدم، مع أزرار فلترة حسب التصنيف (`?category=tactics`) وترتيب حسب التاريخ: الأحدث أولاً أو الأقدم أولاً (`?sort=oldest`) |
| `/posts/add/` | إضافة مقال جديد مع صورة اختيارية (نموذج ModelForm مع التحقق ورسالة نجاح) |
| `/posts/<id>/` | تفاصيل المقال: المقال كاملاً مع صورته، وتحته زرا التعديل والحذف |
| `/posts/<id>/update/` | تعديل المقال (Update): نفس النموذج معبّأً ببيانات المقال `PostForm(instance=post)` |
| `/posts/<id>/delete/` | حذف المقال (Delete): صفحة تأكيد، والحذف يتم بطلب POST فقط |

## الموديل `Post`

| الحقل | النوع |
|---|---|
| `title` | `CharField(max_length=2048)` |
| `content` | `TextField()` |
| `is_published` | `BooleanField(default=True)` |
| `published_at` | `DateTimeField(auto_now_add=True)` |
| `category` | `CharField(max_length=20, choices=Category.choices, default="general")` — عام · الخطط والتكتيك · التحكيم والقوانين · التدريبات واللياقة |
| `image` | `ImageField(upload_to="posts/", default="posts/default.jpg", blank=True)` — المقال بلا صورة يأخذ `media/posts/default.jpg` |

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
- **ORM:** `Post.objects.filter(is_published=True).order_by("-published_at")`، و`[:3]` (slicing) لأحدث 3 مقالات في الرئيسية مع `.count()` للعدد الكلي، و`get_object_or_404(Post, pk=post_id)`، و`form.save()` للإضافة والتعديل، و`post.delete()` للحذف.
- **Forms:** `ModelForm` مع `{% csrf_token %}` وعرض الأخطاء تحت الحقول.
- **Messages framework:** رسالة «تم نشر المقال» بعد الحفظ.
- **التصنيف والفلترة:** `models.TextChoices` للتصنيفات، و`request.GET.get("category")` مع `.filter(category=...)` في صفحة كل المقالات، و`get_category_display` لعرض الاسم العربي.
- **الترتيب:** `request.GET.get("sort")` مع `order_by("-published_at")` للأحدث أولاً و`order_by("published_at")` للأقدم أولاً، ويمكن جمعه مع التصنيف: `?category=tactics&sort=oldest`.
- **CRUD:** صفحة تفاصيل بـ URL ديناميكي `posts/<int:post_id>/`، وتعديل بـ `instance=post`، وحذف بعد صفحة تأكيد. النموذج مشترك بين الإضافة والتعديل في `partials/_post_form.html`.
- **رفع الصور:** `ImageField` (يحتاج Pillow)، و`enctype="multipart/form-data"` في النموذج، و`request.FILES` في الـ view، و`MEDIA_URL`/`MEDIA_ROOT` في الإعدادات مع `static()` في `urls.py` لعرض الصور أثناء التطوير.

## هيكل المشروع

```
Blogger/
├── manage.py
├── requirements.txt
├── Blogger/            settings.py · urls.py · wsgi.py · asgi.py
└── main/
    ├── models.py       Post
    ├── forms.py        PostForm
    ├── views.py        home · all_posts · add_post · post_detail · update_post · delete_post
    ├── urls.py         app_name = "main"
    ├── admin.py        تسجيل Post في لوحة التحكم
    ├── tests.py
    ├── migrations/0001_initial.py · 0002_post_image.py
    ├── fixtures/sample_posts.json
    ├── templates/main/ base.html · home.html · add_post.html · partials/
    └── static/main/    css/style.css · js/main.js · img/ (logo, favicon, pitch)
```
