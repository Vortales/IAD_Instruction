"""Build a self-contained Russian IAD reference from the supplied DOCX.
Run: pip install -r tools/requirements.txt && python tools/build_memo.py
"""
from pathlib import Path
import json, re, hashlib
from docx import Document

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'Памятка/clean_Majestic РП Memphis.docx'
p = [x.text.strip() for x in Document(SOURCE).paragraphs]
# Exact source paragraph positions (zero based); original text is never paraphrased here.
selected = {
 3981: ('Устав LSPD', 'iad'), 5968: ('Охраняемые территории', 'related'),
 6083: ('ЭК', 'standards'), 6405: ('ТК', 'standards'),
 6699: ('ДК', 'road'), 7034: ('АК', 'admin'), 7423: ('ПК', 'process'),
 8681: ('УК', 'criminal'), 9759: ('Конституция', 'related'),
 10676: ('Закон об ОГП', 'related'), 12288: ('Закон об адвокатуре', 'related'),
 12474: ('Закон об ордерах', 'related'), 12876: ('Закон об ОРД', 'related'),
 13576: ('Государственная тайна', 'related'), 13705: ('Неприкосновенность', 'related'),
 13786: ('Оборот оружия', 'related'), 15524: ('Закон о РПО', 'related'),
 16026: ('Обращения в ОГП', 'related'), 16573: ('Разъяснения ОГП', 'related')
}
records=[]; sources=[]
for pos, (code, group) in selected.items():
 assert p[pos].startswith('https://forum.'), (pos, p[pos])
 end = next(i for i in range(pos+1,len(p)) if p[i] == '}')
 sources.append(dict(code=code, title=p[pos-1], url=p[pos], start=pos+1, end=end, group=group))
 starts=[i for i in range(pos+1,end) if re.match(r'^Статья\s+\d',p[i],re.I)]
 # Some appendices and explanations have no article headings. Keep their full text.
 if not starts: starts=[pos+1]
 elif starts[0]>pos+1: starts.insert(0,pos+1)
 for n,start in enumerate(starts):
  stop=starts[n+1] if n+1<len(starts) else end
  lines=[(i,t) for i,t in enumerate(p[start:stop],start) if t and t!='\u200b']
  # Chapter headings at the end belong to the next article, not to the current one.
  while lines and re.match(r'^(Глава|Раздел|Общая часть|Особенная часть)',lines[-1][1],re.I): lines.pop()
  if not lines: continue
  match=re.match(r'^Статья\s+(\d+(?:\.\d+)*)',p[start],re.I)
  number=match[1] if match else 'введение'
  # DOCX extraction has several split article numbers (e.g. ПК 41); preserve source text,
  # but join adjacent numeric heading fragments for navigation.
  if match and len(lines)>1:
   if re.fullmatch(r'\d',lines[1][1]): number+=lines[1][1]
   elif p[start].endswith('.') and re.match(r'^\d\s',lines[1][1]): number+='.'+lines[1][1][0]
  body='\n'.join(t for _,t in lines)
  desc=next((t.lstrip('. ').strip() for _,t in lines[1:] if len(t)>12 and not re.match(r'^(ч\.|Примечание|Исключение|Наказание|Глава|Раздел)',t)), lines[0][1])
  sanctions=[]
  for j,(_,t) in enumerate(lines):
   if t.startswith('Наказание'):
    s=t
    if len(t)<15 and j+1<len(lines): s+=' '+lines[j+1][1]
    sanctions.append(s)
  records.append(dict(id=f'r{len(records)}',code=code,group=group,num=number,title=desc,body=body,
    sanction=' | '.join(sanctions),url=p[pos],start=start+1,end=lines[-1][0]+1))

data=dict(records=records,sources=sources,sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 serverRules=dict(url=p[3238],body='\n'.join(p[3305:3316]+p[3420:3441]),
 label='Правила государственных организаций · п. 1.8, 1.20–1.21 · абзацы 3306–3316, 3421–3441 DOCX'))
template=(ROOT/'tools/memo_template.html').read_text()
content=json.dumps(data,ensure_ascii=False).replace('</','<\\/')
html=template.replace('/*__DATA__*/',content)
out=ROOT/'Памятка IAD — Marcus Nomad.html'
out.write_text(html)
print(f'{out.name}: {len(records)} records, {len(sources)} sources, {out.stat().st_size:,} bytes')
