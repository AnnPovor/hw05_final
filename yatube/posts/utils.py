from django.conf import settings
from django.core.paginator import Paginator


def page_help(posts, request):
    paginator = Paginator(posts, settings.COUNT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
