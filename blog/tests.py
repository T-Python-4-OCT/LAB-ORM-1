
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Post


class PostTests(TestCase):

    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/home.html')

    def test_home_displays_published_posts(self):
        Post.objects.create(
            title='Published Post',
            content='This post is visible.'
        )

        Post.objects.create(
            title='Unpublished Post',
            content='This post is hidden.',
            is_published=False
        )

        response = self.client.get(reverse('home'))

        self.assertContains(response, 'Published Post')
        self.assertNotContains(response, 'Unpublished Post')

    def test_latest_posts_appear_first(self):
        older = Post.objects.create(
            title='Older Post',
            content='Older content.'
        )

        newer = Post.objects.create(
            title='Newer Post',
            content='Newer content.'
        )

        response = self.client.get(reverse('home'))
        posts = list(response.context['posts'])

        self.assertEqual(posts[0], newer)
        self.assertEqual(posts[1], older)

    def test_add_post_page_loads(self):
        response = self.client.get(reverse('add_post'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/add_post.html')

    def test_create_post_successfully(self):
        response = self.client.post(
            reverse('add_post'),
            {
                'title': 'My First Test Post',
                'content': 'This is a test post.',
                'image': SimpleUploadedFile(
                    'test.jpg',
                    b'test image content',
                    content_type='image/jpeg'
                )
            }
        )

        self.assertEqual(Post.objects.count(), 1)

        post = Post.objects.first()

        self.assertEqual(post.title, 'My First Test Post')
        self.assertEqual(post.content, 'This is a test post.')
        self.assertTrue(post.is_published)

        self.assertRedirects(response, reverse('home'))

    def test_empty_post_is_rejected(self):
        response = self.client.post(
            reverse('add_post'),
            {
                'title': '   ',
                'content': '   '
            }
        )

        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please fill in both fields.')

    def test_title_over_2048_characters_is_rejected(self):
        response = self.client.post(
            reverse('add_post'),
            {
                'title': 'A' * 2049,
                'content': 'Test content.',
                'image': SimpleUploadedFile(
                    'test.jpg',
                    b'test image content',
                    content_type='image/jpeg'
                )
            }
        )

        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'The title must not exceed 2048 characters.'
        )



    def test_post_detail_page_loads(self):
        post = Post.objects.create(
            title='Detail Test',
            content='Testing post details.'
        )

        response = self.client.get(
            reverse('post_detail', args=[post.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Detail Test')
        self.assertTemplateUsed(response, 'blog/post_detail.html')

    def test_edit_post_page_loads(self):
        post = Post.objects.create(
            title='Edit Test',
            content='Original content.'
        )

        response = self.client.get(
            reverse('edit_post', args=[post.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/edit_post.html')

    def test_edit_post_successfully(self):
        post = Post.objects.create(
            title='Old Title',
            content='Old content.'
        )

        response = self.client.post(
            reverse('edit_post', args=[post.pk]),
            {
                'title': 'New Title',
                'content': 'New content.'
            }
        )

        post.refresh_from_db()

        self.assertEqual(post.title, 'New Title')
        self.assertEqual(post.content, 'New content.')
        self.assertRedirects(
            response,
            reverse('post_detail', args=[post.pk])
        )

    def test_delete_confirmation_page_loads(self):
        post = Post.objects.create(
            title='Delete Test',
            content='Testing deletion.'
        )

        response = self.client.get(
            reverse('delete_post', args=[post.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/delete_post.html')
        self.assertEqual(Post.objects.count(), 1)

    def test_delete_post_successfully(self):
        post = Post.objects.create(
            title='Delete Test',
            content='Testing deletion.'
        )

        response = self.client.post(
            reverse('delete_post', args=[post.pk])
        )

        self.assertEqual(Post.objects.count(), 0)
        self.assertRedirects(response, reverse('home'))
