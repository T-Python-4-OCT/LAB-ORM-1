from django.test import TestCase
from django.urls import reverse
from .models import Post
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from tempfile import TemporaryDirectory
from io import BytesIO
from PIL import Image


class BlogTests(TestCase):
    def test_repeatable_demo_data(self):
        from django.core.management import call_command
        from io import StringIO

        call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual(Post.objects.count(), 6)
        self.assertEqual(Post.objects.filter(is_published=False).count(), 1)

    def test_search_category_sort_and_count(self):
        older = Post.objects.create(title="Hilal story", content="Football", category="sports")
        newer = Post.objects.create(title="Another story", content="Hilal fans", category="sports")
        Post.objects.create(title="Hilal technology", content="Computers", category="technology")
        Post.objects.create(title="Hilal draft", content="Hidden", category="sports", is_published=False)
        response = self.client.get(reverse("posts:home"), {"q": "hilal", "category": "sports", "sort": "oldest"})
        self.assertEqual(list(response.context["posts"]), [older, newer])
        self.assertEqual(response.context["result_count"], 2)
        self.assertContains(response, "رياضة")

    def test_search_finds_arabic_and_english_category_names(self):
        tech = Post.objects.create(title="Django ORM", content="Programming", category="technology")
        Post.objects.create(title="Football", content="Match", category="sports")
        Post.objects.create(title="Hidden", content="Text", category="technology", is_published=False)
        for query in ("تقنية", "التقنية", "التقنيه", "technology", "Tech"):
            response = self.client.get(reverse("posts:home"), {"q": query})
            self.assertEqual(list(response.context["posts"]), [tech])
        response = self.client.get(reverse("posts:home"), {"q": "التقنية", "category": "sports"})
        self.assertEqual(response.context["result_count"], 0)

    def test_pagination_preserves_filters_and_handles_invalid_page(self):
        for number in range(8):
            Post.objects.create(title=f"Story {number}", content="Text", category="sports")
        response = self.client.get(reverse("posts:home"), {"category": "sports"})
        self.assertEqual(len(response.context["posts"]), 6)
        self.assertEqual(response.context["result_count"], 8)
        self.assertContains(response, "category=sports&amp;page=2")
        response = self.client.get(reverse("posts:home"), {"category": "sports", "page": 2})
        self.assertEqual(len(response.context["posts"]), 2)
        self.assertEqual(self.client.get(reverse("posts:home"), {"page": "bad", "sort": "bad"}).status_code, 200)

    def test_manage_draft_filter_and_category_validation(self):
        draft = Post.objects.create(title="Draft", content="Text", is_published=False)
        Post.objects.create(title="Published", content="Text")
        response = self.client.get(reverse("posts:manage"), {"status": "draft"})
        self.assertEqual(list(response.context["posts"]), [draft])
        response = self.client.post(reverse("posts:create"), {"title": "Invalid", "content": "Text", "category": "unknown"})
        self.assertIn("category", response.context["form"].errors)

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
