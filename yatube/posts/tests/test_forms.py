from posts.models import Post, Group
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from posts.forms import PostForm

User = get_user_model()


class PostFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.form = PostForm()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(user=PostFormsTest.post.author)

    def test_create_post(self):
        """Валидная форма создает запись в create_post."""
        post_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый тест 2',
            'group': '',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': 'auth'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый тест 2',
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует пост по пути posts:post_edit"""
        form_data = {
            'text': 'Тестовый тест 3',
            'group': '',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(1,)),
            data=form_data,
            follow=True
        )
        post_count = Post.objects.count()
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': 1}))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый тест 3',
            ).exists()
        )
