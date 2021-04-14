# hw03_forms/posts/tests/test_forms.py
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User, Group, Post

SLUG = 'test-slug'
ALT_SLUG = 'another-slug'
MYNAME = 'MYNAME'
MAIN_URL = reverse('index')
GROUP_URL = reverse('group_posts', args=(SLUG,))
NEW_POST_URL = reverse('new_post')
TEST_TEXT = 'Изменим тестовый текст'


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG,
            description='Тестовое описание',
        )
        cls.alt_group = Group.objects.create(
            title='Новая группа',
            slug=ALT_SLUG,
            description='Новое описание',
        )
        cls.user = User.objects.create_user(username=MYNAME)
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        posts_ids = set(Post.objects.all().values_list('id', flat=True))
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': self.group.id,
            'text': TEST_TEXT,
            'image': image
        }
        response = self.authorized_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True,
        )
        difference = Post.objects.exclude(id__in=posts_ids)
        self.assertEqual(difference.count(), 1)
        new_obj = difference.get()
        self.assertRedirects(response, MAIN_URL)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(new_obj.text, TEST_TEXT)
        self.assertEqual(new_obj.group, self.group)
        self.assertEqual(new_obj.author, self.user)
        self.assertEqual(new_obj.image, 'posts/small.gif')

    def test_edit_post(self):
        """Валидная форма изменяет пост."""
        posts_count = Post.objects.count()
        form_data = {
            'group': self.alt_group.id,
            'text': TEST_TEXT,
        }
        response = self.authorized_client.post(
            self.MYPOST_EDIT,
            data=form_data,
            follow=True,
        )
        post_to_edit = response.context['post']
        self.assertRedirects(response, self.MYPOST)
        self.assertEqual(post_to_edit.id, self.post.id)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post_to_edit.text, TEST_TEXT)
        self.assertEqual(post_to_edit.group, self.alt_group)
        self.assertEqual(post_to_edit.author, self.user)

    def test_add_comment(self):
        """
        Зарегистрированный пользователь
        может оставлять комментарий
        """
        comment_text = "Это комментарий"
        form_data = {'text': comment_text}
        response = self.authorized_client.post(
            self.MYPOST_COMMENT,
            data=form_data,
            follow=True,
        )
        self.assertEqual(len(response.context['comments']), 1)
        comment = response.context['comments'][0]
        self.assertEqual(comment.text, comment_text)
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)

    def test_new_page_show_correct_context(self):
        """
        Шаблоны /new_post/, /post_edit/
        сформированы с правильным контекстом.
        """
        urls = NEW_POST_URL, self.MYPOST_EDIT
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                for value, expected in form_fields.items():
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)
