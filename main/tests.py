from django.test import TestCase
from django.urls import reverse

from .models import Post


class BlogTests(TestCase):
    def test_home_page(self):
        Post.objects.create(title="Hello", content="First post")
        Post.objects.create(title="Hidden", content="Draft", is_published=False)
        response = self.client.get(reverse("main:home_view"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello")
        self.assertNotContains(response, "Hidden")

    def test_add_post(self):
        response = self.client.post(reverse("main:add_post_view"), {
            "title": "New", "content": "Body", "is_published": "on",
        })
        self.assertRedirects(response, reverse("main:home_view"))
        self.assertTrue(Post.objects.filter(title="New", is_published=True).exists())

    def test_add_post_invalid(self):
        response = self.client.post(reverse("main:add_post_view"), {"title": "", "content": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), 0)
