"""
URL configuration for schoolms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

# swagger imports
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from drf_yasg.generators import OpenAPISchemaGenerator

schema_view = get_schema_view(
    openapi.Info(
        title="SchoolMS API",
        default_version="v1",
        description="SchoolMS API description",
        terms_of_service="https://*",
        contact=openapi.Contact(email="*"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
    generator_class=OpenAPISchemaGenerator,
)



admin.site.site_header = "SchoolMS"
admin.site.site_title = "SchoolMS"

urlpatterns = [
    path("admin/", admin.site.urls),
    # swagger endpoints
    path(
        "api/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    

    
    # local apps endpoint
    path("api/users/", include("users.urls")),
    path("api/course/", include("courses.urls")),
    path("api/", include("school_artifacts.urls")),
    path("api/", include("school_administration.urls")),
]
