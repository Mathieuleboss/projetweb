class NoCacheMiddleware:
    """
    Middleware pour empêcher la mise en cache des pages sensibles
    lorsqu'un utilisateur est connecté.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Si l'utilisateur est connecté, empêche la mise en cache
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response
