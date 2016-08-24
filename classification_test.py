import json
from collections import Counter
from datetime import date, datetime, timedelta
import urllib.request
from konlpy.tag import Kkma
import functools
import os


START_DATE = date(2012, 1, 1)
KNOWN_TAGS = {
    '강용석', '고두심', '고승덕', '고현정', '곽노현', '교도소', '국가정보원', '국민의당', '국정원', '김근태', '김무성', '김문수', '김연아', '김용민', '김정은', '김제동', '김종인', '김현철',
    '나경원', '나꼼수', '나가수', '나는가수다', '노건평', '노건호', '노무현', '노회찬',
    '더불어민주당', '더민주', '대한항공', '디도스',
    '루퍼트', '류현진',
    '메르스', '무한도전', '문대성', '문재인', '문창극', '민영화', '민주당',
    '박근혜', '박명수', '박시후', '박영선', '박원순', '박주영', '박지성', '박지원', '박진영', '박희태', '반기문', '배현진',
    '새누리', '새누리당', '세월호', '설경구', '소녀시대', '손학규', '쇼트트랙', '수아레스', '신하균', '신해철',
    '아이유', '아이폰', '안상수', '안성기', '안철수', '어버이연합', '유민아빠', '유병언', '유병호', '유시민', '윤창중', '이동관', '이명박', '이상득', '이석기', '이완구', '이인제', '이정희', '이재명', '이준석', '이태임', '이한구',
    '자우림', '장하성', '장하준', '전여옥', '정동영', '정문헌', '정봉주', '정윤회', '정준하', '정청래', '정형돈', '조용기', '조현아', '조현오', '주진우', '진중권',
    '채널A', '최시중', '최태원',
    '타진요', '타블로', '통진당', '통합진보',
    '페이스북', '표창원',
    '홍명보',
    'JTBC',
    'KBS',
    'MBC',
    'SBS', 'SNS',
    'TV조선',
}
BLACKLIST_TAGS = {
    '내가',
    '뉴스',
    '단독',
    '종합',
}


def main():
    kkma = Kkma()
    for dt in enum_dates(START_DATE, datetime.now().date()):
        trends = set(get_trending_words_at(kkma, dt)).union(KNOWN_TAGS)
        for a in get_news_at(dt):
            keywords = extract_keywords(kkma, a)
            tags = list(set(keywords).intersection(trends))
            print(a['title'])
            print(', '.join(tags))
            print()


def get_trending_words_at(kkma, dt, window=30):
    today = datetime.now().date()
    date_end = dt + timedelta(days=window)
    date_start = dt - timedelta(days=window)
    if date_start < START_DATE:
        date_start = START_DATE
        date_end = date_start + timedelta(days=window)
    elif date_end >= today:
        date_end = today
        date_start = date_end - timedelta(days=window)

    words = []
    for d in enum_dates(date_start, date_end):
        words += _get_trending_words_at(kkma, d, 20)

    freq_words = Counter(words).most_common(3000)
    return [word for (word, n) in freq_words]


@functools.lru_cache(maxsize=128)
def _get_trending_words_at(kkma, dt, n_sample):
    words = []
    for a in get_news_at(dt)[:n_sample]:
        words += extract_words(kkma, a['title'])
    return words


def get_news_at(dt):
    filename = 'data/{}.json'.format(dt.strftime('%Y%m%d'))
    data = None
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            data = f.read()
    else:
        data = fetch_news_at(dt)
        with open(filename, 'w') as f:
            f.write(data)
    return json.loads(data)['bestreplyNewsList']


def fetch_news_at(dt):
    url = 'http://m.media.daum.net/api/service/bestreply/{}.json?limit={}&scope=0&type=mobile'.format(dt.strftime('%Y%m%d'), 100)
    with urllib.request.urlopen(url) as res:
        return res.read().decode('utf-8')


def extract_words(kkma, text):
    words = []
    for known in KNOWN_TAGS:
        if text.find(known) != -1:
            text = text.replace(known, 'X')
            words.append(known)

    words += [
        token for (token, tag) in kkma.pos(text)
        if len(token) > 1 and tag[:2] == 'NN' and token not in BLACKLIST_TAGS
    ]

    return words


def extract_keywords(kkma, article):
    title = article['title']
    summary = article['summary']

    # Preprocessing
    if article['cpKorName'] == '연합뉴스':
        summary = summary.split('(끝)')[0]

    # Give more weight to title
    source = '. '.join([title, title, summary])
    nouns = extract_words(kkma, source)

    # Filter most frequent nouns
    freq_nouns = Counter(nouns).most_common(30)
    return [noun for (noun, n) in freq_nouns if noun in KNOWN_TAGS or n > 1]


def enum_dates(start, end):
    while start <= end:
        yield start
        start += timedelta(days=1)


if __name__ == '__main__':
    main()
