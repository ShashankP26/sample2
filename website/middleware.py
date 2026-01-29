# # website/middleware.py
# from django.contrib.auth import login
# from .models import MobileSession

# class MobileTokenMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         token = request.headers.get("X-MOBILE-TOKEN")

#         if token and request.user.is_anonymous:
#             try:
#                 session = MobileSession.objects.get(token=token)
#                 login(request, session.user)
#             except MobileSession.DoesNotExist:
#                 pass

#         return self.get_response(request)