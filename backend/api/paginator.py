from rest_framework.pagination import PageNumberPagination, _positive_int


class CustomPaginator(PageNumberPagination):
    def get_page_size(self, request):
        page_size_query_param = request.query_params.get("limit")
        if page_size_query_param:
            try:
                return _positive_int(
                    page_size_query_param, strict=True, cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                return self.page_size
