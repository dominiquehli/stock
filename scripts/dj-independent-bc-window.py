#!/usr/bin/env python3

import os
import random
import sys

# Global setup
NAME = 'dj'
COLUMN = {'DATE': 0, 'PERCENT': 8, 'USEFUL': [1, 2, 3, 4, 5]}

# Balanced Example Sets
BE = True
# Data Type
DT = 'independent-bc'
# Maximum Days
MD = [1, 3, 5]
if len(sys.argv) > 1:
    MD = [int(sys.argv[1])]
# Minimum Rise
MR = [1.0, 2.0]
if len(sys.argv) > 2:
    MR = [float(sys.argv[2])]
# Window Size
WS = [1, 5, 10, 20, 40, 80]
if len(sys.argv) > 3:
    WS = [int(sys.argv[3])]

print('Gathering %s data for M=%s R=%s ...' % (DT, MD, MR))

for D in MD:
    for R in MR:
        data = os.path.dirname(os.path.realpath(sys.argv[0])) + '/../data/'
        raw_path = data + 'raw/' + NAME + '-stock'
        csv_path = data + 'csv/' + NAME + '-stock/%s/day-%s-var-%s' % (DT, D, R)
        os.makedirs(csv_path, exist_ok=True)
        # Labels
        L = {}  # Name => Date => Label
        # Stocks
        S = {}  # Name => Date => Values
        for filename in sorted(os.listdir(raw_path)):
            if 'xxx' in filename:
                continue
            name = filename.split('.')[0]
            if name not in L:
                L[name] = {}
            if name not in S:
                S[name] = {}
            raw_file = raw_path + '/' + filename
            with open(raw_file, 'r') as rf:
                head = True
                for line in rf.readlines():
                    if head:
                        head = False
                        continue
                    columns = line.strip().split(',')
                    date = columns[COLUMN['DATE']]
                    label = 'C'
                    percent = float(columns[COLUMN['PERCENT']])
                    if percent > R:
                        label += 'P'  # + str(percent)
                    else:
                        label += 'N'  # str(percent)
                    L[name][date] = label
                    if date not in S[name]:
                        S[name][date] = []
                        for c in COLUMN['USEFUL']:
                            S[name][date].append(columns[c])
            rf.close()
        # Attributes
        A = {}
        for w in WS:
            A[w] = []
            for i in range(len(next(iter(next(iter(S.values())).values()))) * w):
                A[w].append('attr%d' % (i + 1))
            A[w].append('label')
        # Examples
        E = {}  # Window => Name => Label => [examples]
        for w in WS:
            E[w] = {}
            for name in L:
                E[w][name] = {}
                for date in L[name]:
                    if L[name][date] not in E[w][name]:
                        E[w][name][L[name][date]] = []
                stock_dates = list(sorted(S[name]))
                for i in range(len(stock_dates) - w - D):
                    date = stock_dates[i]
                    e = ','.join(S[name][date])
                    for j in range(1, w):
                        date = stock_dates[i + j]
                        e += ',' + ','.join(S[name][date])
                    label = 'CN'
                    for d in range(D):
                        date = stock_dates[i + w + d]
                        if L[name][date] == 'CP':
                            label = 'CP'
                            break
                    E[w][name][label].append(e)
        for w in E:
            for name in E[w]:
                window_file = csv_path + '/%s-%03d.csv' % (name, w)
                wf = open(window_file, 'w')
                wf.write('%s\n' % ','.join(A[w]))
                less = min(len(E[w][name]['CP']), len(E[w][name]['CN']))
                for label in sorted(E[w][name]):
                    if BE:
                        keys = []
                        while len(keys) < less:
                            key = random.randint(0, less - 1)
                            if key not in keys:
                                keys.append(key)
                        for key in keys:
                            wf.write('%s,%s\n' % (E[w][name][label][key], label))
                    else:
                        for example in E[w][name][label]:
                            wf.write('%s,%s\n' % (example, label))
                wf.close()

print(' done.')
