from django.http import JsonResponse

def help_api_view(request):
    """
    GET /api/help/
    Returns a JSON structure documenting the available API endpoints.
    """
    data = {
        "api_version": "1.0",
        "description": "API Platform Endpoints Directory",
        "authentication": "For endpoints requiring auth, include 'X-UID: <your_uid>' in the request headers.",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/help/",
                "description": "Get this list of available APIs.",
                "auth_required": False
            },
            {
                "method": "POST",
                "path": "/api/auth/register/",
                "description": "Register a new user and get a UID.",
                "auth_required": False,
                "payload": {"username": "str", "password": "str (min 6 chars)"}
            },
            {
                "method": "GET",
                "path": "/api/posts/",
                "description": "Get a paginated list of posts.",
                "auth_required": False,
                "query_params": {
                    "page": "int (default: 1)", 
                    "page_size": "int (default: 10)",
                    "search": "str (search title and content)",
                    "ordering": "str (e.g. '-created_at', 'title')",
                    "author_id": "int (filter by author)"
                }
            },
            {
                "method": "POST",
                "path": "/api/posts/",
                "description": "Create a new post. Use multipart/form-data if uploading an image.",
                "auth_required": True,
                "payload": {"title": "str", "content": "str", "image": "file (optional)"}
            },
            {
                "method": "GET",
                "path": "/api/posts/<id>/",
                "description": "Retrieve a single post by ID.",
                "auth_required": False,
                "path_params": {"id": "int (Post ID)"}
            },
            {
                "method": "PUT",
                "path": "/api/operations/posts/<id>/put/",
                "description": "Fully update your own post.",
                "auth_required": True,
                "path_params": {"id": "int (Post ID)"},
                "payload": {"title": "str", "content": "str", "image": "file (optional)"}
            },
            {
                "method": "PATCH",
                "path": "/api/operations/posts/<id>/patch/",
                "description": "Partially update your own post.",
                "auth_required": True,
                "path_params": {"id": "int (Post ID)"},
                "payload": {"title": "str (optional)", "content": "str (optional)", "image": "file (optional)"}
            },
            {
                "method": "DELETE",
                "path": "/api/operations/posts/<id>/delete/",
                "description": "Delete your own post.",
                "auth_required": True,
                "path_params": {"id": "int (Post ID)"}
            },
            {
                "method": "GET",
                "path": "/external/stream",
                "description": "Mock external API source returning article streams.",
                "auth_required": "Yes (X-API-KEY header)"
            },
            {
                "method": "GET",
                "path": "/dashboard/api/stats/",
                "description": "Real-time server and data metrics.",
                "auth_required": False
            }
        ]
    }
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False, 'indent': 2})
