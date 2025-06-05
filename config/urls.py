# config/urls.py
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import include, path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
        description="API Documentation for Bulletin Board",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="stasm226@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def health_check(request):
    return HttpResponse("ok")


urlpatterns = [
    path("api/admin/", admin.site.urls),
    #
    path("api/swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("api/swaggerjson/", schema_view.without_ui(cache_timeout=0), name="schema-json"),  # API без UI
    path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    #
    path("api/user/", include("user.urls", namespace="user")),
    path("api/bulletin/", include("bulletin.urls", namespace="bulletin")),
    #
    path("api-auth/", include("rest_framework.urls")),  # login/logout через browsable API
    # Чтобы при заходе на / не было 404, редирект на /api/swagger/
    path("", lambda request: HttpResponseRedirect("/api/swagger/")),
]

urlpatterns += [
    path("healthz", health_check),
]
