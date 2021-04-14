# hw03_forms/about/tests/test_views.py
from django.test import Client, TestCase
from django.urls import reverse

AUTHOR = reverse("about:author")
TECH = reverse("about:tech")


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_accessible_by_name(self):
        """URL, генерируемые в приложении about, доступны."""
        pages = [
            AUTHOR,
            TECH,
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, 200)

    def test_about_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'about/author.html': AUTHOR,
            'about/tech.html': TECH,
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
