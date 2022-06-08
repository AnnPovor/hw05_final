import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Group, Post, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            id=1,
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

        cls.comment = Comment.objects.create(
            text='Комментарий',
            post=cls.post,
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый пост',
            'title': 'Тестовый заголовок',
            'small_gif': self.post.image,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'auth'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                author=self.user,
                text=self.post.text,
                image=self.post.image
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        """При отправке валидной формы происходит редактирования поста"""
        post = PostCreateFormTests.post
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            new_text='Тестовый пост',
            group=self.group.id)
        self.assertEqual(post.text, 'Тестовый пост')
        self.assertEqual(post.group, self.group)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_add_comment(self):
        """Комментировать посты может только авторизованный пользователь."""
        comments_count = Comment.objects.count()
        form_data = {'post': self.post,
                     'author': self.user,
                     'text': self.comment.text}
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=(self.post.id,)))
