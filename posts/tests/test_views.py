# hw03_forms/posts/tests/test_views.py
import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache.utils import make_template_fragment_key
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User, Group, Post, Follow

SLUG = 'test-slug'
ANOTHER_SLUG = 'another-slug'

MYNAME = 'MYNAME'
MYFOLLOWER = 'MYFOLLOWER'  # еще один username
# для модели автор-подписчик

MAIN = reverse('index')
GROUP = reverse('group_posts', args=(SLUG,))
ANOTHER_GROUP = reverse('group_posts', args=(ANOTHER_SLUG,))
NEW_POST = reverse('new_post')

PROFILE = reverse('profile', args=(MYNAME,))
FOLLOW = reverse('profile_follow', args=(MYNAME,))
UNFOLLOW = reverse('profile_unfollow', args=(MYNAME,))
FOLLOW_INDEX = reverse('follow_index')
NOT_FOUND = reverse('404')


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG,
            description='Тестовое описание',
        )
        cls.another_group = Group.objects.create(
            title='Другая группа',
            slug=ANOTHER_SLUG,
            description='Описание другой группы',
        )
        cls.user = User.objects.create_user(username=MYNAME)
        # создаем пользователя-подписчика
        cls.following_user = User.objects.create_user(username=MYFOLLOWER)
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )
        kwargs = {'username': MYNAME, 'post_id': cls.post.id}
        cls.MYPOST = reverse('post', kwargs=kwargs)
        cls.MYPOST_EDIT = reverse('post_edit', kwargs=kwargs)
        # урл страницы комментариев
        cls.MYPOST_COMMENT = reverse('add_comment', kwargs=kwargs)

    @classmethod
    def tearDownClass(cls):
        # удаление картинок после теста
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.following_client = Client()
        self.following_client.force_login(self.following_user)

    def test_pages_show_correct_post_content(self):
        """
        Шаблоны сформированы с правильным постом в контексте.
        """
        urls = {
            MAIN: 'page',
            GROUP: 'page',
            PROFILE: 'page',
            self.MYPOST: 'post',
        }
        for url, key in urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                if key == 'post':
                    post = response.context[key]
                else:
                    self.assertEqual(len(response.context[key]), 1)
                    post = response.context[key][0]
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.image, self.post.image)

    def test_pages_show_correct_author(self):
        """
        Шаблоны  /profile/, /post/ сформированы
        с автором соответствующего поста
        """
        urls = [
            PROFILE,
            self.MYPOST,
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                author = response.context['author']
                self.assertEqual(author, self.post.author)

    def test_new_post_posted(self):
        """
        Вновь созданный пост не отображается
        на странице "чужой группы"
        """
        response = self.guest_client.get(ANOTHER_GROUP)
        self.assertNotIn(self.post, response.context['page'])

    # далее тесты к 6 спринту
    def test_main_page_cached(self):
        """Главная страница кэшируется"""

        key = make_template_fragment_key('index_page')
        self.guest_client.get(MAIN)
        cache1 = cache.get(key)
        Post.objects.create(
            text='Новый текст',
            author=self.user,
        )
        self.guest_client.get(MAIN)
        cache2 = cache.get(key)
        # проверяем равен ли кэш первого запроса
        # кэшу второго запроса
        self.assertEqual(cache1, cache2)
        cache.clear()
        self.guest_client.get(MAIN)
        cache3 = cache.get(key)
        # после очистки новый кэш содержит оба созданных поста
        # и не равен предыдыщему кэшу
        self.assertNotEqual(cache2, cache3)
        cache.clear()

    def test_authorized_user_can_follow(self):
        """Авторизованный пользователь
         может подписыватьсяна авторов
        """
        self.following_client.get(FOLLOW, follow=True)
        self.assertTrue(
            Follow.objects.filter(
                author=self.post.author
            ).exists()
        )

    def test_authorized_user_can_unfollow(self):
        """Авторизованный пользователь
         может отписываться от авторов
        """
        self.following_client.get(UNFOLLOW, follow=True)
        self.assertFalse(
            Follow.objects.filter(
                author=self.post.author
            ).exists()
        )

    def test_followed_author_appears_at_follow_page(self):
        """
        Новая запись появляется в ленте подписчиков
        и не появляется у других
        """
        self.following_client.get(FOLLOW, follow=True)
        new_post = Post.objects.create(
            text='Новый текст',
            author=self.user,
            group=self.group,
        )
        response = self.following_client.get(FOLLOW_INDEX)
        self.assertEqual(len(response.context['page']), 2)
        self.assertEqual(new_post, response.context['page'][0])
        another_resp = self.authorized_client.get(FOLLOW_INDEX)
        self.assertEqual(len(another_resp.context['page']), 0)

    def test_404_code_if_not_found(self):
        """
        Сервер возвращает 404, если страница не найдена
        """
        response = self.guest_client.get(NOT_FOUND)
        self.assertEqual(response.status_code, 404)
