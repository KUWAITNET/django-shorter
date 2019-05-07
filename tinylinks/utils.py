from .forms import TinylinkForm


def shortify_url(url):
    data = {'data': {'long_url': url}, 'mode': None}
    form = TinylinkForm(**data)
    if form.is_valid():
        obj = form.save()
        return obj.short_url
    else:
        return url
