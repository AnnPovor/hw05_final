# Generated by Django 2.2.16 on 2022-06-02 05:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Заголовок нового поста', max_length=200, verbose_name='Заголовок')),
                ('slug', models.SlugField(help_text='Выберите псевдоним', unique=True, verbose_name='Псевдоним')),
                ('description', models.TextField(help_text='Напишите описание', verbose_name='Описание группы')),
            ],
            options={
                'verbose_name_plural': 'Группы',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Текст нового поста', verbose_name='Текст')),
                ('pub_date', models.DateTimeField(auto_now_add=True, help_text='Заполните дату', verbose_name='Дата')),
                ('image', models.ImageField(blank=True, upload_to='posts/', verbose_name='Картинка')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('group', models.ForeignKey(blank=True, help_text='Группа, к которой будет относиться пост', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='posts.Group')),
            ],
            options={
                'verbose_name_plural': 'Публикации',
                'ordering': ['-pub_date'],
            },
        ),
    ]
