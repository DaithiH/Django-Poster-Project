class IgnoreFaviconMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/favicon.ico':
            from django.http import HttpResponse
            return HttpResponse(status=204)
        return self.get_response(request)