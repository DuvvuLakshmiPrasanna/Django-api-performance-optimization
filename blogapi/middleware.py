from django.db import connection


class QueryCountMiddleware:
    """
    Adds X-Query-Count header to responses when DEBUG=True,
    enabling the benchmark script to read the query count.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Reset query log before each request
        from django.conf import settings
        if settings.DEBUG:
            try:
                connection.queries.clear()
            except Exception:
                pass

        response = self.get_response(request)

        if settings.DEBUG:
            query_count = len(connection.queries)
            response['X-Query-Count'] = str(query_count)

        return response
