from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug',
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user)

        cls.urls_common = (
            ('posts:index', None, 'posts/index.html'),
            ('posts:profile', {'username': cls.user},
             'posts/profile.html'),
            ('posts:group_list', {'slug': cls.group.slug},
             'posts/group_list.html'),
            ('posts:post_detail', {'post_id': cls.post.id},
             'posts/post_detail.html'))

        cls.urls_redir = (
            ('posts:post_edit', {'post_id': cls.post.id},
             'posts/create_post.html'),
            ('posts:post_create', None, 'posts/create_post.html'))

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_common_uses_correct_template(self):
        """Common URL-адрес использует соответствующий шаблон."""
        for url, slug, template in self.urls_common:
            reverse_name = reverse(url, kwargs=slug)
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_redir_uses_correct_template(self):
        """Common URL-адрес использует соответствующий шаблон."""
        for url, slug, template in self.urls_redir:
            reverse_name = reverse(url, kwargs=slug)
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_common_url_exists_at_desired_location(self):
        """Страницы доступны любому пользователю."""
        for url, slug, template in self.urls_redir:
            reverse_name = reverse(url, kwargs=slug)
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redi_url_exists_at_desired_location(self):
        """Страницы /posts/1/edit/, /create/ перенаправит анонимного
                пользователя на страницу логина."""
        login = '/auth/login/'
        for url, slug, template in self.urls_redir:
            reverse_name = reverse(url, kwargs=slug)
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name, follow=True)
                self.assertRedirects(
                    response, f'{login}?next={reverse_name}')

    def test_unexisting_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
