#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @desc:  root algorithm
 @author: Zhao Pengya
 @created: 17-10-20
 @software: PyCharm python 3.5.3

"""

from math import log
class Segment():
    def __init__(self):
        self.vocabList = {}
        self.nextWordList = {}
        self.vocabSize = 0
        self.tokenSize = 0
        self.Punctuation = [u'、',u'”',u'“',u'。',u'（',u'）',u'：',u'《',u'》',u'；',u'！',u'，',u'、']

    def loadVocablist(self):
        '''
        load the vocab
        :return:
        '''

        print('start load set...')
        fr = open('199801.txt')
        for line in fr.readlines():
            # 去除空格以及空行
            line = line.strip()
            lineArr = line.split()[1:]
            for index, word_Tag in enumerate(lineArr):
                # 得到单词以及词性
                word, tag = word_Tag.split('/')
                if word not in self.Punctuation:
                    if word not in self.vocabList:
                        self.vocabList[word] = 1
                    else:
                        self.vocabList[word] += 1

                    if index == 0:
                        word1, word2 = 'B', word
                    elif index == len(lineArr) - 1:
                        word1, word2 = word, 'E'
                    else:
                        word1, word2 = word, lineArr[index+1].split('/')[0]
                    if word1 not in self.nextWordList:
                        self.nextWordList[word1] = {}
                    if word2 not in self.nextWordList[word1]:
                        self.nextWordList[word1][word2] = 1
                    else:
                        self.nextWordList[word1][word2] += 1
                    self.tokenSize += 1
        self.vocabSize = len(self.vocabList)
        print('load set is done!')
        print('vocabSize is %d' % self.vocabSize)
        print('tokenSize is %d' % self.tokenSize)
        fr.close()

    def findMaxWord(self):
        '''
        计算词典中最长词的长度
        :param vocabList:
        :return:
        '''
        max = 0
        for word, nums in self.vocabList.items():
            if len(word) > max:
                max = len(word)
                print(word)
        return max

    def FMMsegment(self, rawText, maxLength = 7):
        '''
        正向最大匹配法
        根据输入的字符串返回多个有可能的切分
        :param inputString:
        :return:
        '''
        seg = []
        length = len(rawText)
        startIndex = 0; endIndex = startIndex + maxLength
        while (startIndex < length):
            wordSeg = rawText[startIndex:endIndex]
            if wordSeg in self.vocabList.keys():
                seg.append(wordSeg)
                startIndex = endIndex
                endIndex = startIndex + maxLength
            else:
                # OOV 转化为单个字母
                if ((endIndex - 1 == startIndex) and wordSeg not in self.vocabList.keys()):
                    seg.append(wordSeg)
                    startIndex += 1
                    endIndex = startIndex + maxLength
                else:
                    endIndex -= 1
        return seg

    def RMMsegment(self, rawText, maxLength = 7):
        '''
        逆向最大匹配法
        根据输入的字符串返回多个有可能的切分
        :param inputString:
        :return:
        '''
        seg = []
        length = len(rawText)
        startIndex = length;
        endIndex = startIndex - maxLength
        while (startIndex >= 0):
            wordSeg = rawText[(endIndex if endIndex > 0 else 0) :startIndex]
            if wordSeg in self.vocabList.keys():
                seg.append(wordSeg)
                startIndex = endIndex
                endIndex = startIndex - maxLength
            else:
                # OOV 转化为单个字母
                if ((endIndex + 1 == startIndex) and wordSeg not in self.vocabList.keys()):
                    seg.append(wordSeg)
                    startIndex -= 1
                    endIndex = startIndex - maxLength
                else:
                    endIndex += 1
        # 对切分列表进行倒置
        seg = seg[::-1]
        return seg

    def n_gram(self, n = 2):
        return None

    def calSegProb(self, segList):
        '''
        计算切分列表的概率
        :param segS:
        :return:返回的由于x1*x2等概率太小，故对数ln x1 + ln x2 = ln(x1*x2),根据ln的图像，返回的prob越小， 概率越大
        '''
        prob = 0
        for index, word in enumerate(segList):
            #如果不是切分列表的最后一个
            if index < len(segList) - 1:
                word1, word2 = word, segList[index + 1]
                if word1 not in self.vocabList:
                    # add-One 平滑处理
                    prob += log(1.0 / self.vocabSize)
                else:
                    fenzi, fenmu = 1.0, self.vocabSize
                    for tmpWord in self.nextWordList[word1]:
                        if tmpWord == word2:
                            fenzi += self.nextWordList[word1][tmpWord]
                        fenmu += self.nextWordList[word1][tmpWord]
                    prob += log(fenzi / fenmu)

        #    别忘了计算第一个p(w1)的概率
        if index == 0:
            if word not in self.vocabList:
                prob += log(1.0 / self.tokenSize + self.vocabSize)
            else:
                prob += log(self.vocabList[word] + 1 / self.tokenSize + self.vocabSize)
        return prob


    def segs2str(self, seg):
        print('  '.join(seg))

if __name__ == '__main__':
    segment = Segment()
    segment.loadVocablist()
    # 要切分的短语 。
    inputString = '''他是研究生物和化学的'''
    rawText = ''.join(inputString.split())
    FMMseg = segment.FMMsegment(rawText)
    RMMseg = segment.RMMsegment(rawText)
    # result = calMaxProb(segS)
    segment.segs2str(FMMseg)
    segment.segs2str(RMMseg)
    print(segment.calSegProb(FMMseg))
    print(segment.calSegProb(RMMseg))


