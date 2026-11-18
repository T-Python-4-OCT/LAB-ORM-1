import io
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Post

TEMP_MEDIA = tempfile.mkdtemp()


def make_image(name="test.png"):
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), "red").save(buf, "PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


def post_data(**overrides):
    data = {"title": "New post", "content": "Some body text here", "category": "tech", "is_published": "on"}
    data.update(overrides)
    return data


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class BlogTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    # ---------- Home (limiting) ----------
    def test_home_shows_latest_three_published(self):
        for i in range(5):
            Post.objects.create(title=f"Post {i}", content="Body")
        Post.objects.create(title="Hidden", content="Draft", is_published=False)
        response = self.client.get(reverse("main:home_view"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual([p.title for p in response.context["posts"]], ["Post 4", "Post 3", "Post 2"])
        self.assertNotContains(response, "Hidden")
        self.assertContains(response, "View all 5 posts")

    # ---------- All posts (filtering + ordering + count) ----------
    def test_all_posts_filter_and_order(self):
        Post.objects.create(title="Banana", content="x", category="tech")
        Post.objects.create(title="Apple", content="x", category="tech")
        Post.objects.create(title="Cherry", content="x", category="sports")
        response = self.client.get(reverse("main:all_posts_view"), {"category": "tech", "order_by": "title"})
        self.assertEqual([p.title for p in response.context["posts"]], ["Apple", "Banana"])
        self.assertEqual(response.context["count"], 2)

    def test_all_posts_ignores_bad_params(self):
        Post.objects.create(title="A", content="x")
        response = self.client.get(reverse("main:all_posts_view"), {"category": "nope", "order_by": "hack"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["count"], 1)

    # ---------- Search ----------
    def test_search(self):
        Post.objects.create(title="Learning Django", content="x")
        Post.objects.create(title="Coffee", content="I love django too")
        Post.objects.create(title="Football", content="x")
        Post.objects.create(title="Django draft", content="x", is_published=False)
        response = self.client.get(reverse("main:search_posts_view"), {"search": "django", "order_by": "title"})
        self.assertEqual([p.title for p in response.context["posts"]], ["Coffee", "Learning Django"])
        self.assertContains(response, "Search Results (2)")

    def test_search_too_short(self):
        Post.objects.create(title="Django", content="x")
        response = self.client.get(reverse("main:search_posts_view"), {"search": "dj"})
        self.assertEqual(response.context["count"], 0)
        self.assertContains(response, "at least 3 characters")

    # ---------- Create (ModelForm + validation) ----------
    def test_add_post_with_image(self):
        response = self.client.post(reverse("main:add_post_view"), post_data(image=make_image()))
        post = Post.objects.get(title="New post")
        self.assertRedirects(response, reverse("main:post_detail_view", args=[post.id]))
        self.assertTrue(post.image.name.startswith("images/test"))
        self.assertEqual(post.category, "tech")

    def test_add_post_without_image_uses_default(self):
        self.client.post(reverse("main:add_post_view"), post_data())
        self.assertEqual(Post.objects.get().image.name, "images/default.jpg")

    def test_add_post_validation(self):
        response = self.client.post(reverse("main:add_post_view"), post_data(title="ab", content="short", category="bad"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), 0)
        form = response.context["form"]
        self.assertIn("title", form.errors)
        self.assertIn("content", form.errors)
        self.assertIn("category", form.errors)

    # ---------- Detail / Update / Delete ----------
    def test_detail(self):
        post = Post.objects.create(title="Hello", content="Body", category="sports")
        response = self.client.get(reverse("main:post_detail_view", args=[post.id]))
        self.assertContains(response, "Hello")
        self.assertContains(response, "Sports")
        self.assertEqual(self.client.get(reverse("main:post_detail_view", args=[999])).status_code, 404)

    def test_update_keeps_image_when_none_uploaded(self):
        post = Post.objects.create(title="Old", content="Body")
        self.assertEqual(self.client.get(reverse("main:post_update_view", args=[post.id])).status_code, 200)
        response = self.client.post(reverse("main:post_update_view", args=[post.id]), post_data(title="Updated"))
        self.assertRedirects(response, reverse("main:post_detail_view", args=[post.id]))
        post.refresh_from_db()
        self.assertEqual(post.title, "Updated")
        self.assertEqual(post.image.name, "images/default.jpg")

    def test_update_replaces_image(self):
        post = Post.objects.create(title="Old", content="Body")
        self.client.post(reverse("main:post_update_view", args=[post.id]), post_data(image=make_image("new.png")))
        post.refresh_from_db()
        self.assertTrue(post.image.name.startswith("images/new"))

    def test_delete_requires_post(self):
        post = Post.objects.create(title="Bye", content="Body")
        url = reverse("main:post_delete_view", args=[post.id])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertRedirects(self.client.post(url), reverse("main:home_view"))
        self.assertFalse(Post.objects.exists())

    # ---------- Sample data ----------
    def test_fixture_loads(self):
        call_command("loaddata", "posts", verbosity=0)
        self.assertEqual(Post.objects.count(), 4)
        self.assertEqual(Post.objects.get(pk=3).image.name, "images/ronaldo.jpeg")
