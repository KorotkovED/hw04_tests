from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField('Текст поста', help_text='Введите текст поста')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True,
                              null=True, related_name='group_posts',
                              verbose_name='Группа',
                              help_text=('Группа, '
                                         'к которой будет относиться пост')
                              )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.text[:15]
