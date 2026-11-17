from django.test import TestCase
from django.urls import reverse
from .models import Post
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from tempfile import TemporaryDirectory
from io import BytesIO
from PIL import Image


class BlogTests(TestCase):
    def test_edit_and_delete_confirmation(self):
        post = Post.objects.create(title="Original", content="Original content")
        response = self.client.post(reverse("posts:edit", args=[post.pk]), {
            "title": "Updated", "content": "Changed content", "is_published": "on",
        })
        self.assertRedirects(response, reverse("posts:home"))
        post.refresh_from_db()
        self.assertEqual(post.title, "Updated")
        self.assertEqual(self.client.get(reverse("posts:delete", args=[post.pk])).status_code, 200)
        self.assertTrue(Post.objects.filter(pk=post.pk).exists())
        self.assertRedirects(self.client.post(reverse("posts:delete", args=[post.pk])), reverse("posts:home"))
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())

    def test_upload_replace_clear_and_invalid_image(self):
        def picture(name):
            buffer = BytesIO()
            Image.new("RGB", (10, 10), "green").save(buffer, format="PNG")
            return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")

        with TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            data = {"title": "With image", "content": "Story", "is_published": "on"}
            self.client.post(reverse("posts:create"), {**data, "image": picture("first.png")})
            post = Post.objects.get()
            original = post.image.name
            self.assertTrue(post.image.storage.exists(original))
            self.assertContains(self.client.get(reverse("posts:home")), post.image.url)
            self.client.post(reverse("posts:edit", args=[post.pk]), {**data, "image": picture("second.png")})
            post.refresh_from_db()
            self.assertNotEqual(post.image.name, original)
            self.client.post(reverse("posts:edit", args=[post.pk]), {**data, "image-clear": "on"})
            post.refresh_from_db()
            self.assertFalse(post.image)
            response = self.client.post(reverse("posts:create"), {**data, "image": SimpleUploadedFile("fake.png", b"not an image", content_type="image/png")})
            self.assertIn("image", response.context["form"].errors)
            self.assertEqual(Post.objects.count(), 1)

    def test_home_shows_published_posts_newest_first(self):
        older = Post.objects.create(title="Older story", content="First content")
        newer = Post.objects.create(title="Newer story", content="Second content")
        Post.objects.create(title="Hidden draft", content="Private content", is_published=False)
        response = self.client.get(reverse("posts:home"))
        self.assertEqual(list(response.context["posts"]), [newer, older])
        self.assertContains(response, "First content")
        self.assertNotContains(response, "Hidden draft")

    def test_create_published_post(self):
        response = self.client.post(reverse("posts:create"), {
            "title": "A new idea", "content": "My story", "is_published": "on",
        })
        self.assertRedirects(response, reverse("posts:home"))
        post = Post.objects.get()
        self.assertTrue(post.is_published)
        self.assertIsNotNone(post.published_at)

    def test_unpublished_post_is_saved_but_hidden(self):
        self.client.post(reverse("posts:create"), {"title": "Draft", "content": "Still writing"})
        self.assertFalse(Post.objects.get().is_published)
        self.assertNotContains(self.client.get(reverse("posts:home")), "Still writing")

    def test_invalid_post_is_not_saved(self):
        for data in [{"title": "", "content": "Story"}, {"title": "x" * 2049, "content": "Story"}, {"title": "Title", "content": "   "}]:
            response = self.client.post(reverse("posts:create"), data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)
        self.assertEqual(Post.objects.count(), 0)

    def test_create_page_and_escaped_content(self):
        self.assertContains(self.client.get(reverse("posts:create")), "csrfmiddlewaretoken")
        Post.objects.create(title="<script>alert(1)</script>", content="<b>Story</b>")
        response = self.client.get(reverse("posts:home"))
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>")
