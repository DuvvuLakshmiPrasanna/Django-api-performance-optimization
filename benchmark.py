#!/usr/bin/env python3
"""
Benchmark script for the Django blog API endpoints.

Usage:
    python benchmark.py <url> [--requests N]

Example:
    python benchmark.py http://localhost:8000/api/posts/naive --requests 50
    python benchmark.py http://localhost:8000/api/posts/optimized
    python benchmark.py http://localhost:8000/api/posts/advanced
"""

import argparse
import json
import sys
import time

try:
    import requests
except ImportError:
    print("Please install requests: pip install requests")
    sys.exit(1)


def benchmark(url: str, num_requests: int = 50) -> dict:
    times = []
    query_count = None

    for i in range(num_requests):
        start = time.perf_counter()
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"  Request {i+1} failed: {e}")
            continue
        elapsed_ms = (time.perf_counter() - start) * 1000
        times.append(elapsed_ms)

        # Read query count from custom header (set when DEBUG=True)
        if query_count is None:
            qc_header = response.headers.get('X-Query-Count')
            if qc_header:
                query_count = int(qc_header)

        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{num_requests} requests completed...")

    if not times:
        print("No successful requests.")
        return {}

    return {
        'query_count': query_count,
        'avg_response_ms': round(sum(times) / len(times), 3),
        'min_response_ms': round(min(times), 3),
        'max_response_ms': round(max(times), 3),
    }


def main():
    parser = argparse.ArgumentParser(description='Benchmark Django API endpoints.')
    parser.add_argument('url', help='URL to benchmark')
    parser.add_argument('--requests', type=int, default=50,
                        help='Number of requests to make (default: 50)')
    args = parser.parse_args()

    print(f"\nBenchmarking: {args.url}")
    print(f"Sending {args.requests} requests...\n")

    results = benchmark(args.url, args.requests)

    if results:
        print(f"\nResults:")
        print(f"  Query count  : {results.get('query_count', 'N/A')} (per request)")
        print(f"  Avg response : {results['avg_response_ms']} ms")
        print(f"  Min response : {results['min_response_ms']} ms")
        print(f"  Max response : {results['max_response_ms']} ms")
        print(json.dumps(results, indent=2))

    return results


if __name__ == '__main__':
    main()
