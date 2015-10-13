#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# coding=utf-8

from collections import Iterable
import types, pymongo


keypath=[]
matchbox={}
dotretval=[]

connection=pymongo.MongoClient("localhost",27017)
db=connection.MDP
collection=db.behavior

def _saveMatch(keyPath, val):
    global matchbox
    if type(val) is types.DictType:
        for t3Key, t3Val in val.iteritems():
            keypath.append(t3Key)
            _saveMatch(keypath, t3Val)
            keypath.pop()
    elif type(val) is types.ListType:
        for t4Val in val:
            _saveMatch(keyPath, t4Val)
    else:
        key=".".join(keypath)
        if key not in matchbox:
            matchbox[key]=[]

        if key in matchbox:
            # only unique values are saved
            if val not in matchbox[key]:
                matchbox[key].append(val)
            else:
                pass


def _deepDive(t1, t2):
    global keypath
    try:
        for t1Key, t1Val in t1.iteritems():
            for t2Key, t2Val in t2.iteritems():
                keypath.append(t2Key)
                if t1Key == t2Key:
                    if t1Val==t2Val:
                        _saveMatch(keypath, t2Val)
                    else:
                        if isinstance(t1[t1Key], Iterable) and isinstance(t2[t2Key], Iterable):
                            if type(t1[t1Key])==types.ListType and type(t2[t2Key])==types.ListType:
                                for t1Element in t1[t1Key]:
                                    for t2Element in t2[t2Key]:
                                        _deepDive(t1Element, t2Element)
                            else:
                                _deepDive(t1[t1Key], t2[t2Key])
                keypath.pop()
    except AttributeError:
        if type(t1)==types.ListType and type(t2)==types.ListType:
            for t1Element in t1:
                for t2Element in t2:
                    if isinstance(t1Element, Iterable) and isinstance(t2Element, Iterable):
                        _deepDive(t1Element, t2Element)


def _getvalfromDot(item, dotKey):
    global dotretval

    myKey=dotKey.split(".")[0]
    nxKey=".".join(dotKey.split(".")[1:])

    try:
        if not myKey and not nxKey:
            return dotretval.append(item)
        elif myKey and not nxKey:
            if type(item)==types.ListType:
                for lItem in item:
                    _getvalfromDot(lItem, nxKey)
        elif type(item)==types.DictType:
            _getvalfromDot(item[myKey], nxKey)
        else:
            return dotretval.append(item)
    except KeyError or TypeError:
        for lItem in item:
            _getvalfromDot(lItem, nxKey)
    

def _isKeyValIn(queryKey, queryVal, dotKey, dotVal):
    item=collection.find_one({queryKey:queryVal})
    if _getvalfromDot(item, dotKey)==dotVal:
        return True
    else:
        return False


def _findNext(common_key_val, queryKey, queryVal):
    for key, lst in common_key_val.iteritems():
        for val in lst:
            if _isKeyValIn(queryKey, queryVal, key, val):
                pass
            else:
                common_key_val[key].remove(val)

    for key in common_key_val.keys():
        if None in common_key_val[key]:
            common_key_val[key].remove(None)
        if not common_key_val[key]:
            del common_key_val[key]
            
    return common_key_val


def findCommon(targetList):
    global matchbox

    dicts=[]
    for i in collection.find(
            {
                '$or':
                [
                    {'md5sum':targetList[0]},
                    {'md5sum':targetList[1]}
                ]
            }
    ):
        dicts.append(i)

    t1=dicts[0]
    t2=dicts[1]
    _deepDive(t1, t2)

    for target in targetList[2:]:
        matchbox=_findNext(matchbox, 'md5sum', target)

    return matchbox


if __name__ == '__main__':
    import pprint
    pp=pprint.PrettyPrinter(indent=4)
    pp.pprint(findCommon([
        "0dfb1e9514ba3532420797a899c9d8a2",
        "07e7818173bab6845c17a497c0548b8f",
        "33260729d51bd8573a5f42faf19ed8c3",
        "122077e2a3fc214aa179c171972df056",
        "73b2ee6ea6ff72684531c69910abe122",
        "f44a5771505a64cec95889b6e0b3fe71",
        # "3bc61f0720aa1dc9a8a6656b814c4d7a",
        # "f4908839f43415acec8482314c618800",
        # "1d985e5d80f78ead3e80d5428bba429c",
        # "0d881c8d165ed96d0b929b8e7e8c0242",
        # "b9f0a3ec3735f160dd43439d7d15e94b",
        # "5c33e403d1840347a2f40906cafebf91",
        # "1847d671084913dbd26b543bb76ecb70",
        # "1a86982dea6964528f9456fd856fbee0",
    ]))



# 뽑아낸 Key Value를 Chromeless Window에 테이블 형태로 뿌려준다음,
# 해당 테이블의 Element 선택시 Query History Append

# 추가적으로 결과로 나온 결과로 3번째 Diff와 Match해야 함.
# 이를 위해 여기서 뽑아져나온 데이터를 다시 Dict형태로 재 가공.
# 또는 해당 리스트에서 Data 추출해서 None 또는 Exception나타나면, 종료.
