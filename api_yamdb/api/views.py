import uuid

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from reviews.models import (Category, Comment, ConfirmationCode, Genre, Review,
                            Title, User)

from .filters import TitleFilter
from .permissions import (IsAdminOrReadOnly, IsAdminPermission,
                          IsAuthorOrReadOnlyPermission)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, RegistrationSerializer,
                          ReviewSerializer, TitleCreateSerializer,
                          TitleSerializer, TokenObtainPairCustomSerializer,
                          UserSerializer)


class TokenObtainPairCustomView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = TokenObtainPairCustomSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            raise InvalidToken(serializer.errors)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RegistrationView(GenericAPIView):
    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = User(username=data['username'], email=data['email'])
        user.save()

        confirmation_code = ConfirmationCode(
            user=user,
            code=uuid.uuid4().hex
        )
        confirmation_code.save()

        send_mail(
            'Your confirmation code',
            confirmation_code.code,
            settings.ADMIN_EMAIL,
            [user.email],
            fail_silently=False
        )

        return Response(data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    pagination_class = LimitOffsetPagination

    def get_object(self):
        if 'username' in self.kwargs and self.kwargs['username'] == 'me':
            if self.request.method == 'DELETE':
                raise MethodNotAllowed(self.request.method)

            return self.request.user

        return super().get_object()

    def get_permissions(self):
        if 'username' in self.kwargs and self.kwargs['username'] == 'me':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminPermission]

        return [permission() for permission in permission_classes]


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = LimitOffsetPagination

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenresViewSet(CategoriesViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('-pub_date').all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_class = TitleFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', ):
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission, )
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        new_queryset = title.reviews.all()
        return new_queryset

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission, )
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        new_queryset = Comment.objects.filter(review=review)
        return new_queryset

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)
