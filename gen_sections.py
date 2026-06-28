"""
Load the editable YAML source (flowchart.yaml) and convert it into the
row-tuple format that build.py renders.

This is the ONLY source of truth now. Edit flowchart.yaml, not this file.

Row tuples produced (consumed by build.py):
  ('qn', question, [subrows])        nested question; Yes leads into subrows
  ('q',  question, technique)        Yes -> technique, No falls through
  ('q2', question, techYes, techNo)  Yes -> techYes, No -> techNo
  ('end', 'Otherwise', technique)    fall-through default
  ('note', text)                     plain note line
The YAML carries `when:` phrases; we copy them into KEYWORDS (config.py) at
load time so build.py shows them under each pill.
"""
import os, yaml
from config import FAMILY, fam, KEYWORDS

HERE = os.path.dirname(os.path.abspath(__file__))

def _load():
    with open(os.path.join(HERE, 'flowchart.yaml'), encoding='utf-8') as f:
        return yaml.safe_load(f)

def _fam_hint(title):
    t = title.lower()
    if 'graph' in t: return 'graph'
    if 'sorted' in t or 'search' in t: return 'search'
    if 'linked' in t: return 'pointer'
    if 'lookup' in t: return 'heap'
    if 'small' in t: return 'exhaust'
    if 'subarray' in t or 'window' in t: return 'pointer'
    if 'max' in t: return 'dp'
    if 'count' in t: return 'dp'
    return 'other'

def _tech(d):
    name = d['use']
    when = d.get('when', '') or ''
    if when:
        KEYWORDS[name] = when
    return name

def _step(node):
    if 'note' in node:
        return ('note', node['note'])
    if 'otherwise' in node:
        return ('end', 'Otherwise', _tech(node['otherwise']))
    if 'then' in node:
        return ('qn', node['ask'], [_step(s) for s in node['then']])
    q = node['ask']
    if 'if_no' in node:
        return ('q2', q, _tech(node['if_yes']), _tech(node['if_no']))
    return ('q', q, _tech(node['if_yes']))

def build_sections():
    doc = _load()
    out = []
    for sec in doc:
        title = sec['section']
        rows = [_step(s) for s in sec['steps']]
        out.append((title, _fam_hint(title), rows))
    return out

SECTIONS_GEN = build_sections()

if __name__ == '__main__':
    for title, band, rows in SECTIONS_GEN:
        print('##', title)
        def show(rows, d=0):
            for r in rows:
                if r[0]=='q':   print('  '*d, '?', r[1], '-> Yes:', r[2])
                elif r[0]=='q2':print('  '*d, '?', r[1], '-> Yes:', r[2], '| No:', r[3])
                elif r[0]=='qn':print('  '*d, '?', r[1], '[nested]'); show(r[2], d+1)
                elif r[0]=='end':print('  '*d, '=>', r[1], ':', r[2])
                elif r[0]=='note':print('  '*d, '#', r[1])
        show(rows)
        print()
