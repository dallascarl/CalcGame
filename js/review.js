/* CalcGame review mode: the instructor taps "Note", taps the thing that needs fixing, picks tags and types
   (or dictates) a note. Each note is saved with where it was left (world, stop, lesson step or question,
   the tapped text and the screen text) so the fixes can be made later without guessing.
   Loaded only by the review copy. Notes go to the page's shared store ("notes"), or this device if there is none. */
(function(){
  const TAGS=['Wrong answer key','Confusing wording','Too hard','Too easy','Looks broken'];
  let db=null,notes=[],picking=false,target=null,pin=null,sel=new Set();
  const css=`
  .rv-fab{position:fixed;right:calc(12px + env(safe-area-inset-right,0px));bottom:calc(84px + env(safe-area-inset-bottom,0px));z-index:40;
    display:flex;align-items:center;gap:6px;border:0;border-radius:999px;padding:10px 16px;background:var(--gold);color:#1b1404;
    font:800 15px var(--display);box-shadow:0 4px 14px rgba(0,0,0,.25)}
  .rv-fab b{background:#1b1404;color:var(--gold);border-radius:999px;padding:0 7px;font-size:12px}
  .rv-ribbon{position:fixed;left:0;right:0;top:0;z-index:39;height:3px;background:var(--gold);pointer-events:none}
  .rv-pick{position:fixed;inset:0;z-index:50;cursor:crosshair;background:rgba(201,138,11,.08)}
  .rv-pick p{position:absolute;left:12px;right:12px;top:calc(10px + env(safe-area-inset-top,0px));margin:0;padding:10px 12px;border-radius:12px;
    background:var(--ink);color:var(--paper);font:700 14px var(--body);display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap}
  .rv-pick button{border:1.5px solid var(--paper);background:transparent;color:var(--paper);border-radius:8px;padding:4px 10px;font:700 13px var(--body)}
  .rv-pin{position:fixed;z-index:51;width:26px;height:26px;margin:-26px 0 0 -13px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);
    background:var(--gold);border:2px solid #1b1404;pointer-events:none}
  .rv-hl{outline:3px solid var(--gold)!important;outline-offset:2px}
  .rv-sheet{position:fixed;left:0;right:0;bottom:0;z-index:52;max-height:82%;overflow:auto;background:var(--card);color:var(--ink);
    border-top:2px solid var(--gold);border-radius:16px 16px 0 0;box-shadow:0 -8px 24px rgba(0,0,0,.25);
    padding:14px max(16px,env(safe-area-inset-right,0px)) calc(14px + env(safe-area-inset-bottom,0px)) max(16px,env(safe-area-inset-left,0px));
    display:flex;flex-direction:column;gap:10px;max-width:30rem;margin-inline:auto}
  .rv-sheet h3{margin:0;font:800 18px var(--display);display:flex;justify-content:space-between;align-items:center;gap:8px}
  .rv-sheet .rv-where{font-size:12px;color:var(--muted)}
  .rv-sheet .rv-what{font-size:13px;background:var(--paper);border-radius:8px;padding:6px 8px;overflow-wrap:anywhere}
  .rv-tags{display:flex;flex-wrap:wrap;gap:6px}
  .rv-tags button{border:1.5px solid var(--rule);background:var(--paper);color:var(--ink);border-radius:999px;padding:6px 10px;font:600 13px var(--body)}
  .rv-tags button[aria-pressed="true"]{background:var(--gold);border-color:var(--gold);color:#1b1404}
  .rv-sheet textarea{width:100%;min-height:96px;resize:vertical;border:1.5px solid var(--rule);border-radius:10px;padding:8px;font:16px var(--body);background:var(--paper);color:var(--ink)}
  .rv-row{display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap}
  .rv-row button,.rv-sheet h3 button{border:1.5px solid var(--ink);background:var(--paper);color:var(--ink);border-radius:10px;padding:8px 14px;font:700 14px var(--body)}
  .rv-row .rv-save{background:var(--ink);color:var(--paper)}
  .rv-list{display:flex;flex-direction:column;gap:8px;margin:0;padding:0;list-style:none}
  .rv-list li{border:1.5px solid var(--rule);border-radius:10px;padding:8px 10px;display:flex;flex-direction:column;gap:3px;font-size:14px}
  .rv-list li.done{opacity:.55}
  .rv-list .rv-meta{font-size:12px;color:var(--muted);display:flex;justify-content:space-between;gap:8px}
  .rv-list .rv-del{border:0;background:none;color:var(--bad);font:700 12px var(--body);padding:0}
  .rv-warn{font-size:12px;color:var(--bad)}`;
  const st=document.createElement('style');st.textContent=css;document.head.appendChild(st);
  const ribbon=document.createElement('div');ribbon.className='rv-ribbon';document.body.appendChild(ribbon);
  const fab=document.createElement('button');fab.className='rv-fab';fab.setAttribute('aria-label','Leave a review note');document.body.appendChild(fab);
  const e=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const here=()=>{try{return Object.assign({},typeof CUR!=='undefined'&&CUR||{})}catch(x){return {};}};
  const hereKey=()=>{const c=here();return (c.deck||'map')+'|'+(c.qid||c.where||'');};
  const drawFab=()=>{const k=hereKey(),n=notes.filter(x=>x.key===k&&x.status!=='done').length;fab.innerHTML='✎ Note'+(n?' <b>'+n+'</b>':'');};

  /* ---- storage ---- */
  const LS='calcgame.review.notes';
  const local=()=>{try{return JSON.parse(localStorage.getItem(LS)||'[]');}catch(x){return [];}};
  async function boot(){
    try{db=window.claude&&await window.claude.use('db');}catch(x){db=null;}
    if(db){db.collection('notes').orderBy('at','desc').onSnapshot(s=>{notes=s.docs.map(d=>Object.assign({id:d.id},d.data()));drawFab();if(listOpen)showList();},()=>{});}
    else{notes=local();drawFab();}
  }
  async function saveNote(n){
    if(db){await db.collection('notes').add(n);return;}
    notes=[Object.assign({id:'L'+Date.now()},n),...notes];try{localStorage.setItem(LS,JSON.stringify(notes));}catch(x){}
  }
  async function delNote(id){
    if(db){await db.doc('notes/'+id).delete();return;}
    notes=notes.filter(x=>x.id!==id);try{localStorage.setItem(LS,JSON.stringify(notes));}catch(x){} showList();drawFab();
  }

  /* ---- pick the spot ---- */
  let overlay=null,sheet=null,listOpen=false;
  const clearMarks=()=>{document.querySelectorAll('.rv-hl').forEach(x=>x.classList.remove('rv-hl'));if(pin){pin.remove();pin=null;}};
  function startPick(){
    if(picking)return; picking=true; clearMarks(); target=null;
    overlay=document.createElement('div');overlay.className='rv-pick';
    overlay.innerHTML='<p><span>Tap the thing that needs fixing</span><span><button data-a="whole">Whole screen</button> <button data-a="cancel">Cancel</button></span></p>';
    document.body.appendChild(overlay);
    overlay.addEventListener('click',ev=>{
      const a=ev.target.closest('button');
      if(a){picking=false;overlay.remove();if(a.dataset.a==='whole')openSheet(null,null);return;}
      const els=document.elementsFromPoint(ev.clientX,ev.clientY).filter(x=>!x.closest('.rv-pick,.rv-fab,.rv-sheet,.rv-ribbon'));
      const el=els.find(x=>x!==document.body&&x!==document.documentElement&&x.id!=='app')||null;
      picking=false;overlay.remove();
      pin=document.createElement('div');pin.className='rv-pin';pin.style.left=ev.clientX+'px';pin.style.top=ev.clientY+'px';document.body.appendChild(pin);
      openSheet(el,{x:Math.round(100*ev.clientX/innerWidth),y:Math.round(100*ev.clientY/innerHeight)});
    });
  }
  function describe(el){
    if(!el)return null;
    const box=el.closest('.opt,.key,.chip,.blank,.ans,.step,.act,.node,.gwrap,.fb,button,p,h2,li,svg,article')||el;
    box.classList.add('rv-hl');
    const step=el.closest('.step'),steps=[...document.querySelectorAll('.steps .step')];
    return {kind:box.tagName.toLowerCase()+(box.className&&typeof box.className==='string'?'.'+box.className.split(' ').filter(c=>c&&c!=='rv-hl').join('.'):''),
      text:(box.innerText||box.textContent||'').trim().replace(/\s+/g,' ').slice(0,200),
      part:step?steps.indexOf(step)+1:null,option:box.dataset&&(box.dataset.i||box.dataset.k||box.dataset.n||null)};
  }

  /* ---- the note sheet ---- */
  function openSheet(el,pos){
    if(sheet)sheet.remove(); sel=new Set(); listOpen=false;
    const c=here(),t=describe(el);
    target={t,pos};
    sheet=document.createElement('div');sheet.className='rv-sheet';sheet.setAttribute('role','dialog');sheet.setAttribute('aria-label','Review note');
    sheet.innerHTML='<h3><span>Note</span><button data-a="list">My notes ('+notes.filter(x=>x.status!=='done').length+')</button></h3>'+
      '<div class="rv-where">'+e(c.where||'this screen')+(t&&t.part?' · part '+t.part:'')+'</div>'+
      (t?'<div class="rv-what">You picked: '+e(t.text||t.kind)+'</div>':'<div class="rv-what">The whole screen</div>')+
      '<div class="rv-tags">'+TAGS.map(g=>'<button aria-pressed="false" data-t="'+e(g)+'">'+e(g)+'</button>').join('')+'</div>'+
      '<textarea id="rv-text" placeholder="What should change? Type, or tap the 🎤 on your keyboard and talk."></textarea>'+
      (db?'':'<div class="rv-warn">Notes are saving on this device only. Open the review copy in Claude to share them.</div>')+
      '<div class="rv-row"><button data-a="cancel">Cancel</button><button class="rv-save" data-a="save">Save note</button></div>';
    document.body.appendChild(sheet);
    sheet.addEventListener('click',onSheet);sheet.addEventListener('keydown',ev=>ev.stopPropagation());
    setTimeout(()=>{const ta=sheet.querySelector('#rv-text');if(ta)ta.focus();},50);
  }
  async function onSheet(ev){
    const b=ev.target.closest('button');if(!b)return;
    if(b.dataset.t){const g=b.dataset.t;sel.has(g)?sel.delete(g):sel.add(g);b.setAttribute('aria-pressed',sel.has(g));return;}
    if(b.dataset.del){b.disabled=true;await delNote(b.dataset.del);return;}
    const a=b.dataset.a;
    if(a==='cancel'||a==='close'){sheet.remove();sheet=null;listOpen=false;clearMarks();return;}
    if(a==='list'){showList();return;}
    if(a==='new'){sheet.remove();sheet=null;listOpen=false;startPick();return;}
    if(a==='save'){
      const txt=sheet.querySelector('#rv-text').value.trim();
      if(!txt&&!sel.size){sheet.querySelector('#rv-text').placeholder='Add a tag or a few words first.';return;}
      const c=here(),body=document.querySelector('#app .body');
      const n={at:new Date().toISOString(),status:'open',tags:[...sel],note:txt,key:hereKey(),
        where:c.where||'',deck:c.deck||'',qid:c.qid||'',area:(typeof AREA!=='undefined'?AREA:''),questionText:c.text||'',
        world:(typeof MAP!=='undefined'&&MAP?MAP.id:''),target:target&&target.t,pos:target&&target.pos,
        screen:body?body.innerText.replace(/\s+/g,' ').trim().slice(0,800):'',
        view:innerWidth+'x'+innerHeight+(matchMedia('(prefers-color-scheme: dark)').matches?' dark':' light')};
      b.disabled=true;b.textContent='Saving…';
      try{await saveNote(n);sheet.remove();sheet=null;clearMarks();drawFab();if(typeof toast==='function')toast('Note saved');}
      catch(x){b.disabled=false;b.textContent='Save note';const w=document.createElement('div');w.className='rv-warn';
        w.textContent=x&&x.code==='quota_exceeded'?'The notes store is full. Ask Claude to clear finished notes.':'That did not save ('+(x&&x.code||'error')+'). Try again.';sheet.querySelector('.rv-row').before(w);}
    }
  }
  function showList(){
    if(!sheet){sheet=document.createElement('div');sheet.className='rv-sheet';document.body.appendChild(sheet);sheet.addEventListener('click',onSheet);sheet.addEventListener('keydown',ev=>ev.stopPropagation());}
    listOpen=true; clearMarks();
    const open=notes.filter(x=>x.status!=='done').length;
    sheet.innerHTML='<h3><span>My notes · '+open+' open</span><button data-a="close">Close</button></h3>'+
      (notes.length?'<ul class="rv-list">'+notes.map(n=>'<li class="'+(n.status==='done'?'done':'')+'"><div class="rv-meta"><span>'+e(n.where||n.deck)+'</span><span>'+
        (n.status==='done'?'fixed ✓':'<button class="rv-del" data-del="'+e(n.id)+'">Delete</button>')+'</span></div>'+
        (n.tags&&n.tags.length?'<div><b>'+e(n.tags.join(' · '))+'</b></div>':'')+(n.note?'<div>'+e(n.note)+'</div>':'')+
        (n.status==='done'&&n.reply?'<div class="rv-where">Fix: '+e(n.reply)+'</div>':'')+'</li>').join('')+'</ul>'
        :'<p class="rv-where">No notes yet. Tap ✎ Note on any screen.</p>')+
      '<div class="rv-row"><button class="rv-save" data-a="new">New note</button></div>';
  }
  fab.addEventListener('click',()=>{if(sheet){sheet.remove();sheet=null;clearMarks();}startPick();});
  /* keep the button's count in step with the screen the app is showing */
  new MutationObserver(()=>drawFab()).observe(document.getElementById('app'),{childList:true});
  drawFab(); boot();
})();
