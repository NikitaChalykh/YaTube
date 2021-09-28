from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Post, Group, Comment, Follow
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms
import shutil
import tempfile
from django.conf import settings
from django.core.cache import cache

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    """Создаем тестовые посты и группы."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='leo')
        cls.group = Group.objects.create(
            title='Группа поклонников графа',
            slug='tolstoi',
            description='Что-то о группе'
        )
        cls.post_1 = Post.objects.create(
            author=cls.user,
            text='Война и мир изначально назывался «1805 год»',
            group=cls.group,
            image=uploaded
        )
        cls.comment_post_1 = Comment.objects.create(
            author=cls.user,
            text='А мне только битвы запомнились»',
            post=cls.post_1
        )

    @classmethod
    def tearDownClass(cls):
        """Удаляем тестовые медиа."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаем клиент зарегистрированного пользователя."""
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTests.user)

    def post_exist(self, page_context):
        """Метод для проверки существования поста на страницах."""
        if 'page_obj' in page_context:
            post = page_context['page_obj'][0]
        else:
            post = page_context['post']
        task_author = post.author
        task_text = post.text
        task_image = post.image
        task_group = post.group
        self.assertEqual(
            task_image,
            'posts/small.gif'
        )
        self.assertEqual(
            task_author,
            PostViewTests.post_1.author
        )
        self.assertEqual(
            task_text,
            PostViewTests.post_1.text
        )
        self.assertEqual(
            task_group,
            PostViewTests.post_1.group
        )
        self.assertEqual(
            post.comments.last(),
            PostViewTests.comment_post_1
        )

    def test_paginator_correct_context(self):
        """Шаблон index, group_list и profile
        сформированы с корректным Paginator.
        """
        cache.clear()
        paginator_objects = []
        for i in range(1, 18):
            new_post = Post(
                author=PostViewTests.user,
                text='Тестовый пост ' + str(i),
                group=PostViewTests.group
            )
            paginator_objects.append(new_post)
        Post.objects.bulk_create(paginator_objects)
        paginator_data = {
            'index': reverse('posts:index'),
            'group': reverse(
                'posts:group_list',
                kwargs={'slug': PostViewTests.group.slug}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': PostViewTests.user.username}
            )
        }
        for paginator_place, paginator_page in paginator_data.items():
            with self.subTest(paginator_place=paginator_place):
                response_page_1 = self.authorized_client.get(paginator_page)
                response_page_2 = self.authorized_client.get(
                    paginator_page + '?page=2'
                )
                self.assertEqual(len(
                    response_page_1.context['page_obj']),
                    10
                )
                self.assertEqual(len(
                    response_page_2.context['page_obj']),
                    8
                )

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response_index = self.authorized_client.get(reverse('posts:index'))
        page_index_context = response_index.context
        self.post_exist(page_index_context)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response_post_detail = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewTests.post_1.pk}
            )
        )
        page_post_detail_context = response_post_detail.context
        self.post_exist(page_post_detail_context)

    def test_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response_group = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewTests.group.slug}
            )
        )
        page_group_context = response_group.context
        task_group = response_group.context['group']
        self.post_exist(page_group_context)
        self.assertEqual(task_group, PostViewTests.group)

    def test_profile_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response_profile = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostViewTests.user.username}
            )
        )
        page_profile_context = response_profile.context
        task_profile = response_profile.context['author']
        self.post_exist(page_profile_context)
        self.assertEqual(task_profile, PostViewTests.user)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон create_post(edit) сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostViewTests.post_1.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_index_caches(self):
        """Тестирование кэша главной страницы."""
        cache.clear()
        response_1 = self.authorized_client.get(
            reverse('posts:index')
        )
        response_content_1 = response_1.content
        cache.clear()
        new_post = Post.objects.create(
            author=PostViewTests.user,
            text='Этот пост создан быть удаленным)',
            group=PostViewTests.group
        )
        response_2 = self.authorized_client.get(
            reverse('posts:index')
        )
        response_content_2 = response_2.content
        self.assertNotEqual(response_content_1, response_content_2)
        new_post.delete()
        response_3 = self.authorized_client.get(
            reverse('posts:index')
        )
        response_content_3 = response_3.content
        self.assertEqual(response_content_2, response_content_3)
        cache.clear()
        response_4 = self.authorized_client.get(
            reverse('posts:index')
        )
        response_content_4 = response_4.content
        self.assertEqual(response_content_4, response_content_1)

    def test_follow(self):
        """Тестирование подписки и отписки на пользователя."""
        count_follow = 0
        new_author = User.objects.create(username='Lermontov')
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': new_author.username}
            )
        )
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.assertEqual(Follow.objects.last().author, new_author)
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': new_author.username}
            )
        )
        self.assertEqual(Follow.objects.count(), count_follow)
        self.assertIsNone(Follow.objects.last())
        new_author.delete()

    def test_following_posts(self):
        """Тестирование появления поста автора в ленте подписчиков."""
        new_author = User.objects.create(username='Lermontov')
        new_post_author = Post.objects.create(
            author=new_author,
            text='Что тут должно быть из Лермонтова',
        )
        new_user = User.objects.create(username='Niko')
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': new_author.username}
            )
        )
        response_leo = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(
            response_leo.context['page_obj'][0].text,
            new_post_author.text
        )
        new_authorized_client = Client()
        new_authorized_client.force_login(new_user)
        new_authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostViewTests.user.username}
            )
        )
        response_niko = new_authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotEqual(
            response_niko.context['page_obj'][0].text,
            new_post_author.text
        )
