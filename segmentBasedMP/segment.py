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
                       '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖', '拾', '佰', '仟', '万','亿',
                       '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '○' , '－', '点', '分','之']
        self.English = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
                   'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                   'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        self.Time = ['年', '月', '日', '时', '分', '秒']

    def loadVocablist_1998(self):
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

    def loadVocablist_pku(self):
        '''
        load the vocab
        :return:
        '''

        print('start load set...')
        fr = open('pku_training.utf8')
        for line in fr.readlines():
            # 去除空格以及空行
            line = line.strip()
            lineArr = line.split()
            for index, word in enumerate(lineArr):
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

        # 用于记录那些词典外的词汇
        OOV = {}

        # 用于存储那些还不确定的部分
        tmpWords = ''
        for line in testFile.readlines():
            line = line.strip()

            needSegList = []

            # 是否以数字开头
            numberFlag = 0

            # 英文单词的识别
            englishFlat = 0
            for part in line:
                if part in self.Number or part in self.English:
                    if tmpWords != '':
                        if numberFlag == 0:
                            needSegList.append((tmpWords, 1))
                            tmpWords = part
                            numberFlag = 1
                        else:
                            tmpWords += part
                    else:
                        numberFlag = 1
                        tmpWords = part

                elif part in self.Punctuation:
                    if tmpWords != '':
                        if numberFlag == 1:
                            needSegList.append((tmpWords, 0))
                        else:
                            needSegList.append((tmpWords, 1))
                    needSegList.append((part, 0))
                    numberFlag = 0
                    tmpWords = ''

                # 2001年 日期类
                elif part in self.Time and numberFlag == 1:
                    tmpWords += part
                    needSegList.append((tmpWords, 0))
                    tmpWords = ''
                    numberFlag = 0

                # 21 全是数字类
                else:
                    if numberFlag == 1:
                        needSegList.append((tmpWords, 0))
                        numberFlag = 0
                        tmpWords = part
                    else:
                        tmpWords += part

            if tmpWords != '':
                needSegList.append((tmpWords, 1))
            tmpWords = ''

            finalSeg = []
            for seg, status in needSegList:
                # 说明不需要切分了
                if status == 0:
                    finalSeg.append(seg)
                else:
                    fmmSeg = self.FMMsegment(seg)
                    rmmSeg = self.RMMsegment(seg)

                    probFMM = self.calSegProb(fmmSeg)
                    probRMM = self.calSegProb(rmmSeg)

                    if probFMM > probRMM:
                        for item in fmmSeg:
                            finalSeg.append(item)
                    else:
                        for item in rmmSeg:
                            finalSeg.append(item)
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
        print('start evaluate ...')
        test_result_file = open('pku_test_result.utf8')
        test_gold_file = open('pku_test_gold.utf8')

        result_cnt = 0.0
        gold_cnt = 0.0
        right_cnt = 0.0

        for line1, line2 in zip(test_result_file, test_gold_file):
            result_list = line1.strip().split('  ')
            gold_list = line2.strip().split('  ')
            for words in gold_list:
                if words == '':
                    gold_list.remove(words)
            for words in gold_list:
                if words == '':
                    result_list.remove(words)

            result_cnt += len(result_list)
            gold_cnt += len(gold_list)
            for words in result_list:
                if words in gold_list:
                    right_cnt += 1.0
                    gold_list.remove(words)

        p = right_cnt / result_cnt
        r = right_cnt / gold_cnt
        F = 2.0 * p * r / (p + r)

        print('right_cnt: \t\t', right_cnt)
        print('result_cnt: \t', result_cnt)
        print('gold_cnt: \t\t', gold_cnt)
        print('P: \t\t', p)
        print('R: \t\t', r)
        print('F: \t\t', F)


if __name__ == '__main__':
    segment = Segment()
    segment.loadVocablist_pku()
    segment.control()
    segment.evaluate()
    # 要切分的短语 。
    # inputString = '''他是研究生物和化学的'''
    # rawText = ''.join(inputString.split())
    # FMMseg = segment.FMMsegment(rawText)
    # RMMseg = segment.RMMsegment(rawText)
    # segment.segs2str(FMMseg)
    # segment.segs2str(RMMseg)
    # print(segment.calSegProb(FMMseg))
    # print(segment.calSegProb(RMMseg))


