from django.shortcuts import get_object_or_404
from reviews.models import Review, Title


class CurrentTitleDafault:
    requires_context = True

    def __call__(self, serializer_field):
        c_view = serializer_field.context['view']
        title_id = c_view.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class CurrentReviewDafault:
    requires_context = True

    def __call__(self, serializer_field):
        c_view = serializer_field.context['view']
        review_id = c_view.kwargs.get('review_id')
        return get_object_or_404(Review, id=review_id)

    def __repr__(self):
        return '%s()' % self.__class__.__name__
