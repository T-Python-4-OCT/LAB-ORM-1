from django.test import TestCase
from django.urls import reverse
from .models import Post


class BlogTests(TestCase):
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
