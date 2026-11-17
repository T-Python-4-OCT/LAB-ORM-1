import io
import tempfile
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

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
            "title": "الضغط العالي", "content": "تحليل تكتيكي", "is_published": "on",
        })
        self.assertRedirects(res, reverse("main:home"))
        self.assertEqual(Post.objects.count(), 1)

    def test_add_post_invalid_shows_errors(self):
        res = self.client.post(reverse("main:add_post"), {"title": "", "content": ""})
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
            "title": "مقال بصورة", "content": "نص", "is_published": "on", "image": self._image(),
        })
        self.assertRedirects(res, reverse("main:home"))
        post = Post.objects.get()
        self.assertTrue(post.image.name.startswith("posts/"))
        home = self.client.get(reverse("main:home"))
        self.assertContains(home, post.image.url)

    def test_post_without_image_gets_default(self):
        self.client.post(reverse("main:add_post"), {"title": "بدون صورة", "content": "نص", "is_published": "on"})
        self.assertEqual(Post.objects.get().image.name, "posts/default.jpg")

    def test_non_image_file_is_rejected(self):
        bad = SimpleUploadedFile("notes.txt", b"not an image", content_type="text/plain")
        res = self.client.post(reverse("main:add_post"), {"title": "ملف خطأ", "content": "نص", "image": bad})
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
            "title": "عنوان جديد", "content": "نص جديد", "is_published": "on",
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
            "title": "عنوان", "content": "نص", "is_published": "on",
        })
        self.post.refresh_from_db()
        self.assertEqual(self.post.image.name, "posts/my-photo.jpg")

    def test_update_invalid_shows_errors(self):
        res = self.client.post(reverse("main:update_post", args=[self.post.id]), {"title": "", "content": ""})
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
