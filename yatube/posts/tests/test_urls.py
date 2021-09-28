from django.test import TestCase, Client
from ..models import Post, Group
from django.contrib.auth import get_user_model
from django.urls import reverse
from http import HTTPStatus
from django.core.cache import cache

User = get_user_model()


class PostURLTests(TestCase):
    """Создаем тестовый пост и группу."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.group = Group.objects.create(
            title='Группа поклонников графа',
            slug='tolstoi',
            description='Что-то о группе'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Новый пост без группы'
        )

    def setUp(self):
        """Создаем клиент гостя и зарегистрированного пользователя."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_urls_response_guest(self):
        """Проверяем статус страниц для гостя."""
        url_status = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': PostURLTests.group.slug}
            ): HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': PostURLTests.user.username}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostURLTests.post.pk}
            ): HTTPStatus.OK,
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostURLTests.post.pk}
            ): HTTPStatus.FOUND,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostURLTests.post.pk}
            ): HTTPStatus.FOUND,
            reverse('posts:post_create'): HTTPStatus.FOUND,
            '/unexpecting_page/': HTTPStatus.NOT_FOUND,
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostURLTests.user.username}
            ): HTTPStatus.FOUND,
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostURLTests.user.username}
            ): HTTPStatus.FOUND,
            reverse('posts:follow_index'): HTTPStatus.FOUND
        }
        for url, status_code in url_status.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_response_guest_redirect(self):
        """Проверяем редирект страниц для гостя."""
        url_redirect = {
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostURLTests.post.pk}
            ):
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostURLTests.post.pk}
            ),
            reverse('posts:post_create'):
                reverse('users:login') + '?next='
                + reverse('posts:post_create'),
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostURLTests.post.pk}
            ):
            reverse('users:login') + '?next='
                + reverse(
                'posts:add_comment',
                kwargs={'post_id': PostURLTests.post.pk}
            ),
            reverse(
                'posts:follow_index'
            ):
                reverse('users:login')
                + '?next=' + reverse('posts:follow_index'),
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostURLTests.user.username}
            ):
                reverse('users:login') + '?next='
                + reverse(
                'posts:profile_follow',
                kwargs={'username': PostURLTests.user.username}
            ),
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostURLTests.user.username}
            ):
                reverse('users:login') + '?next='
                + reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostURLTests.user.username}
            )
        }
        for url, redirect_url in url_redirect.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_urls_response_auth(self):
        """Проверяем статус страниц для зарегистрированного пользователя."""
        url_status = {
            reverse(
                'posts:post_edit', kwargs={'post_id': PostURLTests.post.pk}
            ): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.OK,
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostURLTests.post.pk}
            ): HTTPStatus.FOUND,
            reverse('posts:follow_index'): HTTPStatus.OK,
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostURLTests.user.username}
            ): HTTPStatus.FOUND,
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostURLTests.user.username}
            ): HTTPStatus.FOUND
        }
        for url, status_code in url_status.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_response_auth_redirect(self):
        """Проверяем редирект страниц
        для зарегистрированного пользователя.
        """
        url_redirect = {
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostURLTests.post.pk}
            ):
                reverse(
                'posts:post_detail',
                kwargs={'post_id': PostURLTests.post.pk}
            ),
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostURLTests.user.username}
            ):
                reverse(
                'posts:profile',
                kwargs={'username': PostURLTests.user.username}
            ),
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostURLTests.user.username}
            ):
                reverse(
                'posts:profile',
                kwargs={'username': PostURLTests.user.username}
            )
        }
        for url, redirect_url in url_redirect.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_urls_uses_correct_template(self):
        """Проверяем запрашиваемые шаблоны страниц через имена."""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostURLTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostURLTests.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostURLTests.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostURLTests.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
