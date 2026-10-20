/* Accounts and everything that talks to the server: sign up / sign in, the character picker,
   syncing progress, logging answers and completions, the leaderboard, due dates, completion codes,
   "Send feedback" and "I don't understand". With no server configured, the app works exactly as before
   (progress stays in this browser) and these features are hidden.
   Privacy: no real names or emails are collected. Students pick a username. */

const ACCT={mode:'off',profile:null,due:{},codes:{},queue:[],stopsLogged:null};
let AREA='',CUR=null;   /* what the student is looking at, for "I don't understand" */
const WORDS=s=>(String(s).trim().match(/[A-Za-z0-9'’]+/g)||[]).length;
const plain=s=>String(s||'').replace(/\$|\*\*/g,'').replace(/frac\{([^{}]*)\}\{([^{}]*)\}/g,'($1)/($2)').replace(/lim\[([^\]]*)\]/g,'lim($1) ').replace(/\n/g,' ').slice(0,220);

/* ---------- small UI helpers ---------- */
function modal(html,onMount){
  closeModal();
  const m=document.createElement('div');m.className='modal';m.setAttribute('role','dialog');m.setAttribute('aria-modal','true');
  m.innerHTML='<div class="modal-c">'+html+'</div>';app.appendChild(m);
  m.addEventListener('click',e=>{if(e.target===m||e.target.closest('[data-close]'))closeModal();});
  const f=m.querySelector('textarea,input');if(f)setTimeout(()=>f.focus(),30);
  if(onMount)onMount(m);return m;
}
function closeModal(){const m=$('.modal');if(m)m.remove();}
const field=(id,label,type,extra)=>'<label class="fld" for="'+id+'"><span>'+label+'</span><input id="'+id+'" type="'+(type||'text')+'" '+(extra||'')+'></label>';

/* ---------- where each deck sits on the maps ---------- */
function stopOf(deckId){for(const w of WORLDS)for(const n of w.nodes)if(n.deck===deckId)return {world:w,node:n,key:w.id+':'+n.id};return null;}
const stopKey=(w,n)=>w.id+':'+n.id;

/* ---------- start up: decide guest or account ---------- */
ACCT.start=async function(){
  if(!BACK)return;                      /* no server configured: local-only, as before */
  try{const uid=await BACK.init(); if(uid&&await ACCT.enter(false))return;}
  catch(e){ACCT.offlineNote=niceErr(e);}
  let guest=false;try{guest=localStorage.getItem('calcgame.guest')==='1';}catch(e){}
  if(guest){ACCT.mode='guest';return;}
  return new Promise(res=>{ACCT.after=res;ACCT.welcome();});
};
ACCT.finish=function(){const r=ACCT.after;ACCT.after=null;if(r)r();else home();};

/* load the profile and the saved game for the signed-in user */
ACCT.enter=async function(fromGuest){
  const p=await BACK.profile(); if(!p){await BACK.signOut();return false;}
  ACCT.profile=p;ACCT.mode='user';
  const guestS=S;
  KEY='calcgame.v1.'+p.id;
  let cloud=null;try{cloud=await BACK.loadSave();}catch(e){}
  /* use whichever copy is newer: the phone's own copy can be ahead if the app closed before it synced */
  let local=null;try{local=JSON.parse(localStorage.getItem(KEY));}catch(e){}
  const cd=cloud&&cloud.data,newer=local&&(!cd||(local.savedAt||0)>(cd.savedAt||0));
  if(cd&&!newer){S=Object.assign(fresh(),cd);}
  else S=Object.assign(fresh(),local||(fromGuest?guestS:{}));
  S.preview=false; ACCT.lastPoints=-1; try{localStorage.setItem(KEY,JSON.stringify(S));}catch(e){}
  if(!cd||newer)ACCT.push(true);
  try{localStorage.removeItem('calcgame.guest');}catch(e){}
  ACCT.refresh();
  return true;
};
/* things that can load in the background */
ACCT.refresh=async function(){
  if(ACCT.mode!=='user')return;
  try{BACK.touch();}catch(e){}
  try{const d=await BACK.dueDates();ACCT.due={};d.forEach(x=>{ACCT.due[x.stop]=new Date(x.due_at);});}catch(e){}
  try{const c=await BACK.myCodes();ACCT.codes={};c.forEach(x=>{ACCT.codes[x.stop]=x;});}catch(e){}
  try{ACCT.stopsLogged=new Set(await BACK.myStops());ACCT.logStops();}catch(e){}
  ACCT.syncPoints();
  if($('.map'))home();
};

/* ---------- welcome, sign up, sign in ---------- */
ACCT.welcome=function(){
  const parade=['fox','basketball','owl','robot','penguin','soccer','frog','rocket'].map(a=>avatarSVG(a,'av par')).join('');
  screen({top:'',body:'<div class="welcome"><div class="parade">'+parade+'</div><h1>CalcGame</h1><p class="sub">Calculus practice, one stop at a time.</p>'+
    (ACCT.offlineNote?'<p class="note bad">'+esc(ACCT.offlineNote)+'</p>':'')+
    '<div class="wbtns"><button class="btn" id="w-new">Create an account</button><button class="btn ghost" id="w-in">Sign in</button></div>'+
    '<button class="link" id="w-guest">Just practice (no account)</button>'+
    '<p class="tiny">This is an optional study tool, not part of your grade. Accounts use a username you make up, with no real name or email. Without an account, your progress stays on this device only.</p></div>'});
  $('#w-new').onclick=()=>ACCT.signUp();
  $('#w-in').onclick=()=>ACCT.signIn();
  $('#w-guest').onclick=()=>{ACCT.mode='guest';try{localStorage.setItem('calcgame.guest','1');}catch(e){}ACCT.finish();};
};
ACCT.signUp=function(pre){
  const st=Object.assign({code:'',username:'',password:''},pre||{});
  screen({top:'<header class="bar"><button class="x" id="back" aria-label="Back">←</button><div class="bar-mid"><span class="bar-l">Create an account</span></div></header>',
    body:'<form class="form" id="su" autocomplete="off">'+
      field('su-code','Class code (from your instructor)','text','autocapitalize="characters" maxlength="12" value="'+esc(st.code)+'"')+'<p class="tiny" id="su-cn"></p>'+
      field('su-user','Pick a username','text','autocapitalize="off" maxlength="20" value="'+esc(st.username)+'"')+
      '<p class="tiny">3 to 20 letters, numbers or _. <strong>Please do not use your real name.</strong> Classmates see it on the leaderboard.</p>'+
      field('su-pw','Password (at least 6 characters)','password','autocomplete="new-password"')+field('su-pw2','Password again','password','autocomplete="new-password"')+
      '<p class="tiny">Write it down. There is no email reset; if you forget it, your instructor can set a new one.</p><div class="fb" id="su-fb" hidden></div></form>',
    foot:'<button class="btn" id="su-go">Next: pick your character</button>'});
  $('#back').onclick=()=>ACCT.welcome();
  const say=m=>sayIn($('#su-fb'),false,m);
  let t=null; $('#su-code').oninput=e=>{clearTimeout(t);const v=e.target.value.trim();$('#su-cn').textContent='';
    if(v.length>=4)t=setTimeout(async()=>{try{const n=await BACK.classOk(v);$('#su-cn').textContent=n?'✓ '+n:'That class code was not found.';$('#su-cn').className='tiny '+(n?'okt':'badt');}catch(e){}},350);};
  const go=async()=>{
    const code=$('#su-code').value.trim(),username=$('#su-user').value.trim(),pw=$('#su-pw').value,pw2=$('#su-pw2').value;
    if(!code)return say('Enter the class code your instructor gave you.');
    if(!USERNAME_RE.test(username))return say('Usernames are 3 to 20 letters, numbers or _ (no spaces).');
    if(pw.length<6)return say('Use a password of at least 6 characters.');
    if(pw!==pw2)return say('The two passwords do not match.');
    $('#su-go').disabled=true;
    try{
      const n=await BACK.classOk(code); if(!n){$('#su-go').disabled=false;return say('That class code was not found. Check it with your instructor.');}
      if(!(await BACK.usernameFree(username))){$('#su-go').disabled=false;return say('That username is taken. Try another.');}
    }catch(e){$('#su-go').disabled=false;return say(niceErr(e));}
    ACCT.pickAvatar('blob',async av=>{
      try{await BACK.signUp({code,username,password:pw,avatar:av});await ACCT.enter(true);toast('Welcome, '+username+'!');ACCT.finish();}
      catch(e){ACCT.signUp({code,username});setTimeout(()=>sayIn($('#su-fb'),false,niceErr(e)),0);}
    },()=>ACCT.signUp({code,username}),'Create my account');
  };
  $('#su-go').onclick=go; $('#su').onsubmit=e=>{e.preventDefault();go();};
};
ACCT.signIn=function(){
  screen({top:'<header class="bar"><button class="x" id="back" aria-label="Back">←</button><div class="bar-mid"><span class="bar-l">Sign in</span></div></header>',
    body:'<form class="form" id="si">'+field('si-user','Username','text','autocapitalize="off" autocomplete="username"')+field('si-pw','Password','password','autocomplete="current-password"')+
      '<p class="tiny">Forgot your password? Ask your instructor to set a new one.</p><div class="fb" id="si-fb" hidden></div></form>',
    foot:'<button class="btn" id="si-go">Sign in</button>'});
  $('#back').onclick=()=>ACCT.mode==='guest'?ACCT.profileScreen():ACCT.welcome();
  const go=async()=>{
    const username=$('#si-user').value.trim(),password=$('#si-pw').value; if(!username||!password)return;
    $('#si-go').disabled=true;
    try{await BACK.signIn({username,password});await ACCT.enter(false);toast('Welcome back!');ACCT.finish();}
    catch(e){$('#si-go').disabled=false;sayIn($('#si-fb'),false,niceErr(e));}
  };
  $('#si-go').onclick=go;$('#si').onsubmit=e=>{e.preventDefault();go();};
};

/* ---------- character picker ---------- */
ACCT.pickAvatar=function(cur,onPick,onBack,btnText){
  let sel=cur||'blob';
  const groups=[['animal','Animals'],['ball','Sports'],['other','Other']];
  screen({top:'<header class="bar"><button class="x" id="back" aria-label="Back">←</button><div class="bar-mid"><span class="bar-l">Pick your character</span></div></header>',
    body:'<div class="avbig" id="avbig"></div>'+groups.map(([g,t])=>'<p class="eyebrow">'+t+'</p><div class="avgrid">'+AVATARS.filter(a=>a.g===g).map(a=>
      '<button class="avb" data-av="'+a.id+'" aria-label="'+esc(a.name)+'" aria-pressed="'+(a.id===sel)+'">'+avatarSVG(a.id)+'</button>').join('')+'</div>').join(''),
    foot:'<button class="btn" id="av-go">'+esc(btnText||'Use this character')+'</button>'});
  const show=()=>{$('#avbig').innerHTML=avatarSVG(sel,'av big')+'<span>'+esc(avatarById(sel).name)+'</span>';app.querySelectorAll('.avb').forEach(b=>b.setAttribute('aria-pressed',b.dataset.av===sel));};
  app.querySelectorAll('.avb').forEach(b=>b.onclick=()=>{sel=b.dataset.av;show();});
  $('#back').onclick=onBack; $('#av-go').onclick=()=>{$('#av-go').disabled=true;onPick(sel);}; show();
};
ACCT.avatar=()=>ACCT.profile?ACCT.profile.avatar:(S.avatar||'blob');

/* ---------- profile screen ---------- */
ACCT.profileScreen=function(){
  const p=ACCT.profile,guest=ACCT.mode!=='user';
  let codes='';
  if(!guest){const list=Object.values(ACCT.codes);
    codes='<h3 class="sec-h">Completion codes</h3>'+(list.length?'<div class="codes">'+list.map(c=>{const s=ACCT.stopName(c.stop);
      return '<div class="code-r"><span>'+esc(s)+'</span><b>'+esc(c.code)+'</b><em>'+(c.redeemed_at?'used':'not used yet')+'</em></div>';}).join('')+'</div>':'<p class="tiny">Clear a stop on the map to get a code for it.</p>');}
  screen({top:bar('You',null),
    body:'<div class="me"><div class="me-av">'+avatarSVG(ACCT.avatar(),'av big')+'</div><div><h2>'+(guest?'Guest':esc(p.username))+'</h2><p class="tiny">'+(guest?'Progress is saved on this device only.':esc(p.class_name||''))+'</p></div></div>'+
      '<div class="row"><button class="btn small ghost" id="me-av">Change character</button>'+(guest?'':'<button class="btn small ghost" id="me-out">Sign out</button>')+'</div>'+
      (guest?'<div class="row"><button class="btn small" id="me-new">Create an account</button><button class="btn small ghost" id="me-in">Sign in</button></div><p class="tiny">An account keeps your progress on every device, puts you on the class leaderboard, and gives you completion codes. Your progress so far comes with you.</p>':'')+
      codes+'<h3 class="sec-h">Points</h3><p class="txt">'+S.points+' game points · '+S.plays+' plays ready</p>'});
  $('#me-av').onclick=()=>ACCT.pickAvatar(ACCT.avatar(),async av=>{
    if(guest){S.avatar=av;save();}else{ACCT.profile.avatar=av;try{await BACK.setAvatar(av);}catch(e){toast(niceErr(e));}}
    ACCT.profileScreen();},()=>ACCT.profileScreen());
  if($('#me-out'))$('#me-out').onclick=async()=>{await ACCT.flush();await BACK.signOut();ACCT.mode='guest';ACCT.profile=null;KEY='calcgame.v1';
    try{S=Object.assign(fresh(),JSON.parse(localStorage.getItem(KEY))||{});}catch(e){S=fresh();}ACCT.welcome();ACCT.after=null;};
  if($('#me-new'))$('#me-new').onclick=()=>ACCT.signUp();
  if($('#me-in'))$('#me-in').onclick=()=>ACCT.signIn();
};
ACCT.stopName=k=>{const [w,n]=String(k).split(':');const W=WORLDS.find(x=>x.id===w);const N=W&&W.nodes.find(x=>x.id===n);return N?N.title+(W.world?' (World '+W.world+')':''):k;};

/* ---------- syncing ---------- */
ACCT.saved=function(){ if(ACCT.mode!=='user'||S.preview)return; clearTimeout(ACCT.st); ACCT.st=setTimeout(()=>ACCT.push(),2500); if(S.points!==ACCT.lastPoints)ACCT.syncPoints(); };
ACCT.push=async function(now){ if(ACCT.mode!=='user')return; try{const d=Object.assign({},S);delete d.preview;await BACK.pushSave(d);}catch(e){} };
ACCT.syncPoints=async function(){ if(ACCT.mode!=='user')return; ACCT.lastPoints=S.points; try{await BACK.syncPoints(S.points);}catch(e){} };
ACCT.answer=function(q,ok){
  if(ACCT.mode!=='user'||S.preview||!DECK||!q||!q.id)return;
  ACCT.queue.push({deck:DECK.id,area:AREA,qid:String(q.id),ok:!!ok});
  clearTimeout(ACCT.qt); if(ACCT.queue.length>=10)ACCT.flush(); else ACCT.qt=setTimeout(()=>ACCT.flush(),5000);
};
ACCT.flush=async function(){
  clearTimeout(ACCT.qt); if(!ACCT.queue.length||ACCT.mode!=='user')return; const rows=ACCT.queue.splice(0);
  try{await BACK.logAnswers(rows);}catch(e){ACCT.queue=rows.concat(ACCT.queue).slice(-500);}
};
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden'){ACCT.flush();if(ACCT.mode==='user')ACCT.push();}});
/* lesson finished, drill set finished; also notices when the stop becomes cleared */
ACCT.done=async function(kind,ref,score,outOf){
  if(ACCT.mode!=='user'||S.preview||!DECK)return;
  ACCT.flush();
  try{await BACK.logCompletion({deck:DECK.id,kind,ref,score:score==null?null:score,out_of:outOf==null?null:outOf});}catch(e){}
  ACCT.logStops();
};
/* log every cleared stop once (also catches stops cleared before the account existed) */
ACCT.logStops=async function(){
  if(ACCT.mode!=='user'||!ACCT.stopsLogged||S.preview)return;
  for(const w of WORLDS)for(const n of w.nodes){
    if(!n.deck||n.kind==='start')continue; const d=DECKS[n.deck],k=stopKey(w,n);
    if(d&&!d.error&&deckCleared(d)&&!ACCT.stopsLogged.has(k)){ACCT.stopsLogged.add(k);
      try{await BACK.logCompletion({deck:n.deck,kind:'stop',ref:k});}catch(e){ACCT.stopsLogged.delete(k);}}
  }
};

/* ---------- due dates and codes on the map ---------- */
const DAY=86400000;
ACCT.dueHTML=function(w,n){
  const d=ACCT.due[stopKey(w,n)]; if(!d)return '';
  const left=Math.ceil((d-Date.now())/DAY),cleared=nodeCleared(n);
  const when=d.toLocaleDateString(undefined,{weekday:'short',month:'short',day:'numeric'});
  const cls=cleared?'ok':left<0?'late':left<=2?'soon':'';
  return '<p class="due '+cls+'">Due '+esc(when)+(cleared?' · done ✓':left<0?' · past due':left===0?' · today':left===1?' · tomorrow':' · '+left+' days left')+'</p>';
};
ACCT.dueDot=function(w,n){const d=ACCT.due[stopKey(w,n)];if(!d||nodeCleared(n))return '';const left=(d-Date.now())/DAY;return left<0?' late':left<=3?' soon':'';};
ACCT.codeHTML=function(w,n){
  if(ACCT.mode!=='user'||!nodeCleared(n)||n.kind==='start')return '';
  const c=ACCT.codes[stopKey(w,n)];
  return '<div class="codebox">'+(c?'<span>Completion code</span><b class="code">'+esc(c.code)+'</b><button class="btn small ghost" data-copy="'+esc(c.code)+'">Copy</button>'
    :'<button class="btn small ghost" data-claim="'+esc(stopKey(w,n))+'">Get my completion code</button>')+'</div>';
};
document.addEventListener('click',async e=>{
  const c=e.target.closest('[data-claim]');
  if(c){c.disabled=true;try{await ACCT.logStops();const k=await BACK.claimCode(c.dataset.claim);ACCT.codes[c.dataset.claim]={code:k,stop:c.dataset.claim};home();}catch(err){c.disabled=false;toast(niceErr(err));}return;}
  const cp=e.target.closest('[data-copy]');
  if(cp){try{await navigator.clipboard.writeText(cp.dataset.copy);toast('Copied '+cp.dataset.copy);}catch(err){toast(cp.dataset.copy);}}
});

/* ---------- leaderboard (on the Match Board screen) ---------- */
ACCT.leaderboard=async function(host){
  if(ACCT.mode!=='user'){host.innerHTML='<p class="tiny">'+(BACK?'Create an account to join your class leaderboard.':'')+'</p>';return;}
  host.innerHTML='<p class="tiny">Loading the leaderboard…</p>';
  try{await ACCT.syncPoints();const L=await BACK.leaderboard(); if(!document.body.contains(host))return;
    const top=L.slice(0,10),mi=L.findIndex(r=>r.me),row=(r,i)=>'<li class="'+(r.me?'me':'')+'"><span class="rk">'+(i+1)+'</span>'+avatarSVG(r.avatar)+'<span class="nm">'+esc(r.username)+'</span><b>'+r.points+'</b></li>';
    host.innerHTML=ACCT.lbCache='<h3 class="sec-h">Class leaderboard</h3><ol class="lb">'+top.map(row).join('')+(mi>=10?'<li class="gap">…</li>'+row(L[mi],mi):'')+'</ol>';}
  catch(e){host.innerHTML='<p class="tiny">Leaderboard unavailable: '+esc(niceErr(e))+'</p>';}
};

/* ---------- Send feedback (always on screen) ---------- */
ACCT.feedback=function(){
  if(!BACK){modal('<h2>Send feedback</h2><p class="txt">Feedback needs the class server, which is not set up yet.</p><div class="row"><button class="btn small" data-close>OK</button></div>');return;}
  const where=CUR?CUR.where:'the map';
  modal('<h2>Send feedback</h2><p class="tiny">About: '+esc(where)+'</p><div class="chips fbk">'+['Something is broken','A question seems wrong','An idea','Other'].map((t,i)=>'<button class="chip" data-k="'+i+'" aria-pressed="'+(i===0)+'">'+t+'</button>').join('')+'</div>'+
    '<textarea id="fb-t" rows="5" maxlength="2000" placeholder="What happened, or what would make this better?"></textarea><p class="tiny" id="fb-n"></p>'+
    '<div class="row"><button class="btn small ghost" data-close>Cancel</button><button class="btn small" id="fb-go" disabled>Send</button></div>',m=>{
    let kind='Something is broken';
    m.querySelectorAll('.fbk .chip').forEach(b=>b.onclick=()=>{kind=b.textContent;m.querySelectorAll('.fbk .chip').forEach(x=>x.setAttribute('aria-pressed',x===b));});
    const t=$('#fb-t',m),go=$('#fb-go',m); t.oninput=()=>{go.disabled=WORDS(t.value)<3;};
    go.onclick=async()=>{go.disabled=true;
      try{await BACK.sendMessage({kind:'feedback',deck:CUR?CUR.deck:null,ref:CUR?CUR.qid:null,context:kind+' · '+where+(CUR&&CUR.text?' · '+CUR.text:''),body:t.value.trim()});closeModal();toast('Thanks! Your feedback was sent.');}
      catch(e){go.disabled=false;toast(niceErr(e));}};
  });
};
/* ---------- I don't understand: it takes real words to send ---------- */
const STUCK_MIN={know:6,stuck:12};
ACCT.stuck=function(){
  if(!BACK){modal('<h2>I don’t understand</h2><p class="txt">This needs the class server, which is not set up yet. Ask your question in class!</p><div class="row"><button class="btn small" data-close>OK</button></div>');return;}
  const c=CUR||{where:'the map'};
  modal('<h2>I don’t understand</h2><p class="tiny">About: <strong>'+esc(c.where)+'</strong></p>'+(c.text?'<p class="ctx">“'+esc(c.text)+'”</p>':'')+
    '<p class="tiny">Your instructor reads these to plan class. Explaining your question in words often answers it, so take a moment.</p>'+
    '<label class="fld"><span>What do you understand so far? (at least '+STUCK_MIN.know+' words)</span><textarea id="st-k" rows="3" maxlength="1500"></textarea></label><p class="tiny wc" id="st-kn"></p>'+
    '<label class="fld"><span>What exactly is confusing you? (at least '+STUCK_MIN.stuck+' words)</span><textarea id="st-s" rows="4" maxlength="2500"></textarea></label><p class="tiny wc" id="st-sn"></p>'+
    '<div class="row"><button class="btn small ghost" data-close>Cancel</button><button class="btn small" id="st-go" disabled>Send my question</button></div>',m=>{
    const k=$('#st-k',m),s=$('#st-s',m),go=$('#st-go',m);
    const upd=()=>{const a=WORDS(k.value),b=WORDS(s.value);
      $('#st-kn',m).textContent=a+' / '+STUCK_MIN.know+' words';$('#st-kn',m).className='tiny wc'+(a>=STUCK_MIN.know?' okt':'');
      $('#st-sn',m).textContent=b+' / '+STUCK_MIN.stuck+' words';$('#st-sn',m).className='tiny wc'+(b>=STUCK_MIN.stuck?' okt':'');
      go.disabled=a<STUCK_MIN.know||b<STUCK_MIN.stuck;};
    k.oninput=upd;s.oninput=upd;upd();
    go.onclick=async()=>{go.disabled=true;
      try{await BACK.sendMessage({kind:'question',deck:c.deck||null,ref:c.qid||null,context:c.where+(c.text?' · '+c.text:''),body:'Understands: '+k.value.trim()+'\nConfused by: '+s.value.trim()});
        closeModal();toast('Sent. Your instructor will see it.');}
      catch(e){go.disabled=false;toast(niceErr(e));}};
  });
};
document.addEventListener('click',e=>{
  if(e.target.closest('[data-feedback]'))ACCT.feedback();
  else if(e.target.closest('[data-stuck]'))ACCT.stuck();
  else if(e.target.closest('[data-me]'))ACCT.profileScreen();
});
