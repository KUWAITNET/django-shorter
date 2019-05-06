from .forms import ShortifyForm


def shortify(url):
    form = ShortifyForm({'long_url': url})
    if form.is_valid():
        return form.cleaned_data.get('short_url')
    else:
        return form.errors.get('long_url')
