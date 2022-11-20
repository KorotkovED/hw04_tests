from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import get_user_model
from .models import Post, Group
from .forms import PostForm
from django.contrib.auth.decorators import login_required


User = get_user_model()
POSTS = 10
LIMIT_PAGE = 10


def pagination(request, post_list):
    paginator = Paginator(post_list, LIMIT_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.all()[:POSTS]
    title = 'Последние обновления на сайте'
    text = "Это главная страница проекта Yatube"
    page_obj = pagination(request, post_list)
    context = {
        'title': title,
        'text': text,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.all()[:POSTS]
    page_obj = pagination(request, posts)
    title = 'Записи сообщества'
    text = "Здесь будет информация о группах проекта Yatube"
    context = {
        'group': group,
        'page_obj': page_obj,
        'title': title,
        'text': text
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    # Здесь код запроса к модели и создание словаря контекста
    user = get_object_or_404(User, username=username)
    post = (user.posts.select_related('group', 'author')
            .filter(author__username=username))[:POSTS]
    post_number = user.posts.count()
    page_obj = pagination(request, post)
    context = {
        'page_obj': page_obj,
        'author': user,
        'post_number': post_number,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    # Здесь код запроса к модели и создание словаря контекста
    post = Post.objects.get(pk=post_id)
    post_num = post.author.posts.count()
    context = {
        'post': post,
        'post_num': post_num,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(f'/profile/{request.user}/')
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author == request.user:
        if request.method == 'POST':
            form = PostForm(request.POST or None, instance=post)
            if form.is_valid():
                # post = form.save(commit=False)
                # post.author = request.user
                # post.save()
                form.save()
                return redirect(f'/posts/{post_id}/')

        if request.method == 'GET':
            form = PostForm(instance=post)
            context = {
                'form': form,
                'is_edit': True,
                'post': post,
            }
            return render(request, 'posts/create_post.html', context)

        form = PostForm()
        context = {
            'form': form,
            'is_edit': True,
            'post': post,
        }
        return render(request, 'posts/create_post.html', context)

    return redirect(f'/posts/{post_id}/')
