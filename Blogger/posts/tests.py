from datetime import datetime, timedelta, timezone as datetime_timezone

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Post


class BloggerTests(TestCase):
    def test_home_shows_published_posts_newest_first(self):
        older = Post.objects.create(title="Older post", content="First content")
        Post.objects.filter(pk=older.pk).update(published_at=timezone.now() - timedelta(days=1))
        Post.objects.create(title="Newer post", content="Second content")
        Post.objects.create(title="Draft post", content="Private content", is_published=False)

        response = self.client.get(reverse("home"))

        self.assertContains(response, "First content")
        self.assertContains(response, "Second content")
        self.assertNotContains(response, "Draft post")
        self.assertLess(response.content.index(b"Newer post"), response.content.index(b"Older post"))

    def test_create_post_and_redirect_to_home(self):
        response = self.client.post(reverse("posts:create"), {"title": "A new post", "content": "Hello blog", "is_published": "true"})

        self.assertRedirects(response, reverse("home"))
        post = Post.objects.get(title="A new post")
        self.assertEqual(post.content, "Hello blog")
        self.assertTrue(post.is_published)
        self.assertIsNotNone(post.published_at)
        self.assertContains(self.client.get(reverse("home")), "A new post")

    def test_invalid_post_is_not_saved(self):
        response = self.client.post(reverse("posts:create"), {"title": "", "content": "Hello blog"})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.exists())

    def test_empty_submission_shows_errors(self):
        response = self.client.post(reverse("posts:create"), {})
        self.assertContains(response, "This field is required.")
        self.assertFalse(Post.objects.exists())

    def test_unpublished_post_is_saved_but_not_shown_on_home(self):
        response = self.client.post(reverse("posts:create"), {
            "title": "A draft", "content": "Not ready yet", "is_published": "false",
        })

        self.assertRedirects(response, reverse("home"))
        self.assertFalse(Post.objects.get(title="A draft").is_published)
        self.assertNotContains(self.client.get(reverse("home")), "A draft")

    def test_publication_choice_is_required(self):
        response = self.client.post(reverse("posts:create"), {
            "title": "A post", "content": "Some content",
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.exists())

    def test_home_displays_riyadh_time(self):
        post = Post.objects.create(title="Time test", content="Content")
        Post.objects.filter(pk=post.pk).update(
            published_at=datetime(2026, 11, 15, 22, 30, tzinfo=datetime_timezone.utc)
        )

        response = self.client.get(reverse("home"))

        self.assertContains(response, "November 16, 2026 at 1:30 AM")
