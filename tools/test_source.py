"""Verify reference coverage and verbatim article text against supplied DOCX."""
from pathlib import Path
import json, re
from docx import Document
root=Path(__file__).resolve().parents[1]
html=(root/'Памятка IAD — Marcus Nomad.html').read_text()
s=html.split('const DATA=',1)[1].split(';\nconst names=',1)[0]
data=json.loads(s.replace('<\\/','</'))
p=[x.text.strip() for x in Document(root/'Памятка/clean_Majestic РП Memphis.docx').paragraphs]
for r in data['records']:
 expected='\n'.join(x for x in p[r['start']-1:r['end']] if x and x!='\u200b')
 assert expected==r['body'],(r['code'],r['num'])
for source in data['sources']:
 starts={i+1 for i in range(source['start'],source['end']) if re.match(r'^Статья\s+\d',p[i],re.I)}
 actual={r['start'] for r in data['records'] if r['code']==source['code'] and r['num']!='введение'}
 assert starts==actual,(source['code'], starts-actual,actual-starts)
 print(source['code'],len(actual),'article headings covered')
assert len({r['id'] for r in data['records']})==len(data['records'])
assert not re.search(r'<(?:script|img|link)[^>]+(?:src|href)=',html,re.I)
print('PASS: all selected article headings covered, all article bodies verbatim, IDs unique, no external assets.')
