from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title='API Documentation',
      default_version='v1',
      description="Your project description",
      terms_of_service="https://www.example.com/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

api_patterns = [
    path('accounts/', include('accounts.urls')),
    path('chat/', include('apps.chat.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_patterns)),

    # Swagger / ReDoc
    # re_path(r'^api/v1/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('', schema_view.with_ui('swagger', cache_timeout=60), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=60), name='schema-redoc'),
]
