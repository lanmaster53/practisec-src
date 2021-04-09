import codecs
import json
from urllib.request import urlopen

base_url = 'https://publish.twitter.com/oembed?url={}?&hide_media=true&hide_thread=true&omit_script=true'

urls = [u for u in open('tweets.txt').read().split() if not u.startswith('#')]

tweets = []
for tweet_url in urls:
    url = base_url.format(tweet_url)
    try:
        resp = urlopen(url)
    except Exception as e:
        if e.code in [403, 404]:
            print(f"#{tweet_url}")
            continue
        raise
    print(tweet_url)
    markup = json.load(resp)['html']
    markup = markup.replace('class="twitter-tweet"', 'class="twitter-tweet tw-align-center"')
    tweets.append(markup)

with codecs.open('./templates/testimonials.html', 'w', encoding="utf-8") as fp:
    fp.write(u'''\
{}
'''.format(''.join(tweets).strip()))
