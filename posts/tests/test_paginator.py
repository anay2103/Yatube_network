# hw03_forms/posts/tests/test_paginator.py
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User, Post
from posts.settings import NUM_OBJECTS_PER_PAGE

SLUG = 'test-slug'
MAIN = reverse('index')
GROUP = reverse('group_posts', args=(SLUG,))
REMAINDER = 3
MYNAME = 'Чебурашка'


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=MYNAME)

        for i in range(NUM_OBJECTS_PER_PAGE + REMAINDER):
            Post.objects.create(
                text=f'Тестовый текст-{i}',
                author=cls.user,
            )

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contain_ten_records(self):
        response = self.client.get(MAIN)
        self.assertEqual(len(response.context.get(
            'page').object_list), NUM_OBJECTS_PER_PAGE)

    def test_second_page_contain_three_records(self):
        response = self.client.get(MAIN + '?page=2')
        self.assertEqual(
            len(response.context.get('page').object_list), REMAINDER)
