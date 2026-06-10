# Django Blog API — N+1 Query Elimination

A Django REST API demonstrating how to diagnose and fix the N+1 query problem using `select_related`, `prefetch_related`, `annotate`, and **window functions**. Three endpoints expose the same data at three tiers of query efficiency.

---

## Quick Start

```bash
# 1. Clone / enter the project
git clone <repo-url> && cd django_blog_api

# 2. (Optional) copy env file
cp .env.example .env

# 3. Build and start everything — migrations + seeding run automatically
docker-compose up --build
```

The API will be available at **http://localhost:8000**.

---

## Endpoints

| Endpoint | Strategy | Queries |
|---|---|---|
| `GET /api/posts/naive` | Raw ORM loop, no optimization | ~401 |
| `GET /api/posts/optimized` | `select_related` + `annotate(Count)` | ≤ 2 |
| `GET /api/posts/advanced` | Optimized + `Window(Sum)` for author views | ≤ 2 |

### Response Schema

**Naive & Optimized:**
```json
[
  {
    "id": 1,
    "title": "Post title",
    "author_name": "Jane Doe",
    "comment_count": 10
  }
]
```

**Advanced** (adds `total_author_views`):
```json
[
  {
    "id": 1,
    "title": "Post title",
    "author_name": "Jane Doe",
    "comment_count": 10,
    "total_author_views": 52341
  }
]
```

---

## Data Model

```
Author (20) ──< Post (200, 10/author) ──< Comment (2000, 10/post)
```

---

## Benchmarking

After services are up, run against a live server:

```bash
pip install requests

# Single endpoint
python benchmark.py http://localhost:8000/api/posts/naive --requests 50

# All three endpoints → writes submission.json
python run_benchmarks.py --host http://localhost:8000 --requests 50
```

The `X-Query-Count` response header (injected by middleware when `DEBUG=True`) is used to record exact query counts.

---

## Key Findings

### The N+1 Problem

The naive endpoint accesses `post.author.name` and `post.comments.count()` inside a Python loop. Each access fires a separate SQL query:

- **1** query for all posts  
- **200** queries for author names (one per post)  
- **200** queries for comment counts (one per post)  
- **Total: 401 queries**

### The Fix

`select_related('author')` replaces the 200 author queries with a single JOIN. `annotate(comment_count=Count('comments'))` moves the count aggregation into the same SQL statement via `GROUP BY`. Result: **1 query**.

### Window Functions

`Window(expression=Sum('views'), partition_by=[F('author_id')])` computes the total views per author for every row, all within one SQL query — no subqueries, no Python-side aggregation.

---

## Environment Variables

See `.env.example` for all supported variables.

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `django-insecure-...` | Django secret key |
| `DEBUG` | `True` | Enable debug mode and query logging |
| `POSTGRES_DB` | `blogdb` | Database name |
| `POSTGRES_USER` | `bloguser` | DB user |
| `POSTGRES_PASSWORD` | `blogpassword` | DB password |
