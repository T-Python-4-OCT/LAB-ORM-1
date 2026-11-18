from django.test import TestCase
from django.urls import reverse
from posts.models import Post


class SearchTests(TestCase):
    def test_search_matches_title_and_content_and_excludes_drafts(self):
        title_match = Post.objects.create(title="Hollow Knight", content="A review")
        content_match = Post.objects.create(title="My favorites", content="Try Hollow Knight")
        Post.objects.create(title="Hollow draft", content="Private", is_published=False)
        Post.objects.create(title="Other game", content="Unrelated")

        response = self.client.get(reverse("search"), {"q": "  hOlLoW  "})

        self.assertEqual(list(response.context["posts"]), [content_match, title_match])
        self.assertContains(response, "2 results")
        self.assertNotContains(response, "Hollow draft")
        self.assertContains(response, reverse("posts:detail", args=[title_match.pk]))

    def test_empty_search_and_no_matches_have_distinct_guidance(self):
        Post.objects.create(title="Existing game", content="Text")
        for query in ["", "   "]:
            response = self.client.get(reverse("search"), {"q": query})
            self.assertContains(response, "What are you looking for?")
            self.assertFalse(response.context["posts"].exists())
        response = self.client.get(reverse("search"), {"q": "missing"})
        self.assertContains(response, "No matching posts")

    def test_long_query_is_rejected_and_html_is_escaped(self):
        response = self.client.get(reverse("search"), {"q": "a" * 201})
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(response.context["posts"].exists())
        response = self.client.get(reverse("search"), {"q": "<script>alert(1)</script>"})
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "&lt;script&gt;")
