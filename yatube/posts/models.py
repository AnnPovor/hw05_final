from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(verbose_name='Текст',
                            help_text='Текст нового поста')
    pub_date = models.DateTimeField(verbose_name='Дата',
                                    auto_now_add=True,
                                    help_text='Заполните дату')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',

    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text='Группа, к которой будет относиться пост')

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(verbose_name='Заголовок',
                             max_length=200,
                             help_text='Заголовок нового поста')
    slug = models.SlugField(verbose_name='Псевдоним',
                            unique=True,
                            help_text='Выберите псевдоним')
    description = models.TextField(verbose_name='Описание группы',
                                   help_text='Напишите описание')

    class Meta:
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text='Пост, к которому относится комментарий',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text='Автор комментария',
    )
    text = models.TextField(verbose_name='Текст',
                            help_text='Текст комментария')
    created = models.DateTimeField(verbose_name='Дата',
                                   auto_now_add=True,
                                   help_text='Заполните дату')

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique follow'
            )
        ]
