from rest_framework.pagination import PageNumberPagination


class HabitPagination(PageNumberPagination):
    """
    Пагинация для списка привычек.
    """
    page_size: int = 5
    page_size_query_param: str | None = None
    max_page_size: str | None = None
