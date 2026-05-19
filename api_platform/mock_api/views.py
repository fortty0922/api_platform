"""
mock_api/views.py — Mock external API endpoint

Provides GET /external/stream for local testing.
In production this would be a real third-party service.
"""

import time

from django.http import JsonResponse


MOCK_DATA = [
    {
        "id": "ext_post_001",
        "author": "TechCrunch",
        "content": "AI Agents are reshaping backend architectures in 2026. [SensitiveDataHidden]",
        "metrics": {"views": 15200, "reports": 2},
        "category": "tech",
        "flagged": False,
    },
    {
        "id": "ext_post_002",
        "author": "TrollUser99",
        "content": "Insert toxic and inappropriate content here.",
        "metrics": {"views": 450, "reports": 25},
        "category": "general",
        "flagged": True,
    },
    {
        "id": "ext_post_003",
        "author": "ScienceDaily",
        "content": "New breakthrough in quantum computing [ResearchClassified] announced.",
        "metrics": {"views": 8900, "reports": 1},
        "category": "science",
        "flagged": False,
    },
]

REQUIRED_API_KEY = "student_secret_2026"


def stream_view(request):
    """GET /external/stream — returns mock post stream."""
    api_key = request.headers.get("X-Api-Key", "")
    if api_key != REQUIRED_API_KEY:
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=401)

    return JsonResponse(
        {
            "status": "success",
            "timestamp": int(time.time()),
            "data": MOCK_DATA,
        }
    )
