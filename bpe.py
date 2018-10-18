
import re, sys, time, collections

def get_stats(vocab):
    pairs = collections.defaultdict(int)
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols)-1):
            pairs[symbols[i],symbols[i+1]] += freq
    return pairs

def merge_vocab(pair, v_in):
    v_out = {}
    bigram = re.escape(' '.join(pair))
    p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
    for word in v_in:
        w_out = p.sub(''.join(pair), word)
        v_out[w_out] = v_in[word]
    return v_out

vocab = {'l o w </w>' : 5, 'l o w e r </w>' : 2,
'n e w e s t </w>':6, 'w i d e s t </w>':3}

fp = open(sys.argv[1])
vocab = {}
for line in fp:
    line = line.strip().decode('utf-8')
    w,num = line.split('\t')
    cs = [c for c in w]
    #cs.append('</w>')
    w = ' '.join(cs)
    vocab[w] = long(num)
fp.close()

num_merges = 500000

def get_max(pairs):
    mk, mv = None, None
    for k,v in pairs.items():
        if not mk or v > mv:
            mk, mv = k, v
    return (mk, mv)

for i in range(num_merges):
    pairs = get_stats(vocab)
    if not pairs:
        break;
    st = time.time()
    res = get_max(pairs)
    print time.time() - st, len(pairs)
    #print res[0][0], res[0][1], res[1]
    best = max(pairs, key=pairs.get)
    print best[0].encode('utf-8'), best[1].encode('utf-8')
    vocab = merge_vocab(best, vocab)
