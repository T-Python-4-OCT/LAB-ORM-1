import io
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Post

TEMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class PostImageUploadTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def make_image(self):
        buffer = io.BytesIO()
        Image.new("RGB", (40, 30), "red").save(buffer, format="PNG")
        return SimpleUploadedFile("cover.png", buffer.getvalue(), content_type="image/png")

    def test_post_with_image_is_saved_and_shown(self):
        self.client.post(reverse("posts:add_post_view"), {
            "title": "With image", "content": "Hello there friends", "category": "news", "is_published": "on", "image": self.make_image(),
        })
        post = Post.objects.get()
        self.assertTrue(post.image.name.startswith("posts/images/"))

        home = self.client.get(reverse("main:home_view"))
        self.assertContains(home, post.image.url)

    def test_post_without_image_still_works(self):
        self.client.post(reverse("posts:add_post_view"), {"title": "No image", "content": "Hello there friends", "category": "news", "is_published": "on"})
        post = Post.objects.get()
        self.assertFalse(post.image)
        self.assertEqual(self.client.get(reverse("main:home_view")).status_code, 200)


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class PostUpdateDeleteTests(TestCase):

    def make_image(self, name="cover.png"):
        buffer = io.BytesIO()
        Image.new("RGB", (40, 30), "blue").save(buffer, format="PNG")
        return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")

    def setUp(self):
        self.post = Post.objects.create(title="Old title", content="Old content", image=self.make_image())

    def test_edit_page_is_filled_with_the_post(self):
        page = self.client.get(reverse("posts:update_post_view", args=[self.post.id]))
        self.assertContains(page, 'value="Old title"')
        self.assertContains(page, "Old content")

    def test_update_changes_text_and_replaces_image(self):
        old_image_name = self.post.image.name
        self.client.post(reverse("posts:update_post_view", args=[self.post.id]), {
            "title": "New title", "content": "New content here", "category": "history", "image": self.make_image("new.png"),
        })
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "New title")
        self.assertEqual(self.post.category, Post.Category.HISTORY)
        self.assertFalse(self.post.is_published)
        self.assertNotEqual(self.post.image.name, old_image_name)
        self.assertFalse(self.post.image.storage.exists(old_image_name))

    def test_update_can_remove_image(self):
        self.client.post(reverse("posts:update_post_view", args=[self.post.id]), {
            "title": "Title", "content": "Some content here", "category": "news", "is_published": "on", "remove_image": "on",
        })
        self.post.refresh_from_db()
        self.assertFalse(self.post.image)

    def test_delete_removes_post_and_image_file(self):
        image_name = self.post.image.name
        response = self.client.post(reverse("posts:delete_post_view", args=[self.post.id]))
        self.assertRedirects(response, reverse("main:home_view"))
        self.assertFalse(Post.objects.exists())
        self.assertFalse(self.post.image.storage.exists(image_name))

    def test_opening_delete_link_only_asks_for_confirmation(self):
        response = self.client.get(reverse("posts:delete_post_view", args=[self.post.id]))
        self.assertContains(response, "Are you sure")
        self.assertTrue(Post.objects.exists())

    def test_detail_page_shows_the_post(self):
        page = self.client.get(reverse("posts:post_detail_view", args=[self.post.id]))
        self.assertContains(page, "Old title")
        self.assertContains(page, self.post.image.url)

    def test_missing_post_gives_404(self):
        self.assertEqual(self.client.get(reverse("posts:update_post_view", args=[999])).status_code, 404)


class PostChoicesAndSearchTests(TestCase):

    def setUp(self):
        Post.objects.create(title="Messi lifts the ten", content="A night to remember", category=Post.Category.NEWS)
        Post.objects.create(title="Cruyff dream team", content="How it all started", category=Post.Category.HISTORY)
        Post.objects.create(title="Hidden draft", content="Not ready yet", category=Post.Category.NEWS, is_published=False)

    def test_default_category_and_label(self):
        post = Post.objects.create(title="Plain", content="No category given")
        self.assertEqual(post.category, Post.Category.OTHER)
        self.assertEqual(post.get_category_display(), "Other")

    def test_add_page_lists_all_categories(self):
        page = self.client.get(reverse("posts:add_post_view"))
        for value, label in Post.Category.choices:
            self.assertContains(page, f'value="{value}"')

    def test_invalid_form_shows_errors_and_saves_nothing(self):
        response = self.client.post(reverse("posts:add_post_view"), {"title": "Hi", "content": "short", "category": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "at least 3 characters")
        self.assertContains(response, "at least 3 words")
        self.assertEqual(Post.objects.count(), 3)

    def test_search_by_word(self):
        response = self.client.get(reverse("posts:search_posts_view"), {"search": "messi"})
        self.assertContains(response, "Messi lifts the ten")
        self.assertNotContains(response, "Cruyff dream team")

    def test_filter_by_category(self):
        response = self.client.get(reverse("posts:search_posts_view"), {"category": "history"})
        self.assertContains(response, "Cruyff dream team")
        self.assertNotContains(response, "Messi lifts the ten")

    def test_search_hides_drafts(self):
        response = self.client.get(reverse("posts:search_posts_view"), {"search": "draft"})
        self.assertNotContains(response, "Hidden draft")
        self.assertContains(response, "No posts match your search")
