from datetime import timedelta

from django.test import TestCase
from django.urls import reverse

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
