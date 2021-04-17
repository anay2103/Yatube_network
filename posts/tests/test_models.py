# hw03_forms/posts/tests/test_models.py
from django.test import TestCase

from posts.models import User, Group, Post

SLUG = 'test-slug'


class ModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug=SLUG,
            description='Тестовый текст'
        )
        user = User.objects.create()
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=user,
            group=ModelTest.group,
        )

    def test_group_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'title': 'Название',
            'slug': 'Ключ для адресов страниц о группе пользователей',
            'description': 'Текст',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Group._meta.get_field(
                        value).verbose_name, expected)

    def test_group_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'title': 'Дайте короткое название группе пользователей',
            'slug': ('Укажите адрес для страницы группы. Используйте только '
                     'латиницу, цифры, дефисы и знаки подчёркивания'),
            'description': 'Дайте подробное описание группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Group._meta.get_field(value).help_text, expected)

    def test_group_object_name(self):
        """В поле __str__  объекта group записано значение поля group.title."""
        group = ModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_post_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата',
            'author': 'Автор',
            'group': 'Группа'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Post._meta.get_field(value).verbose_name, expected)

    def test_post_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Напишите здесь, о чем думаете',
            'group': 'Укажите группу пользователей'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Post._meta.get_field(value).help_text, expected)

    def test_post_object_name(self):
        """В поле __str__  объекта post совпадает с ожидаемым"""
        post = ModelTest.post
        group_var = [post.group.title
                     if post.group is not None else "без группы"
                     ]
        expected_object_name = (f'Группа: {group_var}, '
                                f'Автор: {post.author.username}, '
                                f'Дата: {post.pub_date.strftime("%Y-%m-%d")}, '
                                f'{post.text[:15]}'
                                )
        self.assertEqual(expected_object_name, str(post))
