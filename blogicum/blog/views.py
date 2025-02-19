from django.shortcuts import render, redirect
from django.http import Http404
from blog.models import Post, Category
from django.utils import timezone
from django.core.paginator import Paginator
from .models import User, Comment
from .forms import UserForm, PostForm, CommentForm
from django.contrib.auth.decorators import login_required


def index(request):
    template = 'blog/index.html'
    try:
        post_list = Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')
    except Post.DoesNotExist:
        raise Http404
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, template, context=context)


def post_detail(request, id):
    template = 'blog/detail.html'
    try:
        post = Post.objects.get(
            id=id,
            # is_published=True,
            # category__is_published=True,
            # pub_date__lte=timezone.now()
        )
    except Post.DoesNotExist:
        raise Http404
    if not (post.is_published
            and post.category.is_published
            and post.pub_date <= timezone.now()
            or not post.author != request.user):
        raise Http404
    comments = Comment.objects.filter(
        post=post
    )
    form = CommentForm()
    context = {'post': post, 'comments': comments, 'form': form}
    return render(request, template, context=context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    try:
        post_list = Post.objects.filter(
            category__slug=category_slug,
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')
        category = Category.objects.get(
            slug=category_slug,
            is_published=True,
        )
    except Category.DoesNotExist:
        raise Http404
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, template, context=context)


@login_required(login_url='login')
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    template = 'blog/create.html'
    context = {'form': form}
    return render(request, template, context=context)


@login_required(login_url='login')
def edit_post(request, id):
    try:
        post = Post.objects.get(
            id=id,
        )
    except Post.DoesNotExist:
        raise Http404
    if post.author != request.user:
        return redirect('blog:post_detail', id=id)
    form = PostForm(
        request.POST or None,
        instance=post,
        files=request.FILES or None
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    template = 'blog/create.html'
    context = {'form': form}
    return render(request, template, context=context)


@login_required(login_url='login')
def delete_post(request, id):
    try:
        post = Post.objects.get(
            id=id,
        )
    except Post.DoesNotExist:
        raise Http404
    if post.author != request.user:
        return redirect('blog:post_detail', id=id)
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    template = 'blog/create.html'
    context = {'form': form}
    return render(request, template, context=context)


def profile(request, username):
    page_obj = None
    try:
        user = User.objects.get(username=username)
        if user != request.user:
            post_list = Post.objects.filter(
                author=user,
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            ).order_by('-pub_date')
        else:
            post_list = Post.objects.filter(
                author=user,
            ).order_by('-pub_date')
    except User.DoesNotExist:
        raise Http404
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'blog/profile.html'
    context = {'profile': user, 'page_obj': page_obj}
    return render(request, template, context=context)


@login_required(login_url='login')
def edit_profile(request):
    form = UserForm(request.POST or None, instance=request.user)
    print(form.is_valid())
    if request.method == 'POST':
        if form.is_valid():
            form.save()
    template = 'blog/user.html'
    context = {'form': form}
    return render(request, template, context=context)


@login_required(login_url='login')
def add_comment(request, id):
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        raise Http404
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            post.comment_count += 1
            post.save()
    return redirect('blog:post_detail', id=id)


@login_required(login_url='login')
def edit_comment(request, id, comment_id):
    try:
        Post.objects.get(id=id)
    except Post.DoesNotExist:
        raise Http404
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        raise Http404
    if comment.author != request.user:
        raise Http404
    form = CommentForm(request.POST or None, instance=comment)
    if comment.author == request.user and request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=id)
    template = 'blog/comment.html'
    context = {'form': form, 'comment': comment}
    return render(request, template, context=context)


@login_required(login_url='login')
def delete_comment(request, id, comment_id):
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        raise Http404
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        raise Http404
    if comment.author != request.user:
        raise Http404
    if comment.author == request.user and request.method == 'POST':
        comment.delete()
        post.comment_count -= 1
        post.save()
        return redirect('blog:post_detail', id=id)
    template = 'blog/comment.html'
    context = {'comment': comment}
    return render(request, template, context=context)
