from django.core.management.base import BaseCommand
from posts.models import Post


class Command(BaseCommand):
    help = "Add labelled demo posts without replacing or duplicating existing content."

    def handle(self, *args, **options):
        Post.objects.filter(title__in=[
            "تيفو الهلال المرعب", "تيفو الهلال — BLUE POWER", "تيفو الهلال — عشق لا ينتهي",
        ], category=Post.Category.GENERAL).update(category=Post.Category.SPORTS)
        examples = [
            ("كيف يعمل Django ORM؟", "الموديل يمثل جدولًا، والكائن يمثل صفًا. نستخدم Python لإضافة البيانات واسترجاعها وتعديلها وحذفها.", "technology", True),
            ("الفرق بين filter وall", "all تجلب جميع السجلات، وfilter تختار النتائج المطابقة لشروط محددة. جرّب فلتر Technology.", "technology", True),
            ("يوم تعلّمت فيه البرمجة", "منشور تجريبي بتصنيف Daily life لتوضيح عمل قائمة التصنيفات.", "daily", True),
            ("تنظيم وقت الدراسة", "قسّم وقتك بين قراءة الدرس والتطبيق العملي ومراجعة الأخطاء. جرّب تغيير ترتيب النتائج.", "daily", True),
            ("مرحبًا في Blogger", "مدونة تطبق الإضافة والعرض والتعديل والحذف، مع الصور والتصنيفات والبحث وتقسيم الصفحات.", "general", True),
            ("مسودة لم تُنشر بعد", "مسودة تجريبية تظهر في الإدارة تحت Draft وتُستبعد من الصفحة الرئيسية.", "general", False),
        ]
        created_count = 0
        for title, content, category, published in examples:
            _, created = Post.objects.get_or_create(title=f"مثال تعليمي: {title}", defaults={
                "content": content, "category": category, "is_published": published,
            })
            created_count += created
        self.stdout.write(self.style.SUCCESS(f"Added {created_count} demo posts."))
