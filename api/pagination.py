from rest_framework import pagination


class PageNumberPaginationWithTotalPages(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        response = super(PageNumberPaginationWithTotalPages, self).get_paginated_response(data)
        response.data['total_pages'] = self.page.paginator.num_pages

        return response
