from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoriesViewSet, CommentViewSet, GenresViewSet,
                    RegistrationView, ReviewViewSet, TitleViewSet,
                    TokenObtainPairCustomView, UserViewSet)

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register('categories', CategoriesViewSet)
v1_router.register('genres', GenresViewSet)
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')
v1_router.register('users', UserViewSet)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path(
        'v1/auth/token/',
        TokenObtainPairCustomView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'v1/auth/signup/',
        RegistrationView.as_view(),
        name='registration'
    ),
]
