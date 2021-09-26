import re
import tempfile

import pytest
from django.contrib.auth import get_user_model
from django.core.paginator import Page, Paginator
from django.db.models import fields

try:
    from posts.models import Post
except ImportError:
    assert False, 'Не найдена модель Post'

try:
    from posts.models import Follow
except ImportError:
    assert False, 'Не найдена модель Follow'


def search_field(fields, attname):
    for field in fields:
        if attname == field.attname:
            return field
    return None


def search_refind(execution, user_code):
    """Поиск запуска"""
    for temp_line in user_code.split('\n'):
        if re.search(execution, temp_line):
            return True
    return False


class TestFollow:

    def test_follow(self):
        model_fields = Follow._meta.fields

        user_field = search_field(model_fields, 'user_id')
        assert user_field is not None, 'Добавьте пользователя, автор который создал событие `user` модели `Follow`'
        assert type(user_field) == fields.related.ForeignKey, (
            'Свойство `user` модели `Follow` должно быть ссылкой на другую модель `ForeignKey`'
        )
        assert user_field.related_model == get_user_model(), (
            'Свойство `user` модели `Follow` должно быть ссылкой на модель пользователя `User`'
        )
        assert user_field.remote_field.related_name == 'follower', (
            'Свойство `user` модели `Follow` должно иметь аттрибут `related_name="follower"`'
        )
        # assert user_field.on_delete == CASCADE, (
        #     'Свойство `user` модели `Follow` должно иметь аттрибут `on_delete=models.CASCADE`'

        author_field = search_field(model_fields, 'author_id')
        assert author_field is not None, 'Добавьте пользователя, автор который создал событие `author` модели `Follow`'
        assert type(author_field) == fields.related.ForeignKey, (
            'Свойство `author` модели `Follow` должно быть ссылкой на другую модель `ForeignKey`'
        )
        assert author_field.related_model == get_user_model(), (
            'Свойство `author` модели `Follow` должно быть ссылкой на модель пользователя `User`'
        )
        assert author_field.remote_field.related_name == 'following', (
            'Свойство `author` модели `Follow` должно иметь аттрибут `related_name="following"`'
        )
        # assert author_field.on_delete == CASCADE, (
        #     'Свойство `author` модели `Follow` должно иметь аттрибут `on_delete=models.CASCADE`'

    def check_url(self, client, url, str_url):
        try:
            response = client.get(f'{url}')
        except Exception as e:
            assert False, f'''Страница `{str_url}` работает неправильно. Ошибка: `{e}`'''
        if response.status_code in (301, 302) and response.url == f'{url}/':
            response = client.get(f'{url}/')
        assert response.status_code != 404, f'Страница `{str_url}` не найдена, проверьте этот адрес в *urls.py*'
        return response

    @pytest.mark.django_db(transaction=True)
    def test_follow_not_auth(self, client, user):
        response = self.check_url(client, '/follow', '/follow/')
        if not(response.status_code in (301, 302) and response.url.startswith('/auth/login')):
            assert False, (
                'Проверьте, что не авторизованного пользователя `/follow/` отправляет на страницу авторизации'
            )

        response = self.check_url(client, f'/profile/{user.username}/follow', '/profile/<username>/follow/')
        if not(response.status_code in (301, 302) and response.url.startswith('/auth/login')):
            assert False, (
                'Проверьте, что не авторизованного пользователя `profile/<username>/follow/` '
                'отправляете на страницу авторизации'
            )

        response = self.check_url(client, f'/profile/{user.username}/unfollow', '/profile/<username>/unfollow/')
        if not(response.status_code in (301, 302) and response.url.startswith('/auth/login')):
            assert False, (
                'Проверьте, что не авторизованного пользователя `profile/<username>/unfollow/` '
                'отправляете на страницу авторизации'
            )

    @pytest.mark.django_db(transaction=True)
    def test_follow_auth(self, user_client, user, post):
        assert user.follower.count() == 0, 'Проверьте, что правильно считается подписки'
        self.check_url(user_client, f'/profile/{post.author.username}/follow', '/profile/<username>/follow/')
        assert user.follower.count() == 0, 'Проверьте, что нельзя подписаться на самого себя'

        user_1 = get_user_model().objects.create_user(username='TestUser_2344')
        user_2 = get_user_model().objects.create_user(username='TestUser_73485')

        self.check_url(user_client, f'/profile/{user_1.username}/follow', '/profile/<username>/follow/')
        assert user.follower.count() == 1, 'Проверьте, что вы можете подписаться на пользователя'
        self.check_url(user_client, f'/profile/{user_1.username}/follow', '/profile/<username>/follow/')
        assert user.follower.count() == 1, 'Проверьте, что вы можете подписаться на пользователя только один раз'

        image = tempfile.NamedTemporaryFile(suffix=".jpg").name
        Post.objects.create(text='Тестовый пост 4564534', author=user_1, image=image)
        Post.objects.create(text='Тестовый пост 354745', author=user_1, image=image)

        Post.objects.create(text='Тестовый пост 245456', author=user_2, image=image)
        Post.objects.create(text='Тестовый пост 9789', author=user_2, image=image)
        Post.objects.create(text='Тестовый пост 4574', author=user_2, image=image)

        response = self.check_url(user_client, '/follow', '/follow/')
        assert 'page_obj' in response.context, (
            'Проверьте, что передали переменную `page_obj` в контекст страницы `/follow/`'
        )
        assert type(response.context['page_obj']) == Page, (
            'Проверьте, что переменная `page_obj` на странице `/follow/` типа `Page`'
        )
        assert len(response.context['page_obj']) == 2, (
            'Проверьте, что на странице `/follow/` список статей авторов на которых подписаны'
        )

        self.check_url(user_client, f'/profile/{user_2.username}/follow', '/profile/<username>/follow/')
        assert user.follower.count() == 2, 'Проверьте, что вы можете подписаться на пользователя'
        response = self.check_url(user_client, '/follow', '/follow/')
        assert len(response.context['page_obj']) == 5, (
            'Проверьте, что на странице `/follow/` список статей авторов на которых подписаны'
        )

        self.check_url(user_client, f'/profile/{user_1.username}/unfollow', '/profile/<username>/unfollow/')
        assert user.follower.count() == 1, 'Проверьте, что вы можете отписаться от пользователя'
        response = self.check_url(user_client, '/follow', '/follow/')
        assert len(response.context['page_obj']) == 3, (
            'Проверьте, что на странице `/follow/` список статей авторов на которых подписаны'
        )

        self.check_url(user_client, f'/profile/{user_2.username}/unfollow', '/profile/<username>/unfollow/')
        assert user.follower.count() == 0, 'Проверьте, что вы можете отписаться от пользователя'
        response = self.check_url(user_client, '/follow', '/follow/')
        assert len(response.context['page_obj']) == 0, (
            'Проверьте, что на странице `/follow/` список статей авторов на которых подписаны'
        )
