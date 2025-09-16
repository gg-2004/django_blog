from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from .models import Post
from .forms import PostForm
from django.contrib.auth.models import User

# ---------------- Home page ----------------
def home(request):
    # Show all posts to everyone
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'posts': posts})

# ---------------- Post detail page ----------------
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'post_detail.html', {'post': post})

# ---------------- Signup ----------------
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account was created successfully! 🎉")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

# ---------------- Create post ----------------
@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post created successfully! 📝")
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

# ---------------- Edit post ----------------
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return HttpResponseForbidden("You are not allowed to edit this post.")
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully! ✏️")
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'edit_post.html', {'form': form})

# ---------------- Delete post ----------------
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return HttpResponseForbidden("You are not allowed to delete this post.")
    if request.method == "POST":
        post.delete()
        messages.error(request, "Post deleted 🗑")
        return redirect('home')
    return render(request, 'delete_post.html', {'post': post})

# ---------------- Temporary setup route for Render ----------------
def setup_portfolio(request):
    """
    Temporary route to create admin, demo user, and sample posts.
    Visit /setup-portfolio/ once, then remove this route.
    """
    # Create superuser if it doesn't exist
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )

    # Create a demo user
    demo_user, created = User.objects.get_or_create(username="demo_user")
    if created:
        demo_user.set_password("demo123")
        demo_user.save()

    # Sample posts
    sample_posts = [
        ("First Blog", "This is a sample blog post for your portfolio."),
        ("Second Blog", "Another example post visible to everyone."),
        ("Django Deployment Tips", "This shows my deployment skills."),
    ]

    for title, content in sample_posts:
        Post.objects.get_or_create(title=title, content=content, author=demo_user)

    return HttpResponse("✅ Admin & demo posts created! Homepage will show them.")
