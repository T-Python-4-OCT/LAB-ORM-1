from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Post
from .forms import PostForm
from .validators import validate_publisher_name, validate_article_title, validate_article_content


class ValidationUnitTests(TestCase):
    def test_publisher_name_valid(self):
        valid_names = [
            "أحمد محمد",
            "ليان خالد",
            "عمر الحربي",
            "John Smith",
            "Mary Jane",
            "Jean-Luc",
            "O'Connor"
        ]
        for name in valid_names:
            try:
                validate_publisher_name(name)
            except ValidationError as e:
                self.fail(f"Publisher name '{name}' raised ValidationError unexpectedly: {e}")

    def test_publisher_name_invalid(self):
        invalid_names = [
            "",
            "   ",
            "1",
            "123456",
            "999",
            "@@@@",
            "###!!",
            "Ahmed123",
            "أحمد123"
        ]
        for name in invalid_names:
            with self.assertRaises(ValidationError, msg=f"Expected ValidationError for publisher name: '{name}'"):
                validate_publisher_name(name)

    def test_title_valid(self):
        valid_titles = [
            "القراءة في زمن السرعة",
            "حين تتكلم المدن بصمت",
            "أفضل 10 كتب لعام 2026",
            "Learning Django ORM",
            "Python 3: A Beginner's Guide"
        ]
        for title in valid_titles:
            try:
                validate_article_title(title)
            except ValidationError as e:
                self.fail(f"Title '{title}' raised ValidationError unexpectedly: {e}")

    def test_title_invalid(self):
        invalid_titles = [
            "",
            "   ",
            "abc",
            "123456789",
            "@@@@@@",
            "!!!!!!",
            "20262026"
        ]
        for title in invalid_titles:
            with self.assertRaises(ValidationError, msg=f"Expected ValidationError for title: '{title}'"):
                validate_article_title(title)

    def test_content_valid(self):
        valid_contents = [
            "تساعد القراءة على تنمية المعرفة وتحسين القدرة على التركيز، كما تمنح الإنسان فرصة لفهم الأفكار بطريقة أعمق.",
            "Learning Django ORM with Python 3 is an amazing experience for building robust web applications rapidly and securely."
        ]
        for content in valid_contents:
            try:
                validate_article_content(content)
            except ValidationError as e:
                self.fail(f"Content raised ValidationError unexpectedly: {e}")

    def test_content_invalid(self):
        invalid_contents = [
            "",
            "   ",
            "abc",
            "123456789123456789123456789",
            "@@@@@@@@@@@@@@@@@@@@@@@@@@@",
            "!!!!!!!!!!!!!!!",
            "short content 123"
        ]
        for content in invalid_contents:
            with self.assertRaises(ValidationError, msg=f"Expected ValidationError for content: '{content}'"):
                validate_article_content(content)


class PostFormAndScenariosTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_scenario_a_publisher_numbers(self):
        form_data = {'published_at':'2026-11-16T19:00:00',
            'publisher_name': '123456',
            'title': 'عنوان تجريبي صحيح للمقال',
            'content': 'هذا محتوى تجريبي طويل يكفي لكي يكون مقالاً صحيحاً ومقبولاً في النظام.'
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('publisher_name', form.errors)
        self.assertEqual(Post.objects.count(), 0)

    def test_scenario_b_title_symbols(self):
        form_data = {'published_at':'2026-11-16T19:00:00',
            'publisher_name': 'سارة أحمد',
            'title': '@@@@@@',
            'content': 'هذا محتوى تجريبي طويل يكفي لكي يكون مقالاً صحيحاً ومقبولاً في النظام.'
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertEqual(Post.objects.count(), 0)

    def test_scenario_c_content_numbers(self):
        form_data = {'published_at':'2026-11-16T19:00:00',
            'publisher_name': 'سارة أحمد',
            'title': 'عنوان تجريبي صحيح للمقال',
            'content': '123456789123456789123456789123456'
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
        self.assertEqual(Post.objects.count(), 0)

    def test_scenario_d_all_spaces(self):
        form_data = {'published_at':'2026-11-16T19:00:00',
            'publisher_name': '   ',
            'title': '     ',
            'content': '                         '
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(Post.objects.count(), 0)

    def test_scenario_e_f_g_valid_submissions(self):
        # Arabic valid
        form_data_ar = {'published_at':'2026-11-16T19:00:00',
            'publisher_name': 'أحمد محمد',
            'title': 'القراءة في زمن السرعة',
            'content': 'تساعد القراءة على تنمية المعرفة وتحسين القدرة على التركيز، كما تمنح الإنسان فرصة لفهم الأفكار بطريقة أعمق.'
        }
        form_ar = PostForm(data=form_data_ar)
        self.assertTrue(form_ar.is_valid())
        post_ar = form_ar.save()
        self.assertEqual(post_ar.publisher_name, 'أحمد محمد')

        # English valid with numbers
        form_data_en = {'published_at':'2026-11-16T19:00:00',
            'publisher_name': 'John Smith',
            'title': 'Python 3: A Beginner Guide',
            'content': 'Learning Python 3 and Django ORM is an amazing experience for building robust web applications rapidly and securely.'
        }
        form_en = PostForm(data=form_data_en)
        self.assertTrue(form_en.is_valid())
        post_en = form_en.save()
        self.assertEqual(post_en.publisher_name, 'John Smith')


class BlogViewsAndLanguageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.post1 = Post.objects.create(
            publisher_name="محمد علي",
            title="أول تدوينة عن بايثون",
            content="بايثون لغة برمجة قوية وممتعة للجميع وتستخدم في الذكاء الاصطناعي وتطوير الويب."
        )

    def test_root_redirects_to_home(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/home/', fetch_redirect_response=True)

    def test_clean_urls_accessible(self):
        res_home = self.client.get(reverse('blog:home'))
        self.assertEqual(res_home.status_code, 200)

        res_about = self.client.get(reverse('blog:about'))
        self.assertEqual(res_about.status_code, 200)

        res_add = self.client.get(reverse('blog:add_post'))
        self.assertEqual(res_add.status_code, 200)

        res_detail = self.client.get(reverse('blog:post_detail', args=[self.post1.id]))
        self.assertEqual(res_detail.status_code, 200)

    def test_legacy_prefixed_routes_redirect(self):
        res = self.client.get('/ar/about/')
        self.assertRedirects(res, '/about/', fetch_redirect_response=True)
        self.assertNotIn('django_language', res.cookies)

        res_en = self.client.get('/en/home/')
        self.assertRedirects(res_en, '/home/', fetch_redirect_response=True)
        self.assertNotIn('django_language', res_en.cookies)

    def test_theme_switching_both_directions(self):
        res_dark = self.client.post(reverse('blog:set_theme', args=['dark']), {'next': '/home/'})
        self.assertEqual(res_dark.status_code, 302)
        self.assertEqual(res_dark.cookies['theme'].value, 'dark')

        self.client.cookies['theme'] = 'dark'
        home_dark = self.client.get(reverse('blog:home'))
        self.assertEqual(home_dark.context['theme'], 'dark')
        self.assertContains(home_dark, 'data-theme="dark"')

        res_light = self.client.post(reverse('blog:set_theme', args=['light']), {'next': '/home/'})
        self.assertEqual(res_light.status_code, 302)
        self.assertEqual(res_light.cookies['theme'].value, 'light')

        self.client.cookies['theme'] = 'light'
        home_light = self.client.get(reverse('blog:home'))
        self.assertEqual(home_light.context['theme'], 'light')
        self.assertContains(home_light, 'data-theme="light"')

    def test_image_url_method(self):
        self.assertTrue(self.post1.get_image_url().startswith('/static/blog/img/'))
