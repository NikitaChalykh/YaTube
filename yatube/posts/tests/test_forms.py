from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Post, Group, Comment
from django.contrib.auth import get_user_model
from django.urls import reverse
import shutil
import tempfile
from django.conf import settings

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    """Создаем тестовые посты, группу и форму."""
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
            text='Старый пост',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        """Удаляем тестовые медиа."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаем клиент зарегистрированного пользователя."""
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
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
        form_data = {
            'text': 'Новый пост',
            'group': PostFormTests.group.pk,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': PostFormTests.user.username}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            post.group, PostFormTests.group
        )
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, PostFormTests.user)
        self.assertEqual(post.image, 'posts/small.gif')

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
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
        form_data = {
            'text': 'Измененный старый пост',
            'group': PostFormTests.group.pk,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTests.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': PostFormTests.post.pk}
        ))
        self.assertEqual(
            Post.objects.get(pk=PostFormTests.post.pk).text,
            form_data['text']
        )
        self.assertEqual(
            Post.objects.get(pk=PostFormTests.post.pk).group.pk,
            form_data['group']
        )

    def test_create_comment(self):
        """Валидная форма создает запись в Comment."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Новый остроумный комментарий'
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostFormTests.post.pk}
            ),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.first()
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': PostFormTests.post.pk}
        ))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.post, PostFormTests.post)
        self.assertEqual(comment.author, PostFormTests.user)
