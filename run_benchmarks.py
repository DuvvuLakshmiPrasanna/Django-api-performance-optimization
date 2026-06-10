#!/usr/bin/env python3
"""
Runs benchmarks against all three endpoints and writes submission.json.

Usage:
    python run_benchmarks.py [--host http://localhost:8000] [--requests 50]
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

        if query_count is None:
            qc_header = response.headers.get('X-Query-Count')
            if qc_header:
                query_count = int(qc_header)

        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{num_requests} done...")

    if not times:
        return {'query_count': None, 'avg_response_ms': 0.0,
                'min_response_ms': 0.0, 'max_response_ms': 0.0}

    return {
        'query_count': query_count,
        'avg_response_ms': round(sum(times) / len(times), 3),
        'min_response_ms': round(min(times), 3),
        'max_response_ms': round(max(times), 3),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='http://localhost:8000')
    parser.add_argument('--requests', type=int, default=50)
    args = parser.parse_args()

    endpoints = {
        'naive': f'{args.host}/api/posts/naive',
        'optimized': f'{args.host}/api/posts/optimized',
        'advanced': f'{args.host}/api/posts/advanced',
    }

    results = {}
    for name, url in endpoints.items():
        print(f"\nBenchmarking /{name}...")
        results[name] = benchmark(url, args.requests)
        print(f"  → query_count={results[name]['query_count']}, "
              f"avg={results[name]['avg_response_ms']}ms")

    output_path = 'submission.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults written to {output_path}")
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
