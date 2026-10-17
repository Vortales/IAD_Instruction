// DOM-level offline interaction checks. Install: npm install --no-save jsdom
const fs = require('node:fs');
const assert = require('node:assert/strict');
const {JSDOM,VirtualConsole} = require('jsdom');
const errors=[]; const vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e));
const html=fs.readFileSync('Памятка IAD — Marcus Nomad.html','utf8');
const dom=new JSDOM(html,{runScripts:'dangerously',url:'file:///memo.html',virtualConsole:vc,beforeParse(w){w.scrollTo=()=>{};w.scrollBy=()=>{};w.HTMLElement.prototype.scrollIntoView=()=>{}}});
const w=dom.window,d=w.document;
assert.equal(d.querySelectorAll('.page:not(.hidden)')[0].id,'home');
for(const name of ['criminal','admin','road','process','standards','related','all']){
 w.show(name);assert.ok(d.querySelectorAll('#results details').length>0,name);
}
w.show('all');const total=d.querySelectorAll('#results details').length;assert.equal(total,849);
d.querySelector('#query').value='УК 15.1';w.render();assert.ok(d.querySelectorAll('#results details').length>0);
d.querySelector('#query').value='заведомонесуществующееслово';w.render();assert.equal(d.querySelectorAll('#results details').length,0);assert.ok(d.querySelector('.empty'));
w.resetSearch();assert.equal(d.querySelectorAll('#results details').length,total);
w.openRef('АК','11.1');assert.ok(d.querySelector('details[open]').textContent.includes('Оскорбление'));
w.openRef('ПК','41');assert.ok(d.querySelector('details[open]'));
w.expandResults(true);assert.equal(d.querySelectorAll('#results details[open]').length,d.querySelectorAll('#results details').length);
w.expandResults(false);assert.equal(d.querySelectorAll('#results details[open]').length,0);
// No broken editorial references: introduction links may fall back to the first article.
for(const e of d.querySelectorAll('[data-ref]')){
 const [code,num]=e.dataset.ref.split('|');
 const ok=w.eval(`DATA.records.some(r=>r.code===${JSON.stringify(code)} && (r.num===${JSON.stringify(num)} || ${JSON.stringify(num)}==='введение'))`);
 assert.ok(ok,`Broken reference ${code} ${num}`);
}
assert.equal(d.querySelectorAll('#checks input').length,11);
assert.equal(d.querySelectorAll('script[src],link[href],img[src],iframe').length,0,'No external resources');
assert.equal(errors.length,0,errors.map(e=>e.message).join('\n'));
console.log(`PASS: ${total} records, navigation, filters, empty search, exact references, expand/collapse, checklist, offline assets; no JS errors.`);
w.close();
