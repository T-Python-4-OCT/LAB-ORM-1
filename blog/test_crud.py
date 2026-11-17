from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Post
from datetime import date, datetime, timezone as dt_timezone

DATA = {'published_at':datetime(2026,11,16,16,0,tzinfo=dt_timezone.utc),'publisher_name':'أحمد محمد','title':'مقال تجريبي صحيح','content':'هذا محتوى طويل ومفيد لاختبار إنشاء المقال وتعديله مع الحفاظ على قواعد التحقق الأصلية.'}
class ArticleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User=get_user_model()
        cls.owner=User.objects.create_user('owner',password='a-strong-test-password')
        cls.other=User.objects.create_user('other',password='another-strong-password')
        cls.staff=User.objects.create_user('staff',is_staff=True)
        cls.post=Post.objects.create(**DATA,owner=cls.owner)
    def test_arabic_pages(self):
        self.client.cookies['django_language']='en'
        for url in ['/home/','/about/','/add/',f'/post/{self.post.pk}/']:
            response=self.client.get(url)
            self.assertEqual(response.status_code,200)
            self.assertContains(response,'lang="ar" dir="rtl"')
            self.assertNotContains(response,'set_language')
            self.assertNotContains(response,'Switch to English')
        self.assertEqual(self.client.get('/en/ar/home/?search=test')['Location'],'/home/?search=test')
        self.assertEqual(self.client.post('/i18n/setlang/').status_code,404)
    def test_create_anonymous(self):
        response=self.client.post('/add/',DATA)
        self.assertEqual(response.status_code,302)
        self.assertIsNone(Post.objects.latest('pk').owner)
    def test_create_authenticated(self):
        self.client.force_login(self.owner)
        self.client.post('/add/',DATA)
        self.assertEqual(Post.objects.latest('pk').owner,self.owner)
    def test_update_preserves_identity_and_time(self):
        self.client.force_login(self.owner)
        timestamp=self.post.published_at
        response=self.client.post(f'/post/{self.post.pk}/edit/',{**DATA,'title':'عنوان جديد صحيح'})
        self.assertRedirects(response,'/home/')
        self.post.refresh_from_db()
        self.assertEqual(self.post.published_at,timestamp)
        self.assertEqual(self.post.title,'عنوان جديد صحيح')
    def test_delete_get_does_not_delete(self):
        self.client.force_login(self.owner)
        self.assertRedirects(self.client.get(f'/post/{self.post.pk}/delete/'),f'/post/{self.post.pk}/')
        self.assertContains(self.client.get(f'/post/{self.post.pk}/'),'id="delete-dialog"')
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())
        self.assertRedirects(self.client.post(f'/post/{self.post.pk}/delete/'),'/home/')
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())
    def test_csrf(self):
        client=Client(enforce_csrf_checks=True);client.force_login(self.owner)
        for url in ['/add/',f'/post/{self.post.pk}/edit/',f'/post/{self.post.pk}/delete/','/theme/dark/']:
            self.assertEqual(client.post(url,DATA).status_code,403)
    def test_invalid_create_and_edit(self):
        self.client.force_login(self.owner)
        for url in ['/add/',f'/post/{self.post.pk}/edit/']:
            for field,value in [('publisher_name','123'),('title','@@@@@@'),('content',' '*40)]:
                response=self.client.post(url,{**DATA,field:value})
                self.assertEqual(response.status_code,200)
                self.assertTrue(response.context['form'].errors)
        self.assertEqual(Post.objects.count(),1)
    def test_drafts_and_actions(self):
        self.assertNotContains(self.client.get('/home/'),f'/post/{self.post.pk}/edit/')
        self.post.is_published=False;self.post.save()
        self.assertEqual(self.client.get(f'/post/{self.post.pk}/').status_code,404)
        self.assertNotContains(self.client.get('/home/'),DATA['title'])
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(f'/post/{self.post.pk}/').status_code,404)
    def test_search_sort(self):
        second=Post.objects.create(**{**DATA,'title':'عنوان آخر مختلف'})
        response=self.client.get('/home/',{'sort':'oldest'})
        self.assertEqual(list(response.context['posts']),[self.post,second])
        self.assertEqual(len(self.client.get('/home/',{'search':'مختلف'}).context['posts']),1)

    def test_riyadh_time(self):
        from datetime import datetime, timezone
        from blog.templatetags.riyadh import riyadh_date
        self.assertIn('3:30',riyadh_date(datetime(2026,11,16,12,30,tzinfo=timezone.utc)))

    def test_simplified_form_and_dates(self):
        self.client.force_login(self.owner)
        for url in ['/add/',f'/post/{self.post.pk}/edit/']:
            response=self.client.get(url)
            self.assertNotContains(response,'name="published_at"')
            self.assertNotContains(response,'name="featured"')
            self.assertNotContains(response,'name="feature_new"')
            self.assertNotContains(response,'name="remove_attachments"')

    def test_required_fields_create_edit(self):
        self.client.force_login(self.owner)
        for url in ['/add/',f'/post/{self.post.pk}/edit/']:
            for field in ['publisher_name','title','content']:
                data={**DATA,field:''}
                response=self.client.post(url,data)
                self.assertEqual(response.status_code,200)
                self.assertIn(field,response.context['form'].errors)
        self.assertEqual(Post.objects.count(),1)
    def test_optional_attachments_and_default_image(self):
        response=self.client.post('/add/',DATA)
        self.assertRedirects(response,'/home/')
        post=Post.objects.latest('pk')
        self.assertEqual(post.attachments.count(),0)
        self.assertTrue(post.get_image_url().startswith('/static/blog/img/'))
        from django.contrib.staticfiles import finders
        self.assertTrue(finders.find(post.get_image_url().removeprefix('/static/')))
    def test_shared_header_footer_and_english_dates(self):
        self.client.force_login(self.owner)
        from blog.templatetags.riyadh import english_date
        from datetime import date, datetime, timezone as dt_timezone
        self.assertEqual(english_date(date(2026,11,16)),'16 Nov 2026')
        for url in ['/home/','/about/','/add/',f'/post/{self.post.pk}/',f'/post/{self.post.pk}/edit/']:
            response=self.client.get(url)
            self.assertContains(response,'class="site-header"')
            self.assertContains(response,'class="site-footer-minimal"')
            self.assertContains(response,'/articles/')

    def test_separate_articles_page(self):
        response=self.client.get('/articles/',{'sort':'oldest','search':'تجريبي'})
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'blog/articles.html')
        self.assertContains(response,'sort-toggle')
        self.assertContains(self.client.get('/about/'),'/articles/')


    def test_exact_lab_fields(self):
        from django.db import models
        self.assertEqual(Post._meta.get_field('title').max_length,2048)
        self.assertIsInstance(Post._meta.get_field('content'),models.TextField)
        self.assertTrue(Post._meta.get_field('published_at').auto_now_add)
        self.assertTrue(Post._meta.get_field('is_published').default)
    def test_duplicate_retry_and_automatic_time(self):
        from django.utils import timezone
        before=timezone.now()
        self.client.post('/add/',DATA)
        post=Post.objects.latest('pk')
        self.assertGreaterEqual(post.published_at,before)
        count=Post.objects.count()
        self.client.post('/add/',DATA)
        self.assertEqual(Post.objects.count(),count)
    def test_missing_ids_and_admin(self):
        for action in ['', 'edit/', 'delete/']:
            self.assertEqual(self.client.get('/post/999999/'+action).status_code,404)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get('/admin/').status_code,200)

    def test_public_management_explicit_policy(self):
        self.client.logout()
        self.assertContains(self.client.get(f'/post/{self.post.pk}/'),'data-delete-open')
        self.assertRedirects(self.client.post(f'/post/{self.post.pk}/edit/',{**DATA,'title':'تعديل من زائر'}),'/home/')
        self.assertRedirects(self.client.post(f'/post/{self.post.pk}/delete/'),'/home/')
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())
    def test_public_cannot_manage_drafts(self):
        self.post.is_published=False;self.post.save()
        for action in ['edit','delete']:
            for method in ['get','post']:
                self.assertEqual(getattr(self.client,method)(f'/post/{self.post.pk}/{action}/',DATA).status_code,404)
