import io
import tempfile
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from PIL import Image

from .models import Post


class BloggerTests(TestCase):
    def test_home_shows_only_published_posts_newest_first(self):
        old = Post.objects.create(title="مقال قديم", content="نص")
        Post.objects.create(title="مقال جديد", content="نص")
        Post.objects.create(title="مسودة", content="نص", is_published=False)
        # auto_now_add يمنع تحديد الوقت عند الإنشاء، فنرجع المقال القديم يوماً بالتحديث
        Post.objects.filter(pk=old.pk).update(published_at=old.published_at - timedelta(days=1))

        res = self.client.get(reverse("main:home"))

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "مقال جديد")
        self.assertNotContains(res, "مسودة")
        titles = [p.title for p in res.context["posts"]]
        self.assertEqual(titles, ["مقال جديد", "مقال قديم"])

    def test_defaults(self):
        post = Post.objects.create(title="عنوان", content="نص")
        self.assertTrue(post.is_published)
        self.assertIsNotNone(post.published_at)

    def test_add_post_page_renders(self):
        res = self.client.get(reverse("main:add_post"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "csrfmiddlewaretoken")

    def test_add_post_creates_and_redirects(self):
        res = self.client.post(reverse("main:add_post"), {
            "category": "general", "title": "الضغط العالي", "content": "تحليل تكتيكي", "is_published": "on",
        })
        self.assertRedirects(res, reverse("main:home"))
        self.assertEqual(Post.objects.count(), 1)

    def test_add_post_invalid_shows_errors(self):
        res = self.client.post(reverse("main:add_post"), {"category": "general", "title": "", "content": ""})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Post.objects.count(), 0)
        self.assertContains(res, "اكتب عنواناً للمقال.")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PostImageTests(TestCase):
    def _image(self):
        buf = io.BytesIO()
        Image.new("RGB", (40, 20), "green").save(buf, format="PNG")
        return SimpleUploadedFile("pitch.png", buf.getvalue(), content_type="image/png")

    def test_add_post_with_image_saves_and_shows_it(self):
        res = self.client.post(reverse("main:add_post"), {
            "category": "general", "title": "مقال بصورة", "content": "نص", "is_published": "on", "image": self._image(),
        })
        self.assertRedirects(res, reverse("main:home"))
        post = Post.objects.get()
        self.assertTrue(post.image.name.startswith("posts/"))
        home = self.client.get(reverse("main:home"))
        self.assertContains(home, post.image.url)

    def test_post_without_image_gets_default(self):
        self.client.post(reverse("main:add_post"), {"category": "general", "title": "بدون صورة", "content": "نص", "is_published": "on"})
        self.assertEqual(Post.objects.get().image.name, "posts/default.jpg")

    def test_non_image_file_is_rejected(self):
        bad = SimpleUploadedFile("notes.txt", b"not an image", content_type="text/plain")
        res = self.client.post(reverse("main:add_post"), {"category": "general", "title": "ملف خطأ", "content": "نص", "image": bad})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Post.objects.count(), 0)
        self.assertContains(res, "الملف ليس صورة صالحة")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PostDetailUpdateDeleteTests(TestCase):
    def setUp(self):
        self.post = Post.objects.create(title="البناء من الخلف", content="الفقرة الأولى\n\nالفقرة الثانية")

    # ---- detail ----
    def test_detail_shows_full_post_and_buttons(self):
        res = self.client.get(reverse("main:post_detail", args=[self.post.id]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "البناء من الخلف")
        self.assertContains(res, "الفقرة الثانية")
        self.assertContains(res, reverse("main:update_post", args=[self.post.id]))
        self.assertContains(res, reverse("main:delete_post", args=[self.post.id]))

    def test_detail_404_for_missing_post(self):
        res = self.client.get(reverse("main:post_detail", args=[999]))
        self.assertEqual(res.status_code, 404)

    def test_home_cards_link_to_detail(self):
        res = self.client.get(reverse("main:home"))
        self.assertContains(res, reverse("main:post_detail", args=[self.post.id]))

    # ---- update ----
    def test_update_form_is_prefilled(self):
        res = self.client.get(reverse("main:update_post", args=[self.post.id]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'value="البناء من الخلف"')

    def test_update_saves_changes_and_keeps_date(self):
        old_date = self.post.published_at
        res = self.client.post(reverse("main:update_post", args=[self.post.id]), {
            "category": "general", "title": "عنوان جديد", "content": "نص جديد", "is_published": "on",
        })
        self.assertRedirects(res, reverse("main:post_detail", args=[self.post.id]))
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "عنوان جديد")
        self.assertEqual(self.post.content, "نص جديد")
        self.assertEqual(self.post.published_at, old_date)
        self.assertEqual(Post.objects.count(), 1)  # updated, not duplicated

    def test_update_without_new_image_keeps_current_image(self):
        self.post.image = "posts/my-photo.jpg"
        self.post.save()
        self.client.post(reverse("main:update_post", args=[self.post.id]), {
            "category": "general", "title": "عنوان", "content": "نص", "is_published": "on",
        })
        self.post.refresh_from_db()
        self.assertEqual(self.post.image.name, "posts/my-photo.jpg")

    def test_update_invalid_shows_errors(self):
        res = self.client.post(reverse("main:update_post", args=[self.post.id]), {"category": "general", "title": "", "content": ""})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "اكتب عنواناً للمقال.")
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "البناء من الخلف")

    # ---- delete ----
    def test_delete_get_only_asks_for_confirmation(self):
        res = self.client.get(reverse("main:delete_post", args=[self.post.id]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "هل أنت متأكد")
        self.assertTrue(Post.objects.filter(pk=self.post.id).exists())

    def test_delete_post_removes_and_redirects(self):
        res = self.client.post(reverse("main:delete_post", args=[self.post.id]))
        self.assertRedirects(res, reverse("main:home"))
        self.assertFalse(Post.objects.filter(pk=self.post.id).exists())


class HomeLimitAndAllPostsTests(TestCase):
    def setUp(self):
        base = timezone.now()
        for i in range(5):  # posts 1..5, post 5 is the newest
            p = Post.objects.create(title=f"مقال رقم {i + 1}", content="نص")
            Post.objects.filter(pk=p.pk).update(published_at=base - timedelta(hours=5 - i))
        Post.objects.create(title="مسودة مخفية", content="نص", is_published=False)

    def test_home_shows_only_latest_three(self):
        res = self.client.get(reverse("main:home"))
        titles = [p.title for p in res.context["posts"]]
        self.assertEqual(titles, ["مقال رقم 5", "مقال رقم 4", "مقال رقم 3"])
        self.assertNotContains(res, "مقال رقم 2")
        self.assertEqual(res.context["posts_count"], 5)
        self.assertContains(res, reverse("main:all_posts"))

    def test_all_posts_page_lists_every_published_post(self):
        res = self.client.get(reverse("main:all_posts"))
        self.assertEqual(res.status_code, 200)
        titles = [p.title for p in res.context["posts"]]
        self.assertEqual(titles, [f"مقال رقم {i}" for i in range(5, 0, -1)])
        self.assertNotContains(res, "مسودة مخفية")
        self.assertContains(res, reverse("main:post_detail", args=[res.context["posts"][0].id]))


class CategoryFilterTests(TestCase):
    def setUp(self):
        Post.objects.create(title="خطة 4-3-3", content="نص", category=Post.Category.TACTICS)
        Post.objects.create(title="قانون التسلل", content="نص", category=Post.Category.REFEREEING)
        Post.objects.create(title="تمارين السرعة", content="نص", category=Post.Category.TRAINING)

    def test_new_post_default_category_is_general(self):
        self.assertEqual(Post.objects.create(title="ع", content="ن").category, "general")

    def test_filter_by_category(self):
        res = self.client.get(reverse("main:all_posts"), {"category": "refereeing"})
        self.assertEqual([p.title for p in res.context["posts"]], ["قانون التسلل"])
        self.assertEqual(res.context["current_category"], "refereeing")

    def test_unknown_category_shows_all(self):
        res = self.client.get(reverse("main:all_posts"), {"category": "xyz"})
        self.assertEqual(len(res.context["posts"]), 3)
        self.assertIsNone(res.context["current_category"])

    def test_add_post_saves_category_and_card_shows_it(self):
        self.client.post(reverse("main:add_post"), {
            "title": "ركلات الجزاء", "content": "نص", "category": "refereeing", "is_published": "on",
        })
        self.assertEqual(Post.objects.get(title="ركلات الجزاء").category, "refereeing")
        self.assertContains(self.client.get(reverse("main:home")), "التحكيم والقوانين")


class SortPostsTests(TestCase):
    def setUp(self):
        base = timezone.now()
        data = [("أقدم مقال", "tactics", 3), ("مقال متوسط", "training", 2), ("أحدث مقال", "tactics", 1)]
        for title, cat, hours_ago in data:
            p = Post.objects.create(title=title, content="نص", category=cat)
            Post.objects.filter(pk=p.pk).update(published_at=base - timedelta(hours=hours_ago))

    def titles(self, **params):
        res = self.client.get(reverse("main:all_posts"), params)
        return [p.title for p in res.context["posts"]], res

    def test_default_is_newest_first(self):
        titles, res = self.titles()
        self.assertEqual(titles, ["أحدث مقال", "مقال متوسط", "أقدم مقال"])
        self.assertEqual(res.context["current_sort"], "newest")

    def test_oldest_first(self):
        titles, _ = self.titles(sort="oldest")
        self.assertEqual(titles, ["أقدم مقال", "مقال متوسط", "أحدث مقال"])

    def test_unknown_sort_falls_back_to_newest(self):
        titles, _ = self.titles(sort="xyz")
        self.assertEqual(titles[0], "أحدث مقال")

    def test_sort_works_with_category_filter(self):
        titles, res = self.titles(category="tactics", sort="oldest")
        self.assertEqual(titles, ["أقدم مقال", "أحدث مقال"])
        # category links keep the sort, sort links keep the category
        self.assertContains(res, "?category=training&amp;sort=oldest")
        self.assertContains(res, "?category=tactics")
