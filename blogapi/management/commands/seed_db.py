import random
from django.core.management.base import BaseCommand
from faker import Faker

from blogapi.models import Author, Post, Comment

fake = Faker()

NUM_AUTHORS = 20
POSTS_PER_AUTHOR = 10
COMMENTS_PER_POST = 10


class Command(BaseCommand):
    help = 'Seed the database with Authors, Posts, and Comments for benchmarking.'

    def handle(self, *args, **options):
        self.stdout.write('Clearing existing data...')
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Author.objects.all().delete()

        self.stdout.write(f'Creating {NUM_AUTHORS} authors...')
        authors = Author.objects.bulk_create([
            Author(name=fake.name(), bio=fake.paragraph(nb_sentences=3))
            for _ in range(NUM_AUTHORS)
        ])

        self.stdout.write(f'Creating {NUM_AUTHORS * POSTS_PER_AUTHOR} posts...')
        posts = Post.objects.bulk_create([
            Post(
                author=author,
                title=fake.sentence(nb_words=6),
                content='\n\n'.join(fake.paragraphs(nb=3)),
                views=random.randint(0, 10000),
            )
            for author in authors
            for _ in range(POSTS_PER_AUTHOR)
        ])

        self.stdout.write(f'Creating {len(posts) * COMMENTS_PER_POST} comments...')
        Comment.objects.bulk_create([
            Comment(
                post=post,
                author_name=fake.name(),
                body=fake.paragraph(nb_sentences=2),
            )
            for post in posts
            for _ in range(COMMENTS_PER_POST)
        ])

        self.stdout.write(self.style.SUCCESS(
            f'Database seeded: {NUM_AUTHORS} authors, '
            f'{NUM_AUTHORS * POSTS_PER_AUTHOR} posts, '
            f'{NUM_AUTHORS * POSTS_PER_AUTHOR * COMMENTS_PER_POST} comments.'
        ))
