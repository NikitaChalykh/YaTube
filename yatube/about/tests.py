from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse


class AboutURLTests(TestCase):
    """Создаем клиент гостя."""
    def setUp(self):
        self.guest_client = Client()

    def test_urls_uses_correct_template_and_response(self):
        """Проверяем запрашиваемые шаблоны страниц через адресы."""
        templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
