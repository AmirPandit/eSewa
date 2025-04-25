from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        total_pages = self.page.paginator.num_pages
        current_page = self.page.number
        count_page = self.page.paginator.count
        return Response(
            {
                "total_pages": total_pages,
                "current_page": current_page,
                "count": count_page,
                "data": data,
            }
        )
