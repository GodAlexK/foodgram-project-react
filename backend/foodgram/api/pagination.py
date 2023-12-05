from rest_framework.pagination import PageNumberPagination


class LimitPagePagination(PageNumberPagination):
    """Вывод 6 объектов на странице."""

    page_size = 6
    page_size_query_param = 'limit'
    max_page_size = 200
