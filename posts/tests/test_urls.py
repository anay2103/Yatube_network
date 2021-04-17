# hw03_forms/posts/tests/test_urls.py
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User, Group, Post

SLUG = 'test-slug'
MYNAME = 'MYNAME'
ALT_NAME = 'ALTNAME'
MAIN_URL = reverse('index')
GROUP_URL = reverse('group_posts', args=(SLUG,))
LOGIN_URL = reverse('login')
NEW_POST_URL = reverse('new_post')
PROFILE_URL = reverse('profile', args=(MYNAME,))
POST = 'post'
POST_EDIT = 'post_edit'


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug=SLUG,
            description='Тестовое описание',
        )

        cls.user = User.objects.create(username=MYNAME)
        cls.not_author_user = User.objects.create(username=ALT_NAME)

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        kwargs = {'username': MYNAME, 'post_id': cls.post.id}
        cls.MYPOST = reverse('post', kwargs=kwargs)
        # урл страницы редактирования поста
        cls.MYPOST_EDIT = reverse('post_edit', kwargs=kwargs)
        # урл страницы комментариев
        cls.MYPOST_COMMENT = reverse('add_comment', kwargs=kwargs)

    def setUp(self):
        # Создаем экземпляр клиента
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_client = Client()
        self.another_client.force_login(self.not_author_user)

    def test_correct_url_routing(self):
        '''имена URL соответствуют маршрутам'''
        route_names = {
            MAIN_URL: '/',
            GROUP_URL: f'/group/{SLUG}/',
            NEW_POST_URL: '/new/',
            PROFILE_URL: f'/{MYNAME}/',
            self.MYPOST:
            f'/{MYNAME}/{self.post.id}/',
            self.MYPOST_EDIT:
            f'/{MYNAME}/{self.post.id}/edit/',
            self.MYPOST_COMMENT:
            f'/{MYNAME}/{self.post.id}/comment/',
        }
        for name, url in route_names.items():
            self.assertEqual(name, url)

    def test_home_url_exists_at_desired_location(self):
        """
        Страницы MAIN, GROUP, PROFILE, /post/ доступны любому пользователю.
        Страницы /new_post/, /post_edit/, /add_comment/
         перенаправляют пользователя.
        """
        pages = [
            (MAIN_URL, self.guest_client, 200),
            (GROUP_URL, self.guest_client, 200),
            (NEW_POST_URL, self.guest_client, 302),
            (NEW_POST_URL, self.authorized_client, 200),
            (PROFILE_URL, self.guest_client, 200),
            (self.MYPOST, self.guest_client, 200),
            (self.MYPOST_EDIT, self.guest_client, 302),
            (self.MYPOST_EDIT, self.another_client, 302),
            (self.MYPOST_EDIT, self.authorized_client, 200),
            (self.MYPOST_COMMENT, self.guest_client, 302),
            (self.MYPOST_COMMENT, self.authorized_client, 200),
        ]

        for url, client, code in pages:
            with self.subTest(url=url):
                self.assertEqual(
                    client.get(url).status_code,
                    code,
                    f'Проверить доступность страницы {url}'
                )

    def test_redirect_notauthor_on_login(self):
        """
        Страницы /new/, /post_edit/ перенаправят неавтора
        на страницу логина.
        """
        pages = [
            (NEW_POST_URL, self.guest_client,
             f'{LOGIN_URL}?next={NEW_POST_URL}'),
            (self.MYPOST_EDIT, self.guest_client,
             f'{LOGIN_URL}?next={self.MYPOST_EDIT}'),
            (self.MYPOST_EDIT, self.another_client,
             f'{LOGIN_URL}?next={self.MYPOST_EDIT}'),
            (self.MYPOST_COMMENT, self.guest_client,
             f'{LOGIN_URL}?next={self.MYPOST_COMMENT}'),
        ]
        for page in pages:
            url, client, redirected = page
            self.assertRedirects(self.client.get(url, follow=True), redirected)

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = {
            MAIN_URL: 'index.html',
            GROUP_URL: 'group.html',
            NEW_POST_URL: 'new_post.html',
            PROFILE_URL: 'profile.html',
            self.MYPOST: 'post.html',
            self.MYPOST_EDIT: 'new_post.html',
            self.MYPOST_COMMENT: 'includes/comment.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_client.get(url),
                    template
                )
