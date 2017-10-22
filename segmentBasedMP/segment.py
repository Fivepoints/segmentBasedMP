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
        self.Punctuation = ['、','”','“','。','（','）','：','《','》','；','！','，','、']
        self.Number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '%', '.', '壹',
                       '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖', '拾', '佰', '仟', '万','亿', '○']
        self.English = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
                   'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                   'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        self.Time = ['年', '月', '日', '时']

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

    def control(self):
        '''
        切分主函数
        :return:
        '''
        print('start segment words ...')

        testFile = open('pku_test.utf8')
        testResult = open('pku_test_result.utf8', 'w')

        # 记录测试的条目数
        segListCnt = 0

        # 用于记录那些词典外的词汇
        OOV = {}

        # 用于存储那些还不确定的部分
        tmpWords = ''
        for line in testFile.readlines():
            line = line.strip()
            segList = []

            # 是否以数字开头
            flag = 0
            for part in line:
                if part in self.Number:
                    flag = 1
                    tmpWords += part

                elif part in self.Punctuation:
                    if tmpWords != '':
                        segList.append(tmpWords)
                        segListCnt += 1
                        segList.append(part)
                        if flag == 1:
                            OOV[tmpWords] = 1
                            flag = 0
                    tmpWords = ''

                # 2001年
                elif part in self.Time:
                    if tmpWords != '':
                        tmpWords += part
                        segList.append(tmpWords)
                        segListCnt += 1
                        if flag ==1:
                            OOV[tmpWords] = 1
                            flag = 0
                    tmpWords = ''

                # 21 全是数字
                else:
                    if flag == 1:
                        segList.append(tmpWords)
                        segListCnt += 1
                        OOV[tmpWords] = 1
                        flag = 0
                        tmpWords = part
                    else:
                        tmpWords += part

            if tmpWords != '':
                segList.append(tmpWords)
                segListCnt += 1
                if flag == 1:
                    OOV[tmpWords] = 1
            tmpWords = ''

            for seg in segList:
                if seg not in self.Punctuation or seg not in OOV:

                    # 分别使用fmm和rmm计算词序列
                    fmmSeg = self.FMMsegment(line)
                    rmmSeg = self.RMMsegment(line)

                    fmmSeg.insert(0, 'B')
                    fmmSeg.append('E')
                    rmmSeg.insert(0, 'B')
                    rmmSeg.append('E')

                    probFMM = self.calSegProb(fmmSeg)
                    probRMM = self.calSegProb(rmmSeg)

                    finalSeg = []

                    # CalList1和CalList2分别记录两个句子词序列不同的部分
                    CalList1 = []
                    CalList2 = []

                    # pos1和pos2记录两个句子的当前字的位置，cur1和cur2记录两个句子的第几个词
                    pos1 = pos2 = 0
                    cur1 = cur2 = 0
                    while (1):
                        if cur1 == len(fmmSeg) and cur2 == len(rmmSeg):
                            break
                        # 如果当前位置一样
                        if pos1 == pos2:
                            # 当前位置一样，并且词也一样
                            if len(fmmSeg[cur1]) == len(rmmSeg[cur2]):
                                pos1 += len(fmmSeg[cur1])
                                pos2 += len(rmmSeg[cur2])
                                # 说明此时得到两个不同的词序列，根据bigram选择概率大的
                                # 注意算不同的时候要考虑加上前面一个词和后面一个词，拼接的时候再去掉即可
                                if len(CalList1) > 0:
                                    CalList1.insert(0, finalSeg[-1])
                                    CalList2.insert(0, finalSeg[-1])
                                    if cur1 < len(fmmSeg) - 1:
                                        CalList1.append(fmmSeg[cur1])
                                        CalList2.append(rmmSeg[cur2])

                                    p1 = self.calSegProb(CalList1)
                                    p2 = self.calSegProb(CalList2)
                                    if p1 > p2:
                                        CalList = CalList1
                                    else:
                                        CalList = CalList2
                                    CalList.remove(CalList[0])
                                    if cur1 < len(fmmSeg) - 1:
                                        CalList.remove(fmmSeg[cur1])
                                    for words in CalList:
                                        finalSeg.append(words)
                                    CalList1 = []
                                    CalList2 = []
                                finalSeg.append(fmmSeg[cur1])
                                cur1 += 1
                                cur2 += 1
                            # pos1相同，len(ParseList1[cur1])不同，向后滑动，不同的添加到list中
                            elif len(fmmSeg[cur1]) > len(rmmSeg[cur2]):
                                CalList2.append(rmmSeg[cur2])
                                pos2 += len(rmmSeg[cur2])
                                cur2 += 1
                            else:
                                CalList1.append(fmmSeg[cur1])
                                pos1 += len(fmmSeg[cur1])
                                cur1 += 1
                        else:
                            # pos1不同，而结束的位置相同，两个同时向后滑动
                            if pos1 + len(fmmSeg[cur1]) == pos2 + len(rmmSeg[cur2]):
                                CalList1.append(fmmSeg[cur1])
                                CalList2.append(rmmSeg[cur2])
                                pos1 += len(fmmSeg[cur1])
                                pos2 += len(rmmSeg[cur2])
                                cur1 += 1
                                cur2 += 1
                            elif pos1 + len(fmmSeg[cur1]) > pos2 + len(rmmSeg[cur2]):
                                CalList2.append(rmmSeg[cur2])
                                pos2 += len(rmmSeg[cur2])
                                cur2 += 1
                            else:
                                CalList1.append(fmmSeg[cur1])
                                pos1 += len(fmmSeg[cur1])
                                cur1 += 1
            finalSeg.remove('B')
            finalSeg.remove('E')
            testResult.write('  '.join(finalSeg)+'\n')
        testFile.close()
        testResult.close()
        print('segment words done!...')

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

    def calSegProb(self, segList):
        '''
        计算切分列表的概率
        :param segS:
        :return:由于x1*x2等因子太小，连续相乘可能会造成下溢出或为0，
        故对数ln x1 + ln x2 = ln(x1*x2),根据ln的图像，返回的prob值越大，概率越大
        '''
        prob = 0
        for index, word in enumerate(segList):
            #如果不是切分列表的最后一个
            if index < len(segList) - 1:
                word1, word2 = word, segList[index + 1]
                if word1 not in self.nextWordList:
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

    def evaluate(self):
        return None

if __name__ == '__main__':
    segment = Segment()
    segment.loadVocablist()
    segment.control()
    # 要切分的短语 。
    # inputString = '''他是研究生物和化学的'''
    # rawText = ''.join(inputString.split())
    # FMMseg = segment.FMMsegment(rawText)
    # RMMseg = segment.RMMsegment(rawText)
    # segment.segs2str(FMMseg)
    # segment.segs2str(RMMseg)
    # print(segment.calSegProb(FMMseg))
    # print(segment.calSegProb(RMMseg))


