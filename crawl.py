import urllib.request
from datetime import datetime, timedelta
import os.path


def fetch(date, length, overwrite=False, name=None):
    if name is None:
        filename = os.path.join('data', date.strftime('%Y%m%d') + '.json')
    else:
        filename = os.path.join('data', name + '.json')

    if not overwrite and os.path.isfile(filename):
        return

    print('Fetching', date)
    url_template = 'http://m.media.daum.net/api/service/bestreply/{}.json?limit={}&scope=0&type=mobile'
    date_str = date.strftime('%Y%m%d')
    url = url_template.format(date_str, length)
    with urllib.request.urlopen(url) as res:
        with open(filename, 'w') as f:
            f.write(res.read().decode('utf-8'))


def main():
    now = datetime.now().date()
    start_date = datetime(2012, 1, 1).date()
    end_date = now - timedelta(days=1)
    while start_date <= end_date:
        fetch(start_date, 100)
        start_date += timedelta(days=1)
    fetch(now, 100, overwrite=True, name='today')


if __name__ == '__main__':
    main()

