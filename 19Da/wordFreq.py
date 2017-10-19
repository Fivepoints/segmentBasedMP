from bs4 import BeautifulSoup
import requests
import jieba
import nltk
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

def getFullText():
    '''
    获取全文，共32491字
    :return:
    '''
    startUrl = "http://www.china.com.cn/cppcc/2017-10/18/content_41752399.htm"
    fullText = ''
    html = requests.get(startUrl)
    html.encoding = 'utf-8'
    text = html.text
    # print(text)
    soup = BeautifulSoup(text, 'html.parser')
    pS = soup.body.find_all('p')
    for p in pS[:-5]:
        if p.strings is not None:
            for string in p.stripped_strings:
                fullText += ''.join(string.split())
    print(fullText)
    print(len(fullText))
    return fullText

def parseText(Text,topN=100):
    stopWords = []
    fr = open('stopWords.txt')
    for line in fr.readlines():
        stopWords.append(line.strip())

    word_counts = nltk.defaultdict(int)
    wordList = jieba.cut(Text, cut_all=False)
    for word in wordList:
        if word not in stopWords:
            word_counts[word] += 1
    fdist = nltk.FreqDist(word_counts)
    topN = fdist.most_common(topN)
    print(topN)
    return topN
    # print(word_counts['发展'])

def plotWordCloud():
    text = getFullText()
    topN = parseText(text, 500)
    font = os.path.join(os.path.dirname(__file__), "DroidSansFallbackFull.ttf")
    wordcloud = WordCloud(font_path=font).fit_words(dict(topN))

    plt.imshow(wordcloud)
    plt.axis("off")

    plt.show()