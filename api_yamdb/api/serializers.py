from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from reviews.models import Category, Comment, Genre, Review, Title, User

from .utils import CurrentReviewDafault, CurrentTitleDafault


class TokenObtainPairCustomSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'] = serializers.CharField()
        self.fields['confirmation_code'] = serializers.CharField()
        self.fields.pop('password')

    def validate(self, attrs):
        authenticate_kwargs = {
            'username': attrs['username'],
            'confirmation_code': attrs['confirmation_code'],
        }

        if 'request' in self.context:
            authenticate_kwargs['request'] = self.context['request']

        self.user = authenticate(**authenticate_kwargs)

        data = {}
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        ]
        model = User

    def validate(self, attrs):
        if 'request' in self.context:
            request = self.context['request']
            user = request.user
            if (user.is_authenticated
                    and not user.is_admin
                    and 'role' in attrs):
                attrs['role'] = user.role

        return super().validate(attrs)


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])

    def validate(self, attrs):
        if 'username' in attrs and attrs['username'] == 'me':
            raise ValidationError({'username': 'username cannot be me'})

        return super().validate(attrs)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Title
        exclude = ('pub_date', )


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.HiddenField(default=CurrentTitleDafault())
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Review
        validators = (UniqueTogetherValidator(
            queryset=Review.objects.all(), fields=('title', 'author')),)


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.HiddenField(default=CurrentReviewDafault())
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment
