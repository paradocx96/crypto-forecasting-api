import requests
from bs4 import BeautifulSoup
from config import HEADER

# html tags need to be scrapped
from sentiment_analysis import predict

TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span', 'td', 'li', 'a']
SOURCES = ['https://cointelegraph.com/', 'https://news.bitcoin.com/']
sentiment = 'Not Available'
sentiment_score = 0


def get_sentiment_score():
    return sentiment_score


def set_sentiment_score(_sentiment_score):
    global sentiment_score
    sentiment_score = _sentiment_score


def get_sentiment():
    return sentiment


def set_sentiment(_sentiment):
    global sentiment
    sentiment = _sentiment


def test_with_bs4(url):
    response = requests.get(url, headers=HEADER)
    soup = BeautifulSoup(response.text, "html.parser")
    file = open("test.html", "w+")
    file.write(str(soup))
    file.close()


def scrapping_sentences(url):
    sentences = []
    # download html page of the website
    response = requests.get(url, headers=HEADER)
    # parse with bs4
    soup = BeautifulSoup(response.text, "html.parser")
    # iterate through html tags
    for tag in TAGS:
        # find all inner texts for the tag
        rows = soup.find_all(tag)
        # iterate through all rows found related to the given tag
        for row in rows:
            # inner text to lower
            sentence = row.get_text().lower()
            # keep only alphabet
            sentence = ''.join(x for x in sentence if x.isalpha() or x == ' ')
            sentences.append(sentence)
    return sentences


def start_web_scrapping():
    m = {
        1: 0,
        0: 0
    }
    for source in SOURCES:
        sentences = scrapping_sentences(source)
        for sentence in sentences:
            if len(sentence.strip()) > 0:
                # there should be a minimum 6 words
                if len(sentence.split()) >= 6:
                    pred = predict(sentence)
                    m[pred] += 1

    score = m[1] / (m[1] + m[0]) * 100

    if m[1] > m[0]:
        set_sentiment('Positive')
        set_sentiment_score(round(score, 2))
    else:
        set_sentiment('Negative')
        set_sentiment_score(round(100 - score, 2))


# only for testing
'''
if __name__ == "__main__":
    start_web_scrapping()
'''
