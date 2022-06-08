from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
        )

        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Комментарий',
            post=cls.post,
        )

        cls.follow = Follow.objects.create(
            author=cls.user,
            user=User.objects.create_user(username='follower')
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(str(self.post), self.post.text[:15])
        self.assertEqual(str(self.group), self.group.title)
        self.assertEqual(str(self.comment), self.comment.text)

    def test_models_label(self):
        """Verbose_name в полях совпадают с ожидаемым."""
        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment
        follow = PostModelTest.follow
        field_verboses_post = {
            'text': 'Текст',
            'pub_date': 'Дата',
            'author': 'Автор',
        }
        field_verboses_group = {
            'title': 'Заголовок',
            'slug': 'Псевдоним',
            'description': 'Описание группы',
        }
        field_verboses_comment = {
            'text': 'Текст',
            'created': 'Дата',
        }
        field_verboses_follow = {
            'user': 'Подписчик',
            'author': 'Автор',
        }

        for field, expected_value in field_verboses_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

        for field, expected_value in field_verboses_group.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)
        for field, expected_value in field_verboses_comment.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected_value)
        for field, expected_value in field_verboses_follow.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """Help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment
        field_help_post = {
            'text': 'Текст нового поста',
            'pub_date': 'Заполните дату',
        }
        field_help_group = {
            'title': 'Заголовок нового поста',
            'slug': 'Выберите псевдоним',
            'description': 'Напишите описание',
        }
        field_help_comment = {
            'post': 'Пост, к которому относится комментарий',
            'author': 'Автор комментария'
        }
        for field, expected_value in field_help_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

        for field, expected_value in field_help_group.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)
        for field, expected_value in field_help_comment.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).help_text, expected_value)
