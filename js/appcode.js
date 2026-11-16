/* App codes. Students keep their progress in their own browser only (no server; UVU rules), so the app
   turns that progress into one short code. The code is CUMULATIVE: for every stop it holds whether the
   student has done nothing, done the before-class work (lessons and theory), or cleared it; plus their
   Match Board points. So the same code does two jobs:
     - the student pastes it into the pre-class quiz on Canvas, and the instructor decodes it (codes.html);
     - if the browser ever loses its data, entering the latest code restores everything up to that point.

   Layout of a version 2 code, 200 bits = 40 characters, shown as 8 groups of 5:
     version 3 | student number 14 (0000-9999) | points ÷ 10, 15 | stops 140 | check 28
   The stop field is one base-3 number: stop k (in stops.json order, append-only) is digit k,
   0 = not started, 1 = before-class work done, 2 = cleared. 3^88 < 2^140, so 88 stops fit.
   The check is a keyed hash of everything before it. The whole thing is then run through a 6-round Feistel
   network, so changing one stop changes the whole code and the layout is not visible from outside.
   This is scrambling, not security: the key is in this file. It stops casual sharing, since a code only
   counts for the student number inside it; it does not stop someone who reads the source.

   Loaded by index.html (before app.js) and by codes.html. The functions further down (welcome, panel)
   use the game's globals and only run inside the game. */
const APPCODE=(()=>{
  const ALPH='0123456789ABCDEFGHJKMNPQRSTVWXYZ';            /* Crockford base 32: no I, L, O or U */
  const W={ver:3,sid:14,pts:15,stops:140,chk:28},NB=200,LEN=40,GROUP=5,VER=2,ROUNDS=6,MAXSTOPS=88;
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
  const put=(out,v,w)=>{v=BigInt(v);for(let k=w-1;k>=0;k--)out.push(Number((v>>BigInt(k))&1n));};
  const take=(b,i,w)=>{let v=0n;for(let k=0;k<w;k++)v=v*2n+BigInt(b[i+k]);return v;};
  const check=bits=>(h32(KEY+'|chk|'+bits.join(''),7)>>>8)*16+(h32(KEY+'|chk2|'+bits.join(''),11)&15);   /* 24 + 4 = 28 bits */

  /* the stop keys ("world:node") in code order */
  function setRegistry(list){REG=Array.isArray(list)?list.slice(0,MAXSTOPS):[];}
  const registry=()=>REG.slice();

  /* {sid: 0-9999, points, state: {'toolkit:notation': 2, 'toolkit:domain': 1, ...}}
     (or done: [keys] for cleared stops and prep: [keys] for before-class work) -> "K7Q2M-9XP4D-..." */
  function encode(o){
    const sid=Math.max(0,Math.min(9999,Math.floor(+o.sid||0))),pts=Math.max(0,Math.min(2**W.pts-1,Math.floor((+o.points||0)/10)));
    const st=Object.assign({},...(o.prep||[]).map(k=>({[k]:1})),...(o.done||[]).map(k=>({[k]:2})),o.state||{});
    let V=0n;for(let k=REG.length-1;k>=0;k--)V=V*3n+BigInt(Math.max(0,Math.min(2,st[REG[k]]|0)));
    const b=[];put(b,VER,W.ver);put(b,sid,W.sid);put(b,pts,W.pts);put(b,V,W.stops);
    put(b,check(b),W.chk);
    const s=scramble(b);let str='';
    for(let i=0;i<NB;i+=5)str+=ALPH[Number(take(s,i,5))];
    return str.match(new RegExp('.{'+GROUP+'}','g')).join('-');
  }
  /* tidy what a student typed: case, separators, and the letters people confuse with digits */
  const clean=s=>String(s||'').toUpperCase().replace(/[^0-9A-Z]/g,'').replace(/O/g,'0').replace(/[IL]/g,'1').replace(/U/g,'V');
  /* -> {ok:true, sid, sidText, points, state:{key: 1|2}, done:[cleared keys], prep:[before-class-only keys]}
        or {ok:false, why} */
  function decode(str){
    const c=clean(str);
    if(c.length!==LEN)return {ok:false,why:'An app code has '+LEN+' letters and numbers; this one has '+c.length+'.'};
    const s=[];for(const ch of c)put(s,ALPH.indexOf(ch),5);
    const b=unscramble(s),body=b.slice(0,NB-W.chk);
    if(Number(take(b,NB-W.chk,W.chk))!==check(body))return {ok:false,why:'That code does not check out. Look for a typo.'};
    let i=0;const ver=Number(take(b,i,W.ver));i+=W.ver;
    if(ver!==VER)return {ok:false,why:'That code is from a different version of the app.'};
    const sid=Number(take(b,i,W.sid));i+=W.sid;const points=10*Number(take(b,i,W.pts));i+=W.pts;
    let V=take(b,i,W.stops);
    if(sid>9999||V>=3n**BigInt(MAXSTOPS))return {ok:false,why:'That code does not check out.'};
    const state={},done=[],prep=[];
    for(let k=0;k<MAXSTOPS;k++){const d=Number(V%3n);V/=3n;if(d&&k<REG.length){state[REG[k]]=d;(d===2?done:prep).push(REG[k]);}}
    return {ok:true,sid,sidText:String(sid).padStart(4,'0'),points,state,done,prep,canon:c.match(new RegExp('.{'+GROUP+'}','g')).join('-')};
  }
  /* finds every code-shaped string in pasted text (a Canvas export, an email, a list) */
  function find(text){return (String(text||'').match(/[0-9A-Za-z]{5}(?:[- ]?[0-9A-Za-z]{5}){7}(?![0-9A-Za-z])/g)||[]);}

  return {encode,decode,find,clean,setRegistry,registry,LEN,MAXSTOPS};
})();

/* ===================================================================== in the game */
/* the parts done before class; everything else (practice) is after class */
APPCODE.BEFORE=['theory'];
/* 0 = not started, 1 = before-class work done (every lesson and the theory set), 2 = cleared */
APPCODE.stateOf=function(d){
  if(deckCleared(d))return 2;
  const L=lessonsOf(d),B=drillKinds(d).filter(k=>APPCODE.BEFORE.includes(k));
  if(!L.length&&!B.length)return 0;
  return L.every(l=>lp(d,l.id).done)&&B.every(k=>drillPassed(d,k))?1:0;
};
APPCODE.states=function(){
  const out={};
  for(const w of WORLDS)for(const n of w.nodes){const d=n.deck&&DECKS[n.deck];if(d&&!d.error){const v=APPCODE.stateOf(d);if(v)out[w.id+':'+n.id]=v;}}
  return out;
};
APPCODE.doneKeys=function(){const s=APPCODE.states();return Object.keys(s).filter(k=>s[k]===2);};
APPCODE.mine=function(){return S.sid==null?'':APPCODE.encode({sid:S.sid,points:S.points,state:APPCODE.states()});};
APPCODE.total=()=>APPCODE.registry().filter(k=>{const [w,n]=k.split(':');const W=WORLDS.find(x=>x.id===w);return W&&W.nodes.some(x=>x.id===n&&x.deck);}).length;

/* put a decoded code's progress into this browser. Never takes anything away. */
APPCODE.restore=function(r){
  let n=0;
  for(const [key,v] of Object.entries(r.state)){
    const [wid,nid]=key.split(':'),w=WORLDS.find(x=>x.id===wid),node=w&&w.nodes.find(x=>x.id===nid),d=node&&DECKS[node.deck];
    if(!d||d.error||APPCODE.stateOf(d)>=v)continue;
    n++;
    const p=ds(d.id);p.v2=true;p.pass=p.pass||{};
    drillKinds(d).forEach(k=>{if(v===2||APPCODE.BEFORE.includes(k))p.pass[k]=true;});
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
  return '<label class="fld" for="ac-in"><span>Your latest app code</span><input id="ac-in" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"></label>'+
    '<div class="row"><button class="btn" id="ac-rs">Restore</button></div><div class="fb" id="ac-fb" hidden></div>';
}
function wireRestore(m,after){
  const fb=$('#ac-fb',m),say=(ok,t)=>{fb.hidden=false;fb.className='fb '+(ok?'good':'bad');fb.innerHTML='<span>'+fmt(t)+'</span>';};
  $('#ac-rs',m).onclick=()=>{
    const r=APPCODE.decode($('#ac-in',m).value);
    if(!r.ok)return say(false,r.why);
    if(S.sid!=null&&S.sid!==r.sid)return say(false,'That code belongs to student number **'+r.sidText+'**, but this app is set to **'+String(S.sid).padStart(4,'0')+'**. If '+r.sidText+' is yours, change your number first.');
    const n=APPCODE.restore(r);
    say(true,n?'Restored: progress on '+n+(n===1?' stop':' stops')+', and '+r.points+' game points.':'Nothing to restore: this browser already has everything in that code.');
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
    const has=S.sid!=null,code=has?APPCODE.mine():'',stt=APPCODE.states(),nd=Object.values(stt).filter(v=>v===2).length,np=Object.values(stt).filter(v=>v===1).length,tot=APPCODE.total();
    modal('<h2>Your app code</h2>'+
      (has&&!editing?
        '<p class="tiny">Student number <b>'+String(S.sid).padStart(4,'0')+'</b> · <button class="link" id="ac-chg">change</button></p>'+
        '<div class="acode" id="ac-code" tabindex="0" aria-label="App code">'+code.split('-').map(g=>'<span>'+g+'</span>').join('')+'</div>'+
        '<div class="row"><button class="btn" id="ac-copy">Copy code</button></div>'+
        '<p class="txt">It holds the <b>'+nd+' of '+tot+'</b> stops you have cleared'+(np?', <b>'+np+'</b> more with the before-class work done,':'')+' and your <b>'+(S.points||0)+'</b> game points. Paste it into the pre-class quiz.</p>'+
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
