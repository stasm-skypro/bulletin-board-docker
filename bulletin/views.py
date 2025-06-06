# bulletin/views.py

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Bulletin, Review
from .paginators import BulletinPagination, ReviewPagination
from .permissions import IsAuthenticatedOrReadOnlyForReviews, IsAuthorOrAdminOrReadOnlyForBulletins
from .serializers import BulletinCreateSerializer, BulletinDetailSerializer, BulletinListSerializer, ReviewSerializer
from .utils import send_review_notification_email


class BulletinViewSet(ModelViewSet):
    """
    API endpoint, который позволяет просматривать, редактировать и удалять объявления.
    :param queryset: объекты Bulletin
    :param serializer_class: сериализатор класса Bulletin
    :param permission_classes: классы уровней доступа
    :param pagination_class: пагинатор
    :filter_backends: фильтры
    :filterset_fields: поля для фильтрации
    """

    queryset = Bulletin.objects.all().order_by("-created_at")
    permission_classes = [IsAuthorOrAdminOrReadOnlyForBulletins]
    pagination_class = BulletinPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["title"]
    search_fields = ["title"]
    ordering_fields = ["title", "price", "created_at"]

    def get_serializer_class(self):  # type: ignore
        if self.action == "list" or self.action == "me":
            return BulletinListSerializer
        elif self.action == "retrieve":
            return BulletinDetailSerializer
        return BulletinCreateSerializer

    @action(detail=False, methods=["get"], permission_classes=[IsAuthorOrAdminOrReadOnlyForBulletins])
    def me(self, request):
        """
        Возвращает объявления текущего пользователя.
        URL: /api/bulletin/bulletins/me/
        """
        bulletins = self.queryset.filter(author=request.user)
        page = self.paginate_queryset(bulletins)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(bulletins, many=True)
        return Response(serializer.data)


class ReviewViewSet(ModelViewSet):
    """
    API endpoint, который позволяет просматривать, редактировать и удалять отзывы.
    :param queryset: Объекты Review
    :param serializer_class: сериализатор класса Review
    :param permission_classes: классы уровней доступа
    :param pagination_class: пагинатор
    """

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnlyForReviews]
    pagination_class = ReviewPagination
    search_fields = ["text", "created_at"]
    ordering_fields = ["created_at"]

    def get_queryset(self):  # type: ignore
        bulletin_id = self.kwargs.get("bulletin_pk")
        if not bulletin_id:
            return Review.objects.none()
        try:
            Bulletin.objects.get(pk=bulletin_id)
        except Bulletin.DoesNotExist:
            raise NotFound("Объявление не найдено.")
        return Review.objects.filter(bulletin_id=bulletin_id).order_by("-created_at")

    def perform_create(self, serializer):  # type: ignore
        """
        Сохраняет новый отзыв, устанавливая текущего пользователя автором и передавая bulletin.
        """
        bulletin = get_object_or_404(Bulletin, pk=self.kwargs["bulletin_pk"])
        review = serializer.save(author=self.request.user, bulletin=bulletin)

        # Отправляем письмо владельцу объявления
        send_review_notification_email.delay(  # type: ignore
            email=bulletin.author.email,
            bulletin_id=bulletin.id,
            bulletin_title=bulletin.title,
            bulletin_author=bulletin.author.email,
            review_author=review.author.email,
            review_text=review.text,
        )
