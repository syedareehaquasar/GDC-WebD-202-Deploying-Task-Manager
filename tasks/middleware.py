from datetime import datetime

class CustomMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("From middleware Request", request)
        request.currentTime = datetime.now()
        response = self.get_response(request)
        return response
