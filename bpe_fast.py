# coding: utf-8

import re, sys, json, time, collections

try:
    import Queue as Q
except ImportError:
    import queue as Q

class WordPhrase():
    def __init__(self):
        self.word_phrase = collections.defaultdict(set)
        self.max_id = 0
        self.phrase_id = {}
        self.id_phrase = {}

    def replace(self, pair, s, d):
        if s == d:
            return
        id = self.phrase_id[s]
        del self.phrase_id[s]
        self.phrase_id[d] = id
        self.id_phrase[id] = d

        nws = d.split()
        if not pair[0] in nws:
            assert id in self.word_phrase[pair[0]]
            self.word_phrase[pair[0]].remove(id)
        if not pair[1] in nws and pair[0]!=pair[1]:
            self.word_phrase[pair[1]].remove(id)
        self.word_phrase[''.join(pair)].add(id)

    def get_hit_phrases(self, pair):
        hit_ids = self.word_phrase[pair[0]] & self.word_phrase[pair[1]]
        return [self.id_phrase[id] for id in hit_ids]

    def add(self, word, symbols):
        assert not word in self.phrase_id
        self.phrase_id[word] = self.max_id

        assert not self.max_id in self.id_phrase
        self.id_phrase[self.max_id] = word

        for symbol in symbols:
            self.word_phrase[symbol].add(self.max_id)
        self.max_id += 1

def get_stats(vocab):
    pairs = collections.defaultdict(int)
    word_phrase = WordPhrase()
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols)-1):
            pairs[symbols[i],symbols[i+1]] += freq
        word_phrase.add(word, symbols)
    return pairs, word_phrase

class WordCount():
    def __init__(self, word, count):
        self.word = word
        self.count = count
    def __lt__(self, other):
        return self.count > other.count

def merge_vocab(pairs, wp, pair, vocab, pq):
    bigram = re.escape(' '.join(pair))
    hit_phrases = wp.get_hit_phrases(pair)
    p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
    delta = collections.defaultdict(int)
    for word in hit_phrases:
        new_word = p.sub(''.join(pair), word)
        if new_word == word:
            continue
        nws = new_word.split()
        num = vocab[word]
        vocab[new_word] = vocab[word]
        del vocab[word]

        wp.replace(pair, word, new_word)

        ws = word.split()
        for i in range(1, len(nws)):
            delta[nws[i-1], nws[i]] += num
        for i in range(1, len(ws)):
            delta[ws[i-1],ws[i]] -= num

    for k, v in delta.iteritems():
        if v == 0:
            continue
        pairs[k] += v
        if v<0 and pairs[k] <= 0:
            if not pairs[k] == 0:
                print json.dumps(k,ensure_ascii=False).encode('utf-8'), pairs[k]
            assert pairs[k] == 0
            del pairs[k]
        else:
            pq.put(WordCount(k, pairs[k]))

def get_max(pairs, pq):
    while not pq.empty():
        tmp = pq.get()
        if tmp.word in pairs and pairs[tmp.word] == tmp.count:
            return tmp.word

fp = open(sys.argv[1])
vocab = {}
for line in fp:
    line = line.strip().decode('utf-8')
    w,num = line.split('\t')
    cs = [c for c in w]
    w = ' '.join(cs)
    vocab[w] = long(num)
fp.close()

num_merges = 500000

pairs, word_phrase = get_stats(vocab)
pq = Q.PriorityQueue()
for w, c in pairs.iteritems():
    pq.put(WordCount(w,c))

for i in range(num_merges):
    st = time.time()
    #best = max(pairs, key=pairs.get)
    if not pairs:
        break
    best = get_max(pairs, pq)
    #print time.time() - st

    print 'id:', i, best[0].encode('utf-8'), best[1].encode('utf-8'), pairs[best]
    merge_vocab(pairs, word_phrase, best, vocab, pq)
    print time.time() - st
    #print '============================='
