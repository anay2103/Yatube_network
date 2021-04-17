from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Дайте короткое название группе пользователей')

    slug = models.SlugField(
        unique=True,
        verbose_name='Ключ для адресов страниц о группе пользователей',
        help_text=('Укажите адрес для страницы группы. Используйте только '
                   'латиницу, цифры, дефисы и знаки подчёркивания'))

    description = models.TextField(
        verbose_name='Текст',
        help_text='Дайте подробное описание группы')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Напишите здесь, о чем думаете')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор')
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Укажите группу пользователей')
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        # изменено строковое представление группы,
        # т.к. админка падает, если у поста нет группы
        group_var = [self.group.title
                     if self.group is not None else "без группы"
                     ]
        return (
            f'Группа: {group_var}, '
            f'Автор: {self.author.username}, '
            f'Дата: {self.pub_date.strftime("%Y-%m-%d")}, '
            f'{self.text[:15]}'
        )


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Напишите здесь комментарий')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария')
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


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
        verbose_name='Автор, на кого подписка')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique follow')
        ]
