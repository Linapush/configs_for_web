from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from drf_spectacular.views import SpectacularSwaggerView

from example.views import register_view

urlpatterns = [
    path("admin/", admin.site.urls),

    path("auth/", include("django.contrib.auth.urls")),
    path("auth/register/", register_view, name="register"),

    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    path("api/", include("example.urls_api")),

    path("example/", include("example.urls_web")),

    path("", RedirectView.as_view(url="/example/")),
]

# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi

# schema_view = get_schema_view(
#     openapi.Info(title="API", default_version='v1'),
#     public=True,
# )

# urlpatterns += [
#     path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
# ]