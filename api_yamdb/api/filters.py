import django_filters as df
from reviews.models import Title


class TitleFilter(df.FilterSet):
    name = df.CharFilter(field_name='name', lookup_expr='contains')
    category = df.CharFilter(
        field_name='category__slug', lookup_expr='contains')
    genre = df.CharFilter(
        field_name='genre__slug', lookup_expr='contains'
    )
    year = df.NumberFilter(
        field_name='year', lookup_expr='contains'
    )

    class Meta:
        model = Title
        fields = '__all__'
