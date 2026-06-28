"""Shared config: technique colour families and inline keyword phrases.
Edit KEYWORDS here to change the italic trigger phrases under each pill."""

FAMILY = {
  'graph':   ('#E1F5EE', '#1D9E75', '#085041'),
  'search':  ('#EEEDFE', '#7F77DD', '#3C3489'),
  'pointer': ('#E6F1FB', '#378ADD', '#0C447C'),
  'heap':    ('#FBEAF0', '#D4537E', '#72243E'),
  'dp':      ('#FAEEDA', '#EF9F27', '#633806'),
  'exhaust': ('#FAECE7', '#D85A30', '#712B13'),
  'stack':   ('#EAF3DE', '#97C459', '#27500A'),
  'other':   ('#F1EFE8', '#B4B2A9', '#2C2C2A'),
}

def fam(tech):
    t = tech.lower()
    if any(k in t for k in ['bfs','dfs','topolog','dijkstra','disjoint']): return 'graph'
    if any(k in t for k in ['binary search','ordered set','fenwick','segment tree']): return 'search'
    if any(k in t for k in ['two pointer','sliding window','partition']): return 'pointer'
    if any(k in t for k in ['heap','sorting','interval']): return 'heap'
    if 'bitmask' in t or 'dynamic programming' in t or 'divide and conquer' in t or 'memo' in t: return 'dp'
    if 'backtrack' in t or 'brute' in t: return 'exhaust'
    if 'stack' in t: return 'stack'
    return 'other'

# Short, real problem-statement trigger phrases shown under each pill (≤ ~38 chars).
KEYWORDS = {
  'BFS': 'shortest unweighted path · level order',
  'Binary Search': 'sorted array · "minimize the max"',
  'Bitmask DP': 'n ≤ 20 · "visit all" · subset state',
  'Brute Force / Backtracking': 'all permutations / subsets · n ≤ 12',
  'DFS': 'tree paths · explore all branches',
  'DFS / Backtracking': 'enumerate paths · small graph',
  'Design + Supporting Structures': '"implement LRU / iterator"',
  "Dijkstra's Algorithm": 'shortest path · weighted edges',
  'Disjoint Set Union': 'connected components · "merge accounts"',
  'Divide & Conquer / Tree DP': 'count distinct trees · subtree DP',
  'Dynamic Programming': '"number of ways" · max/min with choices',
  'Greedy Algorithms': 'intervals · "jump game" · local choice',
  'Hash Table / Counting': 'frequency · "first unique" · group by',
  'Heap / Divide & Conquer': 'merge k sorted lists',
  'Heap / Sorting': 'kth largest · "top k" · running median',
  'Linked-List Manipulation': 'reverse / reorder a list',
  'Math / Bit Manipulation': 'XOR tricks · powers · "single number"',
  'Monotonic Stack': 'next greater · "daily temperatures"',
  'Number Theory': 'gcd / primes / modular arithmetic',
  'Ordered Set / Fenwick / Segment Tree': 'range sum + updates · order stats',
  'Prefix Sums': 'subarray sum = k · cumulative totals',
  'Simulation / Basic DSA': 'follow the rules step by step',
  'Sliding Window': 'longest/shortest substring · ≤ k distinct',
  'Sorting + Interval Scan': 'merge intervals · "meeting rooms"',
  'Specialized / Advanced Pattern': 'rare / problem-specific trick',
  'Stack': 'valid parentheses · expression parse',
  'Topological Sort': '"course schedule" · prerequisites · DAG',
  'Trie / DP / Memoization': 'word break · dictionary split',
  'Trie / String Matching / Rolling Hash': 'prefix search · "starts with"',
  'Two pointers': 'pair from ends · fast/slow · in-place',
  'Two pointers / Partitioning': 'move zeroes · Dutch flag · in-place',
}
