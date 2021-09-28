import datetime as dt


def year(request):
    """Добавляет переменную с текущим годом."""
    year = dt.datetime.now().strftime('%Y')
    return {
        'year': int(year),
    }
