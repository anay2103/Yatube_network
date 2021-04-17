from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .forms import CommentForm, PostForm
from .models import Follow, Post, Group


def index(request):
    post_list = Post.objects.select_related('author', 'group').all()
    paginator = Paginator(post_list, settings.NUM_OBJECTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {
        'page': page,
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.NUM_OBJECTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
        'group': group,
        'page': page,
    })


@login_required
def new_post(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if not form.is_valid():
        return render(request, 'new_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'includes/comment.html', {'form': form})
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect('post', username, post.id)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'post.html', {
            'form': form,
            'author': post.author,
            'post': post,
            'comments': post.comments.all(),
        })
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return render(request, 'post.html', {
        'form': form,
        'author': post.author,
        'post': post,
        'comments': post.comments.all(),
    })


@login_required
def post_edit(request, username, post_id):
    if username != request.user.username:
        return redirect(
            'post',
            username,
            post_id,
        )
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, 'new_post.html', {
            'form': form,
            'post': post,
        })
    form.save()
    return redirect('post', username, post.id)

# далее все функции изменные в спринте 6


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        if author.following.filter(
            user=request.user,
            author__username=username
        ).count() != 0:
            following = True
    paginator = Paginator(author.posts.all(), settings.NUM_OBJECTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {
        'author': author,
        'page': page,
        'following': following
    })


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, settings.NUM_OBJECTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow_index.html", {'page': page})


@login_required
def profile_follow(request, username):
    if not request.user.username == username:
        author_to_follow = get_object_or_404(User, username=username)
        obj, created = Follow.objects.get_or_create(
            user=request.user,
            author=author_to_follow
        )
    return redirect('follow_index')


@login_required
def profile_unfollow(request, username):
    unfollow = Follow.objects.filter(
        user=request.user,
        author__username=username)
    unfollow.delete()
    return redirect('follow_index')


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
