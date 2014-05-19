"""Views for the ``django-tinylinks`` application."""
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Count, Sum
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    RedirectView,
    UpdateView,
)

from tinylinks.forms import TinylinkForm
from tinylinks.models import Tinylink, TinylinkLog, validate_long_url

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics, permissions, viewsets, status
from tinylinks.serializers import TinylinkSerializer, UserSerializer

import re
piwik_id = re.compile(r'^_pk_id')


class TinylinkViewMixin(object):
    """
    View to handle general functions for Tinylink objects.

    """
    model = Tinylink
    form_class = TinylinkForm

    @method_decorator(permission_required('tinylinks.add_tinylink'))
    def dispatch(self, *args, **kwargs):
        self.mode = kwargs.get('mode')
        return super(TinylinkViewMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TinylinkViewMixin, self).get_context_data(**kwargs)
        context.update({'mode': self.mode})
        return context

    def get(self, request, *args, **kwargs):
        self.object = None
        if hasattr(self, 'get_object') and kwargs.get('pk'):
            self.object = self.get_object()
            if (not request.user.is_staff
                and (not self.object
                     or not self.object.user == request.user)):
                raise Http404
        return super(TinylinkViewMixin, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(TinylinkViewMixin, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'mode': self.mode,
        })
        return kwargs

    def get_success_url(self):
        return reverse('tinylink_list')


class TinylinkListView(TinylinkViewMixin, ListView):
    """
    View to list all tinylinks of a user.

    """
    @method_decorator(permission_required('tinylinks.add_tinylink'))
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            for key in request.POST:
                if key.startswith('validate'):
                    try:
                        link_id = int(key.replace('validate', ''))
                    except ValueError:
                        raise Http404
                    try:
                        link = Tinylink.objects.get(pk=link_id)
                    except Tinylink.DoesNotExist:
                        raise Http404
                    validate_long_url(link)
        return super(TinylinkListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_staff:
            return Tinylink.objects.all()
        return self.request.user.tinylinks.all()


class TinylinkCreateView(TinylinkViewMixin, CreateView):
    """
    View to generate a Tinylink instance including a shortened URL.

    """
    def get_success_url(self):
        return reverse('tinylink_update', kwargs={'pk': self.object.id,
                                                  'mode': 'change-short'})


class TinylinkUpdateView(TinylinkViewMixin, UpdateView):
    """
    View to update a Tinylink instance.

    """
    pass


class TinylinkDeleteView(TinylinkViewMixin, DeleteView):
    """
    View to delete a certain tinylink.

    """
    pass


class TinylinkRedirectView(RedirectView):
    """
    View to validate a short URL and redirect to its location.

    """
    def dispatch(self, *args, **kwargs):
        if kwargs.get('short_url'):
            try:
                tinylink = Tinylink.objects.get(short_url=kwargs.get(
                    'short_url'))
            except Tinylink.DoesNotExist:
                tinylink = None
                self.url = reverse('tinylink_notfound')
            if tinylink:
                # set the redirect long URL
                self.url = tinylink.long_url
                tinylink.amount_of_views += 1
                tinylink.save()
                print tinylink

                try:
                    ref = self.request.META.get('HTTP_REFERER', '')
                except KeyError:
                    ref = ''

                cookies = self.request.COOKIES
                pk_id = ''
                for key in cookies:
                    if piwik_id.search(key):
                        pk_id = cookies[key]

                tlog = TinylinkLog(
                    tinylink=tinylink, referrer=ref, cookie=pk_id,
                    user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
                    remote_ip=self.request.META['REMOTE_ADDR']
                )
                print tlog
                tlog.save()

        return super(TinylinkRedirectView, self).dispatch(*args, **kwargs)

    def get_redirect_url(self, **kwargs):
        """
        We have to override this method.

        The original method tries to do `self.url % kwargs` which will fail
        when the URL has `%` characters.

        """
        if self.url:
            url = self.url
            args = self.request.META.get('QUERY_STRING', '')
            if args and self.query_string:
                url = "%s?%s" % (url, args)
            return url
        else:
            return None


class StatisticsView(ListView):
    """
    View to list all tinylinks including their statistics.

    """
    model = Tinylink
    template_name = "tinylinks/statistics.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404
        return super(StatisticsView, self).dispatch(request, *args, **kwargs)


class TinylinkList(generics.ListCreateAPIView):
    """
    API Class for listing and creating tinylinks

    """
    queryset = Tinylink.objects.all()
    serializer_class = TinylinkSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def pre_save(self, obj):
        obj.user = self.request.user


class TinylinkDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API Class for retrieving, updating and destroying tinylinks

    """
    queryset = Tinylink.objects.all()
    serializer_class = TinylinkSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def pre_save(self, obj):
        obj.user = self.request.user


class TinylinkViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    """
    queryset = Tinylink.objects.all()
    serializer_class = TinylinkSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
            #permissions.IsOwnerOrReadOnly,)

    def pre_save(self, obj):
        obj.user = self.request.user


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.

    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(['GET'])
def db_stats(request):
    """
    Total number of tinylinks and sum of clicks

    """
    clicks = Tinylink.objects.aggregate(Sum('amount_of_views')).amount_of_views__sum
    data = {
        'tinylinks': Tinylink.objects.count(),
        'clicks': clicks
    }

    return Response(data)


@api_view(['GET'])
# TODO: Pagination and filtering
def stats(request):
    """
    Stats about tinylinks

    """

    data = {}

    count = 0
    for link in Tinylink.objects.all():
        data['link_' + str(count)] = {
            'shorturl': link.short_url,
            'url': link.long_url,
            'clicks': link.amount_of_views,
            'is_broken': link.is_broken
        }
        count += 1

    data['stats'] = {
        'tinylinks': Tinylink.objects.count(),
        'clicks': Tinylink.objects.aggregate(Sum('amount_of_views'))
    }

    return Response(data)


@api_view(['GET'])
def tinylink_stats(request, short_url):
    '''
    Return stats for a link

    '''
    tinylink = Tinylink.objects.get(short_url=short_url)

    if not tinylink:
        data = { 'message': 'Error: Link not found' }
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    data = {}
    data['link'] = {
        'short_url': tinylink.short_url,
        'long_url': tinylink.long_url,
        'clicks': tinylink.amount_of_views
    }

    return Response(data)

@api_view(['GET'])
def tinylink_expand(request, short_url):
    '''
    Expand a short URL into a long URL

    '''
    tinylink = Tinylink.objects.get(short_url=short_url)

    if not tinylink:
        data = { 'message': 'Error: Link not found' }
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    data = {
        'short_url': tinylink.short_url,
        'long_url': tinylink.long_url,
    }

    return Response(data)
