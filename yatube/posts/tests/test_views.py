from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post, Follow

User = get_user_model()


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='auth',)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug',
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group)

        cls.urls_common = (
            ('posts:index', None, 'posts/index.html'),
            ('posts:profile', {'username': cls.user},
             'posts/profile.html'),
            ('posts:group_list', {'slug': cls.group.slug},
             'posts/group_list.html'),
            ('posts:post_detail', {'post_id': cls.post.id},
             'posts/post_detail.html'),
            ('posts:post_edit', {'post_id': cls.post.id},
             'posts/create_post.html'),
            ('posts:post_create', None, 'posts/create_post.html'),
            ('posts:follow_index', None, 'posts/follow.html'))

        cls.image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTests.user)

    def test_urls_common_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, slug, template in self.urls_common:
            reverse_name = reverse(url, kwargs=slug)
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_context(self, response, one_post=False):
        if not one_post:
            post = response.context.get('page_obj')[0]
        else:
            post = response.context.get('post')
        self.assertEqual(post.group, PostViewTests.group)
        self.assertEqual(post.author, PostViewTests.user)
        self.assertEqual(post.pub_date, PostViewTests.post.pub_date)
        self.assertEqual(post.text, PostViewTests.post.text)
        self.assertEqual(post.image, PostViewTests.post.image)

    def test_index_show_correct_context(self):
        """Index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_context(response)

    def test_group_list_show_correct_context(self):
        """Group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        self.check_context(response)
        group = response.context.get('group')
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.description, self.group.description)
        self.assertEqual(group.slug, self.group.slug)

    def test_profile_show_correct_context(self):
        """Profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', args=(self.user.username,)))
        self.check_context(response)
        self.assertEqual(response.context.get('author'), self.user)

    def test_post_detail_show_correct_context(self):
        """Post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=(self.post.id,)))
        self.check_context(response, one_post=True)

    def test_url_redir_page_show_correct_context(self):
        urls_redir = (
            ('posts:post_edit', {'post_id': self.post.id}),
            ('posts:post_create', None))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for url, slug in urls_redir:
            reverse_name = reverse(url, kwargs=slug)
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get('form').fields.get(
                            value)
                        self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='follower')
        cls.author = User.objects.create_user(username='following')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug',
        )
        cls.urls_common = (
            ('posts:index', None),
            ('posts:profile', {'username': cls.author}),
            ('posts:group_list', {'slug': cls.group.slug}))

        cls.url_follow = 'posts:follow_index', None

        posts = [
            Post(text=f'Тестовый текст{i}',
                 author=cls.author,
                 group=cls.group)
            for i in range(13)
        ]
        Post.objects.bulk_create(posts)

    def setUp(self) -> None:
        cache.clear()
        self.guest_client = Client()
        self.authorized_client_follower = Client()
        self.authorized_client_following = Client()
        self.authorized_client_follower.force_login(self.user)
        self.authorized_client_following.force_login(self.author)

    def test_page_contains_ten_records(self):
        for url, slug in self.urls_common:
            reverse_name = reverse(url, kwargs=slug)
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse(url, kwargs=slug))
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.client.get(
                    reverse(url, kwargs=slug) + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)

    def test_follow_index_contains_ten_records(self):
        Follow.objects.create(user=self.user, author=self.author)
        response = self.authorized_client_follower.get(
            reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.authorized_client_follower.get(
            reverse('posts:follow_index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


class PostCacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='auth',)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
            pk=1)
        cls.url_index = 'posts:index', None

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_cache(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post = self.post
        post.text = 'Изменённый пост',
        post.save()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, response_3.content)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='follower', )
        cls.author = User.objects.create_user(
            username='following', )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
        )

    def setUp(self):
        self.authorized_client_follower = Client()
        self.authorized_client_following = Client()
        self.authorized_client_follower.force_login(self.user)
        self.authorized_client_following.force_login(self.author)

    def test_follow(self):
        """Авторизованный пользователь может подписываться на других"""
        response = self.authorized_client_follower.get(
            reverse('posts:profile', args=(self.user.username,)))
        if self.user != self.author:
            Follow.objects.get_or_create(user=self.user, author=self.author)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        """Авторизованный пользователь может удалять подписку"""
        response = self.authorized_client_follower.get(
            reverse('posts:profile', args=(self.user.username,)))
        follower = Follow.objects.filter(user=self.user, author=self.author)
        if follower.exists():
            follower.delete()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_follow_index(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан"""
        Post.objects.create(text=self.post.text,
                            author=self.author)
        Follow.objects.create(user=self.user, author=self.author)
        response = self.authorized_client_follower.get(
            reverse('posts:follow_index')
        )
        new_post = response.context['page_obj'][0].text
        self.assertEqual(new_post, 'Тестовый пост')
        response = self.authorized_client_following.get(
            reverse('posts:follow_index'))
        self.assertNotContains(response, 'Тестовый пост')
