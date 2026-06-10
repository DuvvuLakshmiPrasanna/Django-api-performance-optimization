import json
from django.http import JsonResponse
from django.db.models import Count, Sum, F
from django.db.models.expressions import Window

from .models import Post


def naive_posts(request):
    """
    Naive implementation demonstrating the N+1 query problem.
    For 200 posts: 1 (posts) + 200 (authors) + 200 (comment counts) = 401 queries.
    """
    posts = Post.objects.all()
    data = []
    for post in posts:
        data.append({
            'id': post.id,
            'title': post.title,
            'author_name': post.author.name,       # triggers query per post
            'comment_count': post.comments.count(), # triggers query per post
        })
    return JsonResponse(data, safe=False)


def optimized_posts(request):
    """
    Optimized implementation using select_related and annotate.
    Results in a single SQL query with JOIN and GROUP BY.
    """
    posts = (
        Post.objects
        .select_related('author')
        .annotate(comment_count=Count('comments'))
    )
    data = []
    for post in posts:
        data.append({
            'id': post.id,
            'title': post.title,
            'author_name': post.author.name,
            'comment_count': post.comment_count,
        })
    return JsonResponse(data, safe=False)


def advanced_posts(request):
    """
    Advanced implementation adding a window function to compute
    total views per author across all their posts, efficiently at DB level.
    """
    posts = (
        Post.objects
        .select_related('author')
        .annotate(
            comment_count=Count('comments'),
            total_author_views=Window(
                expression=Sum('views'),
                partition_by=[F('author_id')],
            ),
        )
    )
    data = []
    for post in posts:
        data.append({
            'id': post.id,
            'title': post.title,
            'author_name': post.author.name,
            'comment_count': post.comment_count,
            'total_author_views': post.total_author_views,
        })
    return JsonResponse(data, safe=False)
