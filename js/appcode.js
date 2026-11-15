/* App codes. Students keep their progress in their own browser only (no server; UVU rules), so the app
   turns that progress into one short code. The code is CUMULATIVE: it holds every stop the student has
   finished and their Match Board points, so the same code does two jobs:
     - the student pastes it into the pre-class quiz on Canvas, and the instructor decodes it (codes.html);
     - if the browser ever loses its data, entering the latest code restores everything up to that point.

   Layout of a version 1 code, 140 bits = 28 characters, shown as 7 groups of 4:
     version 3 bits | student number 14 bits (0000-9999) | points ÷ 10, 15 bits | stops 88 bits | check 20 bits
   Stop k is bit k of the stop field, in the order of stops.json (append-only).
   The check is a keyed hash of everything before it. The whole thing is then run through a 6-round Feistel
   network, so changing one stop changes the whole code and the layout is not visible from outside.
   This is scrambling, not security: the key is in this file. It stops casual sharing, since a code only
   counts for the student number inside it; it does not stop someone who reads the source.

   Loaded by index.html (before app.js) and by codes.html. The functions at the bottom (welcome, panel)
   use the game's globals and only run inside the game. */
const APPCODE=(()=>{
  const ALPH='0123456789ABCDEFGHJKMNPQRSTVWXYZ';            /* Crockford base 32: no I, L, O or U */
  const W={ver:3,sid:14,pts:15,stops:88,chk:20},NB=140,LEN=28,VER=1,ROUNDS=6;
  const KEY='calcgame|e902d6d64ca33f943ea2cc7d';
  let REG=[];

  function h32(str,seed){                                     /* a fast 32-bit string hash (cyrb53, folded) */
    let a=0xdeadbeef^seed,b=0x41c6ce57^seed;
    for(let i=0;i<str.length;i++){const c=str.charCodeAt(i);a=Math.imul(a^c,2654435761);b=Math.imul(b^c,1597334677);}
    a=Math.imul(a^(a>>>16),2246822507)^Math.imul(b^(b>>>13),3266489909);
    b=Math.imul(b^(b>>>16),2246822507)^Math.imul(a^(a>>>13),3266489909);
    return (a^(b>>>3))>>>0;
  }
  function bitsFrom(seed,n){                                  /* n pseudo-random bits from a 32-bit seed (xorshift32) */
    let x=seed||0x9e3779b9; const out=[];
    while(out.length<n){x^=x<<13;x^=x>>>17;x^=x<<5;x>>>=0;for(let k=0;k<32&&out.length<n;k++)out.push((x>>>k)&1);}
    return out;
  }
  const F=(half,r)=>bitsFrom(h32(KEY+'|'+r+'|'+half.join(''),r+1),half.length);
  const xor=(a,b)=>a.map((v,i)=>v^b[i]);
  function scramble(bits){let L=bits.slice(0,NB/2),R=bits.slice(NB/2);for(let r=0;r<ROUNDS;r++){const t=xor(L,F(R,r));L=R;R=t;}return L.concat(R);}
  function unscramble(bits){let L=bits.slice(0,NB/2),R=bits.slice(NB/2);for(let r=ROUNDS-1;r>=0;r--){const t=xor(R,F(L,r));R=L;L=t;}return L.concat(R);}
  const put=(out,v,w)=>{for(let k=w-1;k>=0;k--)out.push(Math.floor(v/2**k)%2);};
  const take=(b,i,w)=>{let v=0;for(let k=0;k<w;k++)v=v*2+b[i+k];return v;};
  const check=bits=>h32(KEY+'|chk|'+bits.join(''),7)%(2**W.chk);

  /* the stop keys ("world:node") in code order */
  function setRegistry(list){REG=Array.isArray(list)?list.slice(0,W.stops):[];}
  const registry=()=>REG.slice();

  /* {sid: 0-9999, points, done: ['toolkit:notation', ...]} -> "K7Q2-M9XP-..." */
  function encode(o){
    const sid=Math.max(0,Math.min(9999,Math.floor(+o.sid||0))),pts=Math.max(0,Math.min(2**W.pts-1,Math.floor((+o.points||0)/10)));
    const want=new Set(o.done||[]),b=[];
    put(b,VER,W.ver);put(b,sid,W.sid);put(b,pts,W.pts);
    for(let k=0;k<W.stops;k++)b.push(k<REG.length&&want.has(REG[k])?1:0);
    put(b,check(b),W.chk);
    const s=scramble(b);let str='';
    for(let i=0;i<NB;i+=5)str+=ALPH[take(s,i,5)];
    return str.match(/.{4}/g).join('-');
  }
  /* tidy what a student typed: case, separators, and the letters people confuse with digits */
  const clean=s=>String(s||'').toUpperCase().replace(/[^0-9A-Z]/g,'').replace(/O/g,'0').replace(/[IL]/g,'1').replace(/U/g,'V');
  /* -> {ok:true, sid, sidText, points, done:[keys], stops:[indexes]} or {ok:false, why} */
  function decode(str){
    const c=clean(str);
    if(c.length!==LEN)return {ok:false,why:'An app code has 28 letters and numbers; this one has '+c.length+'.'};
    const s=[];for(const ch of c)put(s,ALPH.indexOf(ch),5);
    const b=unscramble(s),body=b.slice(0,NB-W.chk);
    if(take(b,NB-W.chk,W.chk)!==check(body))return {ok:false,why:'That code does not check out. Look for a typo.'};
    let i=0;const ver=take(b,i,W.ver);i+=W.ver;
    if(ver!==VER)return {ok:false,why:'That code is from a different version of the app.'};
    const sid=take(b,i,W.sid);i+=W.sid;const points=10*take(b,i,W.pts);i+=W.pts;
    const stops=[],done=[];for(let k=0;k<W.stops;k++)if(b[i+k]){stops.push(k);if(k<REG.length)done.push(REG[k]);}
    if(sid>9999)return {ok:false,why:'That code does not check out.'};
    return {ok:true,sid,sidText:String(sid).padStart(4,'0'),points,done,stops,canon:c.match(/.{4}/g).join('-')};
  }
  /* finds every code-shaped string in pasted text (a Canvas export, an email, a list) */
  function find(text){return (String(text||'').match(/[0-9A-Za-z]{4}(?:[- ]?[0-9A-Za-z]{4}){6}(?![0-9A-Za-z])/g)||[]);}

  return {encode,decode,find,clean,setRegistry,registry,LEN,MAXSTOPS:W.stops};
})();

/* ===================================================================== in the game */
/* the stops this browser has finished, as registry keys */
APPCODE.doneKeys=function(){
  const out=[];
  for(const w of WORLDS)for(const n of w.nodes)if(n.deck&&DECKS[n.deck]&&deckCleared(DECKS[n.deck]))out.push(w.id+':'+n.id);
  return out;
};
APPCODE.mine=function(){return S.sid==null?'':APPCODE.encode({sid:S.sid,points:S.points,done:APPCODE.doneKeys()});};
APPCODE.total=()=>APPCODE.registry().filter(k=>{const [w,n]=k.split(':');const W=WORLDS.find(x=>x.id===w);return W&&W.nodes.some(x=>x.id===n&&x.deck);}).length;

/* put a decoded code's progress into this browser. Never takes anything away. */
APPCODE.restore=function(r){
  let n=0;
  for(const key of r.done){
    const [wid,nid]=key.split(':'),w=WORLDS.find(x=>x.id===wid),node=w&&w.nodes.find(x=>x.id===nid),d=node&&DECKS[node.deck];
    if(!d||d.error)continue;
    if(!deckCleared(d))n++;
    const p=ds(d.id);p.v2=true;p.pass=p.pass||{};
    drillKinds(d).forEach(k=>{p.pass[k]=true;});
    lessonsOf(d).forEach(l=>{lp(d,l.id).done=true;});
  }
  S.points=Math.max(S.points||0,r.points);
  if(S.sid==null)S.sid=r.sid;
  save();
  return n;
};
const sidOk=v=>/^\d{4}$/.test(String(v).trim());

/* the restore form, used on the welcome screen and in the code panel */
function restoreForm(){
  return '<label class="fld" for="ac-in"><span>Your latest app code</span><input id="ac-in" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX"></label>'+
    '<div class="row"><button class="btn" id="ac-rs">Restore</button></div><div class="fb" id="ac-fb" hidden></div>';
}
function wireRestore(m,after){
  const fb=$('#ac-fb',m),say=(ok,t)=>{fb.hidden=false;fb.className='fb '+(ok?'good':'bad');fb.innerHTML='<span>'+fmt(t)+'</span>';};
  $('#ac-rs',m).onclick=()=>{
    const r=APPCODE.decode($('#ac-in',m).value);
    if(!r.ok)return say(false,r.why);
    if(S.sid!=null&&S.sid!==r.sid)return say(false,'That code belongs to student number **'+r.sidText+'**, but this app is set to **'+String(S.sid).padStart(4,'0')+'**. If '+r.sidText+' is yours, change your number first.');
    const n=APPCODE.restore(r);
    say(true,n?'Restored: '+n+(n===1?' stop':' stops')+' marked finished, and '+r.points+' game points.':'Nothing to restore: this browser already has everything in that code.');
    if(after)setTimeout(after,n?1400:2200);
  };
}

/* first launch: ask for the student number (or restore from a code) */
APPCODE.welcome=function(){
  if(typeof BACK!=='undefined'&&BACK)return Promise.resolve();
  if(S.sid!=null||S.preview||isInstructor())return Promise.resolve();
  return new Promise(res=>{
    const done=()=>{closeModal();res();};
    modal('<h2>Welcome to CalcGame</h2><p class="txt">Enter the 4-digit student number your instructor gave you. It goes into your app code, so the work you do here counts for you.</p>'+
      '<label class="fld" for="ac-sid"><span>Student number</span><input id="ac-sid" inputmode="numeric" maxlength="4" autocomplete="off" placeholder="0000"></label>'+
      '<div class="row"><button class="btn" id="ac-go">Start</button><button class="btn ghost" id="ac-later">Not now</button></div><div class="fb bad" id="ac-err" hidden></div>'+
      '<details class="ac-more"><summary>Already played on another phone or computer?</summary><p class="tiny">Enter the latest app code you pasted into Canvas. Everything in it comes back here.</p>'+restoreForm()+'</details>'+
      '<p class="tiny">Your progress stays in this browser. Nothing is sent anywhere.</p>',m=>{
      $('#ac-go',m).onclick=()=>{const v=$('#ac-sid',m).value.trim();
        if(!sidOk(v)){const e=$('#ac-err',m);e.hidden=false;e.innerHTML='<span>A student number is exactly 4 digits.</span>';return;}
        S.sid=+v;save();done();};
      $('#ac-sid',m).onkeydown=e=>{if(e.key==='Enter')$('#ac-go',m).click();};
      $('#ac-later',m).onclick=done;
      wireRestore(m,done);
    });
    const mm=$('.modal');if(mm)mm.addEventListener('click',e=>{if(!document.body.contains(mm)||!$('.modal'))res();});
  });
};

/* the App code panel: the code, Copy, change number, restore */
APPCODE.panel=function(){
  const sidForm=(v)=>'<label class="fld" for="ac-sid"><span>Student number (4 digits, from your instructor)</span><input id="ac-sid" inputmode="numeric" maxlength="4" autocomplete="off" value="'+(v==null?'':String(v).padStart(4,'0'))+'"></label>'+
    '<div class="row"><button class="btn" id="ac-save">Save</button></div><div class="fb bad" id="ac-err" hidden></div>';
  const draw=(editing)=>{
    const has=S.sid!=null,code=has?APPCODE.mine():'',nd=APPCODE.doneKeys().length,tot=APPCODE.total();
    modal('<h2>Your app code</h2>'+
      (has&&!editing?
        '<p class="tiny">Student number <b>'+String(S.sid).padStart(4,'0')+'</b> · <button class="link" id="ac-chg">change</button></p>'+
        '<div class="acode" id="ac-code" tabindex="0" aria-label="App code">'+code.split('-').map(g=>'<span>'+g+'</span>').join('')+'</div>'+
        '<div class="row"><button class="btn" id="ac-copy">Copy code</button></div>'+
        '<p class="txt">It holds the <b>'+nd+' of '+tot+'</b> stops you have finished and your <b>'+(S.points||0)+'</b> game points. Paste it into the pre-class quiz.</p>'+
        '<p class="tiny">It is also your backup. If this browser ever loses your progress, enter your latest code below and everything comes back.</p>'
       :'<p class="txt">'+(has?'Change':'Enter')+' the 4-digit student number your instructor gave you. Your code is made from it.</p>'+sidForm(S.sid))+
      (S.preview?'<p class="banner">Preview mode is on: practice in preview is not recorded, so it is not in the code.</p>':'')+
      '<details class="ac-more"'+(has?'':' open')+'><summary>Restore from a code</summary>'+restoreForm()+'</details>'+
      '<div class="row"><button class="btn ghost" data-close>Close</button></div>',m=>{
      const c=$('#ac-copy',m);
      if(c)c.onclick=async()=>{try{await navigator.clipboard.writeText(code);c.textContent='Copied ✓';}
        catch(e){const r=document.createRange();r.selectNodeContents($('#ac-code',m));const s=getSelection();s.removeAllRanges();s.addRange(r);c.textContent='Selected: copy it now';}};
      const ch=$('#ac-chg',m);if(ch)ch.onclick=()=>draw(true);
      const sv=$('#ac-save',m);
      if(sv)sv.onclick=()=>{const v=$('#ac-sid',m).value.trim();
        if(!sidOk(v)){const e=$('#ac-err',m);e.hidden=false;e.innerHTML='<span>A student number is exactly 4 digits.</span>';return;}
        S.sid=+v;save();draw(false);if(typeof home==='function'&&$('.hud'))home();};
      wireRestore(m,()=>{closeModal();home();});
    });
  };
  draw(false);
};
document.addEventListener('click',e=>{if(e.target.closest('[data-appcode]'))APPCODE.panel();});
