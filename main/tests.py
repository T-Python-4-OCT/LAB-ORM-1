import io
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Post

TEMP_MEDIA = tempfile.mkdtemp()


def make_image(name="test.png"):
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), "red").save(buf, "PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class BlogTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def test_home_page(self):
        Post.objects.create(title="Hello", content="First post")
        Post.objects.create(title="Hidden", content="Draft", is_published=False)
        response = self.client.get(reverse("main:home_view"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello")
        self.assertNotContains(response, "Hidden")
        self.assertContains(response, "images/default.jpg")

    def test_add_post_with_image(self):
        response = self.client.post(reverse("main:add_post_view"), {
            "title": "New", "content": "Body", "is_published": "on", "image": make_image(),
        })
        post = Post.objects.get(title="New")
        self.assertRedirects(response, reverse("main:post_detail_view", args=[post.id]))
        self.assertTrue(post.image.name.startswith("images/test"))

    def test_add_post_without_image_uses_default(self):
        self.client.post(reverse("main:add_post_view"), {"title": "New", "content": "Body"})
        self.assertEqual(Post.objects.get().image.name, "images/default.jpg")

    def test_add_post_invalid(self):
        response = self.client.post(reverse("main:add_post_view"), {"title": "", "content": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), 0)

    def test_detail(self):
        post = Post.objects.create(title="Hello", content="Body")
        response = self.client.get(reverse("main:post_detail_view", args=[post.id]))
        self.assertContains(response, "Hello")
        self.assertEqual(self.client.get(reverse("main:post_detail_view", args=[999])).status_code, 404)

    def test_update_keeps_image_when_none_uploaded(self):
        post = Post.objects.create(title="Old", content="Body")
        response = self.client.post(reverse("main:post_update_view", args=[post.id]), {
            "title": "Updated", "content": "New body", "is_published": "on",
        })
        self.assertRedirects(response, reverse("main:post_detail_view", args=[post.id]))
        post.refresh_from_db()
        self.assertEqual(post.title, "Updated")
        self.assertEqual(post.image.name, "images/default.jpg")

    def test_update_replaces_image(self):
        post = Post.objects.create(title="Old", content="Body")
        self.client.post(reverse("main:post_update_view", args=[post.id]), {
            "title": "Old", "content": "Body", "image": make_image("new.png"),
        })
        post.refresh_from_db()
        self.assertTrue(post.image.name.startswith("images/new"))

    def test_delete_requires_post(self):
        post = Post.objects.create(title="Bye", content="Body")
        url = reverse("main:post_delete_view", args=[post.id])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertRedirects(self.client.post(url), reverse("main:home_view"))
        self.assertFalse(Post.objects.exists())
