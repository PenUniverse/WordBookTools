import json
import os
import sys

VERSION             = "1.0.0"
WORDBOOK_VERSION    = 100

SUPPORTED_DICTS = {
    "Senior": "高中生词典",
    "PureEnglishAndExample": "有道简明释义"
}

def printLogo():
    print("""┌───────────────────────────────────┐
│                                   │
│       ╔═╗┌─┐┌┐┌╔╦╗┌─┐┌┬┐┌─┐       │
│       ╠═╝├┤ │││║║║│ │ ││└─┐       │
│       ╩  └─┘┘└┘╩ ╩└─┘─┴┘└─┘       │
│                                   │
└───────────────────────────────────┘
Welcome to use WordBookTools!
Developer:  RedbeanW
Repo:       https://github.com/PenUniverse/WordBookTools
Version:    %s""" % VERSION)

def terminate(msg:str = None):
    if msg:
        print(msg)
    os.system('pause')
    sys.exit(-1)

if __name__ == '__main__':
    
    printLogo()

    if not os.path.exists('WordBook.json'):
        terminate('请将 WordBook.json 放在脚本同级目录再重试。')
    
    obj = None
    try:
        with open('WordBook.json', 'r', encoding='utf-8') as file:
            obj = json.load(file)
    except:
        terminate('解析 WordBook.json 时出错...')

    if obj["version"] != WORDBOOK_VERSION:
        terminate('不支持的单词本导出格式，版本不匹配（%s!=%s）' % (obj["version"], WORDBOOK_VERSION))
    else:
        obj = obj["data"]

    sorted_words = []
    handled_words = []

    fromSenior  = obj["Senior"]
    fromPureEng = obj["PureEnglishAndExample"]

    # Sort all words.

    for i in range(5):
        frequency = 5 - i
        for word in fromSenior:
            if frequency == fromSenior[word]["frequency"]:
                sorted_words.append(word)
    
    for word in fromPureEng:
        if word not in sorted_words: # can improve performance
            sorted_words.append(word)
    
    # Handle

    result = str()
    count = 0
    max = len(sorted_words)

    for word in sorted_words:
        count += 1
        # priority [senior]->[pure_eng]
        if word in fromSenior:
            print('[processing(%s/%s)|Senior] "%s".' % (count, max, word))
            item = fromSenior[word]
            
            ## handle marker
            mark = min(item["frequency"], 3) * '\*'
            
            ## handle trans
            tset = {}
            for t in item["trans"]:
                key = t["pos"]
                if key in tset:
                    tset[key] += '；' + t['sense']
                else:
                    tset[key] = t['sense']
            trans = ''
            for pos in tset:
                trans += ('*%s* %s | ' % (pos, tset[pos]))
            trans = trans[:len(trans) - 3]

            ## handle idiomatic
            idios = ''
            if "idiomatic" in item:
                is_final_idio_has_colloc = False
                for idio in item["idiomatic"]:
                    idios += "**`%s`** %s" % (idio["colloc"]["en"], idio["colloc"]["zh"])
                    if "sents" in idio:
                        idios += '\n\n> %s\n> %s\n\n' % (idio["sents"][0]['en'], idio["sents"][0]['zh'])
                        is_final_idio_has_colloc = True
                    else:
                        idios += '\n'
                        is_final_idio_has_colloc = False
                if not is_final_idio_has_colloc:
                    idios += '\n'
            
            ## generate this word
            result += "### %s%s\n\n###### %s\n\n%s" % (word, '', trans, idios)
        elif word in fromPureEng:
            print('[processing(%s/%s)|PureEng] "%s".' % (count, max, word))
            item = fromPureEng[word]

            ## handle trans
            trans = ''
            for t in item['pure']['word']['trs']:
                if 'pos' in t:
                    trans += (' *%s* %s | ' % (t['pos'], t['tran']))
                else:
                    trans += (' %s | ' % (t['tran']))
            trans = trans[:len(trans) - 3]

            result += "**%s**%s\n" % (word, trans.replace('【','[').replace('】',']'))

    
    with open('WordBook.md', 'w+', encoding='utf-8') as file:
        file.write(result)
    
    print("Completed, see 'WordBook.md'.")
    