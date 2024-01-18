import jieba
import jieba.analyse
import os
from whoosh import fields
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.query import Every
from whoosh.query import And,Or


def tokenize(text):
    words = jieba.lcut(text.replace(' ',''))
    #print(words)
    # 加载停用词表
    stop_words_path = 'hit_stopwords.txt'
    stop_words = set()
    with open(stop_words_path, 'r', encoding='utf-8') as file:
        for line in file:
            stop_words.add(line.strip())
    filtered_words = [word for word in words if word not in stop_words]
    return filtered_words

def create_index(documents): #创建倒排索引
    # 创建索引目录
    index_dir = 'index'
    analyzer = jieba.analyse.ChineseAnalyzer()
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
    schema = fields.Schema(id=fields.ID(unique=True, stored=True),content=fields.TEXT(stored=True, analyzer=analyzer))
    ix = create_in(index_dir, schema)
    # 打开索引目录
    ix = open_dir(index_dir)
    # 获取写入器
    writer = ix.writer()
    # 将文档添加到索引
    for sub,doc in enumerate(documents):
        writer.add_document(id=str(sub),content=doc['content'])
    # 提交更改
    writer.commit()

def search_index(search_query):
    # 打开索引目录
    ix = open_dir('index')
    # 创建查询解析器
    analyzer = jieba.analyse.ChineseAnalyzer()
    schema = fields.Schema(id=fields.ID(unique=True, stored=True),content=fields.TEXT(stored=True, analyzer=analyzer))
    qp = QueryParser("content", schema=schema)
    # 创建模糊查询列表
    fuzzy_queries = [qp.parse(f"{keyword}*") for keyword in search_query]
    # 创建布尔查询
    boolean_query = Or(fuzzy_queries)
    # 执行搜索
    with ix.searcher() as searcher:
        results = searcher.search(boolean_query)
        # 输出匹配的文档
        result = []
        if len(results) > 0:
            for i in range(len(results)):
                #print(results[i]['content'])
                result.append(int(results[i]['id']))
        return result

def full_text_search(text,documents):
    tokens = tokenize(text)
    create_index(documents)
    result = search_index(tokens)
    return result

'''
text = "对面唯一有机会的一局"
documents = [
    {"content": "盘外招不能说没用，只能在特殊情况用。08这种老手，什么场面没见过，对盘外招他是相当熟悉了，不管别人怎么操作都有应对技巧。但如果你换个不熟悉的人来，很容易就翻车了。说白了还是针对不了解的，对付那些经验丰富的高手没什么用"},
    {"content": "对面唯一有机会的一局就是3号打8号那把，一开始不应该造兵以免影响重工进度，重工出来卖基地，等出了3坦克1防空车（可偷+防飞行兵）再果断卖重工爆兵，这样还有可能打得下"},
    {"content": "允许，一个牛你还有精力手动控制，等牛多了不手动操作的话就容易堵矿，中后期大规模坦克交战或者小规模坦克分兵，如果还敢分精力飞矿，很容易被人抓住坦克发呆的漏洞"}
]
result = full_text_search(text,documents)
#print(result)
'''

