from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group
from django import forms

User = get_user_model()
TEST_NUM = 10


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(user=PostViewsTest.post.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'auth'}): 'posts/profile.html',
            (reverse('posts:post_detail',
                     kwargs={'post_id': '1'})): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': '1'}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        excepted_object = list(Post.objects.all()[:TEST_NUM])
        self.assertEqual(list(response.context['page_obj']), excepted_object)

    def test_index_page_pagination(self):
        """Тест главной страницы с правильной пагинацией."""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        responce = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        excepted = list(Post.objects.filter(
                        group_id=self.group.id)[:TEST_NUM])
        self.assertEqual(list(responce.context['page_obj']), excepted)

    def test_group_page_pagination(self):
        """Тест страницы группы с правильной пагинацией."""
        response = self.guest_client.get(reverse('posts:group_list',
                                         kwargs={'slug': self.group.slug}))
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author}))
        excepted = list(Post.objects.filter(author_id=self.user.id)[:TEST_NUM])
        self.assertEqual(list(response.context['page_obj']), excepted)

    def test_profile_page_pagination(self):
        """Тест страницы профиля с правильной пагинацией."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author}))
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        responce = self.guest_client.get(reverse('posts:post_detail',
                                                 kwargs={'post_id': 1}))
        self.assertEqual(responce.context.get('post').text, self.post.text)
        self.assertEqual(responce.context.get('post').author, self.post.author)
        self.assertEqual(responce.context.get('post').group, self.post.group)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_create edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      kwargs={'post_id': 1}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_check_group(self):
        """
        Проверка создания поста с выбранной группой на главной странице,
        на странице группы и странице профиля.
        """
        form_fields = {
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ): Post.objects.exclude(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertNotIn(expected, form_field)

    def test_check_group_in_pages(self):
        """Проверка группы на правильное распредение по шаблонам"""
        form_fields = {
            reverse('posts:index'): Post.objects.get(group=self.post.group),
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}): (
                        Post.objects.get(group=self.post.group)),
            reverse('posts:profile',
                    kwargs={'username': 'auth'}): (
                        Post.objects.get(group=self.post.group)),
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertIn(expected, form_field)
