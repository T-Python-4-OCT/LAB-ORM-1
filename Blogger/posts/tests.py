import base64
from datetime import datetime, timedelta, timezone as datetime_timezone
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Comment, Post


class CommentTests(TestCase):
    def setUp(self):
        self.post = Post.objects.create(title="Game review", content="Review")
        self.url = reverse("posts:detail", args=[self.post.pk])

    def test_comment_is_saved_on_current_post_and_refresh_does_not_resubmit(self):
        other = Post.objects.create(title="Other review", content="Other")
        response = self.client.post(self.url, {
            "name": " Reader ", "content": " Great review! ", "post": other.pk,
        })
        comment = Comment.objects.get()
        self.assertEqual((comment.post, comment.name, comment.content), (self.post, "Reader", "Great review!"))
        self.assertRedirects(response, self.url + f"#comment-{comment.pk}")
        self.assertContains(self.client.get(self.url), "Great review!")
        self.assertEqual(Comment.objects.count(), 1)
        self.assertNotContains(self.client.get(reverse("posts:detail", args=[other.pk])), "Great review!")

    def test_blank_and_oversized_comments_are_rejected(self):
        for data in [{}, {"name": " ", "content": " "}, {"name": "x" * 81, "content": "Text"}, {"name": "Reader", "content": "x" * 2001}]:
            with self.subTest(data=data):
                response = self.client.post(self.url, data)
                self.assertContains(response, "Check the fields below")
                self.assertTrue(response.context["comment_form"].errors)
                self.assertFalse(Comment.objects.exists())

    def test_draft_and_missing_posts_reject_comments(self):
        self.post.is_published = False
        self.post.save()
        for pk in [self.post.pk, self.post.pk + 100]:
            response = self.client.post(reverse("posts:detail", args=[pk]), {"name": "Reader", "content": "Text"})
            self.assertEqual(response.status_code, 404)
        self.assertFalse(Comment.objects.exists())

    def test_comment_text_is_escaped_and_csrf_is_required(self):
        Comment.objects.create(post=self.post, name="<b>Reader</b>", content="<script>alert(1)</script>")
        response = self.client.get(self.url)
        self.assertContains(response, "&lt;b&gt;Reader&lt;/b&gt;")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")
        response = Client(enforce_csrf_checks=True).post(self.url, {"name": "Reader", "content": "Text"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.count(), 1)


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

    def test_edit_draft_with_image(self):
        post = Post.objects.create(title="Draft", content="Text", is_published=False)
        edit_url = reverse("posts:edit", args=[post.pk])
        self.assertContains(self.client.get(reverse("posts:list")), "Draft")
        self.assertContains(self.client.get(edit_url), '<option value="false" selected>Not published</option>', html=True)
        image = SimpleUploadedFile(
            "game.gif",
            base64.b64decode("R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="),
            content_type="image/gif",
        )
        with TemporaryDirectory() as media_dir, override_settings(MEDIA_ROOT=media_dir):
            response = self.client.post(edit_url, {
                "title": "Updated", "content": "Text", "is_published": "true", "image": image,
            })
            self.assertRedirects(response, reverse("posts:list"))
            post.refresh_from_db()
            self.assertTrue(post.is_published)
            self.assertTrue(post.image.name.startswith("images/"))
            self.assertTrue(post.image.storage.exists(post.image.name))
            self.assertContains(self.client.get(reverse("home")), post.image.url)

    def test_delete_requires_post_confirmation(self):
        post = Post.objects.create(title="Delete me", content="Text")
        url = reverse("posts:delete", args=[post.pk])
        self.assertContains(self.client.get(url), "Delete me")
        self.assertTrue(Post.objects.filter(pk=post.pk).exists())
        self.assertRedirects(self.client.post(url), reverse("posts:list"))
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())

    def test_post_without_image_uses_default(self):
        Post.objects.create(title="No image", content="Text")
        self.assertContains(self.client.get(reverse("home")), "/media/images/default.png")

    def test_new_post_image_uses_images_folder(self):
        image = SimpleUploadedFile(
            "game.gif",
            base64.b64decode("R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="),
            content_type="image/gif",
        )
        with TemporaryDirectory() as media_dir, override_settings(MEDIA_ROOT=media_dir):
            response = self.client.post(reverse("posts:create"), {
                "title": "New game", "content": "Text", "is_published": "true", "image": image,
            })
            self.assertRedirects(response, reverse("home"))
            post = Post.objects.get(title="New game")
            self.assertTrue(post.image.name.startswith("images/"))
            self.assertTrue(post.image.storage.exists(post.image.name))

    def test_long_post_has_excerpt_and_full_detail_page(self):
        post = Post.objects.create(title="Long post", content="A" * 180 + " ENDING")
        response = self.client.get(reverse("home"))
        self.assertContains(response, reverse("posts:detail", args=[post.pk]))
        self.assertNotContains(response, "ENDING")
        self.assertContains(self.client.get(reverse("posts:detail", args=[post.pk])), "ENDING")

    def test_short_post_has_read_more_and_draft_is_not_public(self):
        post = Post.objects.create(title="Short post", content="A" * 180)
        draft = Post.objects.create(title="Draft", content="Secret", is_published=False)
        self.assertContains(self.client.get(reverse("home")), f'href="{reverse("posts:detail", args=[post.pk])}"')
        self.assertEqual(self.client.get(reverse("posts:detail", args=[draft.pk])).status_code, 404)

    def test_filter_order_and_limit_rated_posts(self):
        for rating in [1, 2, 3, 4, 5, 5]:
            Post.objects.create(title=f"Game {rating}", content="Text", rating=rating)
        Post.objects.create(title="Draft", content="Text", rating=5, is_published=False)
        response = self.client.get(reverse("home"), {"rating": "2", "order": "rating", "limit": "5"})
        self.assertEqual([post.rating for post in response.context["posts"]], [5, 5, 4, 3, 2])
        self.assertNotContains(response, "Draft")

    def test_invalid_rating_is_rejected(self):
        response = self.client.post(reverse("posts:create"), {"title": "Game", "content": "Text", "rating": "9", "is_published": "true"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(title="Game").exists())
