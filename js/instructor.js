/* CalcGame instructor page: class data, questions, feedback, due dates, completion codes, classes.
   Students appear only by the usernames they chose. */
const R=document.getElementById('inst');
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const plain=s=>String(s||'').replace(/\$|\*\*/g,'').replace(/frac\{([^{}]*)\}\{([^{}]*)\}/g,'($1)/($2)').replace(/lim\[([^\]]*)\]/g,'lim($1) ').replace(/\\n|\n/g,' ');
const pct=(a,b)=>b?Math.round(100*a/b)+'%':'–';
const N=v=>Number(v)||0;
const fmtD=d=>d?new Date(d).toLocaleString(undefined,{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'}):'–';
const fmtDay=d=>d?new Date(d).toLocaleDateString(undefined,{month:'short',day:'numeric'}):'–';
const ago=d=>{if(!d)return '–';const s=(Date.now()-new Date(d))/1000;return s<3600?Math.max(1,Math.round(s/60))+' min ago':s<86400?Math.round(s/3600)+' h ago':Math.round(s/86400)+' d ago';};
function toast(m){const t=document.createElement('div');t.className='itoast';t.textContent=m;document.body.appendChild(t);setTimeout(()=>t.remove(),2800);}

/* ---------- content (maps and decks) for names and question text ---------- */
const C={worlds:[],decks:{},q:{}};
async function loadContent(){
  const j=async p=>{const r=await fetch(p,{cache:'no-cache'});return r.json();};
  const idx=await j('worlds.json'); C.worlds=(await Promise.all(idx.worlds.map(j))).sort((a,b)=>a.world-b.world);
  const ids=[...new Set(C.worlds.flatMap(w=>w.nodes.map(n=>n.deck).filter(Boolean)))];
  await Promise.all(ids.map(async id=>{try{C.decks[id]=await j('decks/'+id+'.json');}catch(e){}}));
  for(const [id,d] of Object.entries(C.decks)){
    const add=(q,where)=>{C.q[id+'|'+q.id]={text:plain(q.title?q.title+'. '+(q.text||''):q.text),type:q.type,where};(q.steps||[]).forEach((s,k)=>{if(!s.id)s.id=q.id+'.'+(k+1);});};
    (d.lessons||[d.lesson]).filter(Boolean).forEach((l,i)=>l.slides.forEach((q,k)=>add(q,(d.lessons?'Lesson '+(i+1):'Lesson')+', step '+(k+1))));
    Object.values(d.drills||{}).forEach(dr=>dr.questions.forEach(q=>add(q,dr.title)));
  }
}
const stopOfDeck=id=>{for(const w of C.worlds)for(const n of w.nodes)if(n.deck===id)return {w,n};return null;};
const deckName=id=>{const s=stopOfDeck(id);return s?s.n.title:id;};
const stopName=k=>{const [w,n]=String(k).split(':');const W=C.worlds.find(x=>x.id===w);const X=W&&W.nodes.find(x=>x.id===n);return X?X.title+' (W'+W.world+')':k;};

/* ---------- state ---------- */
const ST={cls:'',tab:'overview',classes:[],students:[],questions:[],comps:[],msgs:[],due:[],msgFilter:'new'};
const clsName=id=>{const c=ST.classes.find(c=>c.id===id);return c?c.name:'–';};

/* ---------- sign in ---------- */
function signInScreen(msg){
  R.innerHTML='<div class="auth"><h1>CalcGame <span>Instructor</span></h1>'+(BACK?'':'<p class="warn">No server is set up yet. Fill in js/config.js (see the setup guide), or open this page with <code>?mock=1</code> to try it with pretend data.</p>')+
    '<div class="auth-c"><h2>Sign in</h2><label>Username<input id="a-u" autocomplete="username"></label><label>Password<input id="a-p" type="password" autocomplete="current-password"></label>'+
    '<button class="btn" id="a-go">Sign in</button><p class="err" id="a-err">'+esc(msg||'')+'</p></div>'+
    '<details class="auth-c"><summary>First time? Create the instructor account</summary><p class="tiny">Pick a username (not your real name needed) and a strong password. After creating it, you will run one line in Supabase to make it an instructor.</p>'+
    '<label>Username<input id="c-u"></label><label>Password (8+ characters)<input id="c-p" type="password" autocomplete="new-password"></label><button class="btn ghost" id="c-go">Create instructor account</button><p class="err" id="c-err"></p></details></div>';
  if(!BACK){$('#a-go').disabled=true;$('#c-go').disabled=true;return;}
  $('#a-go').onclick=async()=>{try{await BACK.signIn({username:$('#a-u').value,password:$('#a-p').value});enter();}catch(e){$('#a-err').textContent=niceErr(e);}};
  $('#a-p').onkeydown=e=>{if(e.key==='Enter')$('#a-go').click();};
  $('#c-go').onclick=async()=>{const u=$('#c-u').value.trim(),p=$('#c-p').value;
    if(!USERNAME_RE.test(u))return $('#c-err').textContent='Usernames are 3 to 20 letters, numbers or _.';
    if(p.length<8)return $('#c-err').textContent='Use at least 8 characters.';
    try{await BACK.createInstructor({username:u,password:p});enter();}catch(e){$('#c-err').textContent=niceErr(e);}};
}
async function enter(){
  let p=null;try{p=await BACK.profile();}catch(e){}
  if(!p)return signInScreen('That account has no profile.');
  if(!p.is_instructor){
    R.innerHTML='<div class="auth"><h1>Almost there</h1><div class="auth-c"><p>The account <b>'+esc(p.username)+'</b> exists but is not an instructor yet. In Supabase, open <b>SQL Editor</b>, paste this line and press <b>Run</b>:</p>'+
      '<pre class="sql">update public.profiles set is_instructor = true where lower(username) = lower(\''+esc(p.username)+'\');</pre><button class="btn" id="re">I ran it: check again</button> <button class="btn ghost" id="out">Sign out</button></div></div>';
    $('#re').onclick=enter;$('#out').onclick=async()=>{await BACK.signOut();signInScreen();};return;
  }
  ST.me=p; shell(); await refresh();
}

/* ---------- layout ---------- */
const TABS=[['overview','Overview'],['students','Students'],['hard','Hard questions'],['questions','I don’t understand'],['feedback','Feedback'],['due','Due dates'],['codes','Completion codes'],['classes','Classes'],['setup','Setup and privacy']];
function shell(){
  R.innerHTML='<aside class="side"><div class="brand">CalcGame<span>Instructor</span></div><nav>'+TABS.map(([k,t])=>'<button data-tab="'+k+'">'+t+'<i id="badge-'+k+'"></i></button>').join('')+'</nav>'+
    '<div class="who">'+avatarSVG(ST.me.avatar)+'<span>'+esc(ST.me.username)+'</span><button class="link" id="out">Sign out</button></div></aside>'+
    '<main class="main"><header class="top"><h1 id="title"></h1><label class="clsel">Class <select id="cls"></select></label><button class="btn small ghost" id="ref">Refresh</button><span class="tiny" id="stamp"></span></header><div id="view"></div></main>';
  $$('[data-tab]').forEach(b=>b.onclick=()=>{ST.tab=b.dataset.tab;draw();});
  $('#out').onclick=async()=>{await BACK.signOut();signInScreen();};
  $('#ref').onclick=refresh;
  $('#cls').onchange=e=>{ST.cls=e.target.value;refresh();};
}
async function refresh(){
  $('#stamp').textContent='Loading…';
  try{
    ST.classes=await BACK.classes();
    const sel=$('#cls');sel.innerHTML='<option value="">All classes</option>'+ST.classes.map(c=>'<option value="'+c.id+'"'+(c.id===ST.cls?' selected':'')+'>'+esc(c.name)+'</option>').join('');
    const cls=ST.cls||null;
    [ST.students,ST.questions,ST.comps,ST.msgs,ST.due]=await Promise.all([BACK.students(cls),BACK.questions(cls),BACK.completions(cls),BACK.messages(),BACK.allDueDates()]);
    if(ST.cls)ST.msgs=ST.msgs.filter(m=>!m.class_id||m.class_id===ST.cls);
    $('#stamp').textContent='Updated '+new Date().toLocaleTimeString(undefined,{hour:'numeric',minute:'2-digit'});
  }catch(e){$('#stamp').textContent='Error: '+niceErr(e);}
  draw();
}
function draw(){
  $$('[data-tab]').forEach(b=>b.classList.toggle('on',b.dataset.tab===ST.tab));
  const nq=ST.msgs.filter(m=>m.kind==='question'&&m.status==='new').length,nf=ST.msgs.filter(m=>m.kind==='feedback'&&m.status==='new').length;
  $('#badge-questions').textContent=nq||'';$('#badge-feedback').textContent=nf||'';
  $('#title').textContent=TABS.find(t=>t[0]===ST.tab)[1];
  ({overview,students,hard,questions:()=>messages('question'),feedback:()=>messages('feedback'),due,codes,classes,setup}[ST.tab])();
}
const V=()=>$('#view');

/* ---------- Overview ---------- */
function overview(){
  const S=ST.students,week=Date.now()-7*86400000;
  const active=S.filter(s=>new Date(s.last_seen)>week).length,ans=S.reduce((a,s)=>a+N(s.answers),0),wr=S.reduce((a,s)=>a+N(s.wrong),0);
  const tiles=[['Students',S.length],['Active this week',active],['Lessons finished',S.reduce((a,s)=>a+N(s.lessons),0)],['Questions answered',ans],['Correct',pct(ans-wr,ans)],['New questions',ST.msgs.filter(m=>m.kind==='question'&&m.status==='new').length]];
  /* answers per day, last 21 days, from completions + messages is not enough; use completions as activity */
  const days=21,cnt=Array(days).fill(0),t0=new Date();t0.setHours(0,0,0,0);
  ST.comps.forEach(c=>{const d=Math.floor((t0-new Date(c.at))/86400000)+1;const i=days-d;if(i>=0&&i<days)cnt[i]++;});
  const mx=Math.max(1,...cnt);
  const spark='<svg class="spark" viewBox="0 0 '+(days*14)+' 70" role="img" aria-label="Lessons and drill sets finished per day">'+cnt.map((v,i)=>'<rect x="'+(i*14+2)+'" y="'+(62-56*v/mx)+'" width="10" height="'+(56*v/mx+0.5)+'" rx="2"><title>'+v+' on '+fmtDay(t0-((days-1-i)*86400000))+'</title></rect>').join('')+'<line x1="0" x2="'+(days*14)+'" y1="62.5" y2="62.5"/></svg>';
  /* per stop */
  const by={};ST.comps.forEach(c=>{const s=stopOfDeck(c.deck);if(!s)return;const k=s.w.id+':'+s.n.id,o=by[k]||(by[k]={lessons:new Set(),sets:0,score:0,out:0,cleared:new Set(),users:new Set()});
    o.users.add(c.user_id);if(c.kind==='lesson')o.lessons.add(c.user_id);if(c.kind==='drill'){o.sets++;o.score+=N(c.score);o.out+=N(c.out_of);}if(c.kind==='stop')o.cleared.add(c.user_id);});
  const qs={};ST.questions.forEach(q=>{const o=qs[q.deck]||(qs[q.deck]={a:0,w:0});o.a+=N(q.attempts);o.w+=N(q.wrong);});
  const dueOf=k=>{const d=ST.due.filter(x=>x.stop===k&&(!ST.cls||x.class_id===ST.cls));return d.length?fmtDay(d[0].due_at)+(d.length>1?' +':''):'';};
  const n=Math.max(1,S.length);
  const rows=C.worlds.map(w=>{const stops=w.nodes.filter(x=>x.deck&&x.kind!=='start');if(!stops.some(x=>by[w.id+':'+x.id]||qs[x.deck]))return '';
    return '<tr class="wrow"><td colspan="7">World '+w.world+': '+esc(w.title)+'</td></tr>'+stops.map(x=>{const k=w.id+':'+x.id,o=by[k],q=qs[x.deck]||{a:0,w:0};
      const cl=o?o.cleared.size:0;
      return '<tr><td>'+esc(x.title)+(x.kind!=='main'?' <em class="kind">'+x.kind+'</em>':'')+'</td><td>'+esc(dueOf(k))+'</td><td>'+(o?o.users.size:0)+'</td><td>'+(o?o.lessons.size:0)+'</td><td><span class="ibar"><i style="width:'+(100*cl/n)+'%"></i></span>'+cl+'</td><td>'+(o&&o.out?pct(o.score,o.out):'–')+'</td><td>'+(q.a?q.a+' · <b class="'+(q.w/q.a>0.35?'hot':'')+'">'+pct(q.w,q.a)+'</b> wrong':'–')+'</td></tr>';}).join('');}).join('');
  V().innerHTML='<div class="tiles">'+tiles.map(t=>'<div class="tile2"><b>'+t[1]+'</b><span>'+t[0]+'</span></div>').join('')+'</div>'+
    '<section class="panel"><h2>Activity: lessons and drill sets finished per day (last 3 weeks)</h2>'+spark+'</section>'+
    '<section class="panel"><h2>By stop</h2>'+(rows?'<table class="tbl"><thead><tr><th>Stop</th><th>Due</th><th>Students started</th><th>Finished a lesson</th><th>Cleared the stop</th><th>Avg drill score</th><th>Answers</th></tr></thead><tbody>'+rows+'</tbody></table>':'<p class="empty">No activity yet.</p>')+'</section>';
}

/* ---------- Students ---------- */
function students(){
  const S=ST.students.slice();
  V().innerHTML='<section class="panel"><p class="tiny">Students are listed by the username they chose. Keep it that way: don’t make a list matching usernames to real names.</p>'+
    (S.length?'<table class="tbl sortable"><thead><tr><th data-k="username">Student</th>'+(ST.cls?'':'<th data-k="class_id">Class</th>')+'<th data-k="created_at">Joined</th><th data-k="last_seen">Last seen</th><th data-k="stops">Stops cleared</th><th data-k="lessons">Lessons</th><th data-k="sets">Drill sets</th><th data-k="answers">Answers</th><th data-k="wrongp">Wrong</th><th data-k="points">Points</th><th></th></tr></thead><tbody>'+
    S.map(s=>'<tr data-id="'+s.id+'"><td class="who2">'+avatarSVG(s.avatar)+esc(s.username)+'</td>'+(ST.cls?'':'<td>'+esc(clsName(s.class_id))+'</td>')+'<td>'+fmtDay(s.created_at)+'</td><td>'+ago(s.last_seen)+'</td><td>'+N(s.stops)+'</td><td>'+N(s.lessons)+'</td><td>'+N(s.sets)+'</td><td>'+N(s.answers)+'</td><td>'+pct(N(s.wrong),N(s.answers))+'</td><td>'+N(s.points)+'</td>'+
      '<td class="acts2"><button class="link" data-detail>Details</button><button class="link" data-reset>Reset password</button><button class="link danger" data-del>Remove</button></td></tr>').join('')+'</tbody></table>':'<p class="empty">No students yet. Give them the class code from the Classes tab.</p>')+'</section><div id="detail"></div>';
  $$('tr[data-id]').forEach(tr=>{const s=ST.students.find(x=>x.id===tr.dataset.id);
    $('[data-detail]',tr).onclick=()=>detail(s);
    $('[data-reset]',tr).onclick=async()=>{const p=prompt('New password for '+s.username+' (at least 6 characters). Tell it to them in person.');if(!p)return;try{await BACK.resetPassword(s.username,p);toast('Password changed for '+s.username);}catch(e){alert(niceErr(e));}};
    $('[data-del]',tr).onclick=async()=>{if(!confirm('Remove '+s.username+' and all of their data? This cannot be undone.'))return;try{await BACK.deleteStudent(s.id);toast('Removed '+s.username);refresh();}catch(e){alert(niceErr(e));}};});
  sortable();
}
function detail(s){
  const c=ST.comps.filter(x=>x.user_id===s.id).slice().reverse(),m=ST.msgs.filter(x=>x.username===s.username);
  $('#detail').innerHTML='<section class="panel"><h2>'+avatarSVG(s.avatar)+' '+esc(s.username)+'</h2><div class="cols"><div><h3>Timeline</h3>'+(c.length?'<table class="tbl compact"><tbody>'+c.map(x=>'<tr><td>'+fmtD(x.at)+'</td><td>'+esc(deckName(x.deck))+'</td><td>'+
    (x.kind==='lesson'?'Finished lesson '+esc(x.ref):x.kind==='drill'?'Drill set ('+esc(x.ref)+'): '+N(x.score)+' / '+N(x.out_of):'<b>Cleared the stop</b>')+'</td></tr>').join('')+'</tbody></table>':'<p class="empty">Nothing yet.</p>')+'</div>'+
    '<div><h3>Messages</h3>'+(m.length?m.map(msgCard).join(''):'<p class="empty">None.</p>')+'</div></div></section>';
  $('#detail').scrollIntoView({behavior:'smooth'});
}
function sortable(){
  $$('.sortable th[data-k]').forEach(th=>th.onclick=()=>{const k=th.dataset.k,dir=th.dataset.d==='1'?-1:1;$$('.sortable th').forEach(x=>delete x.dataset.d);th.dataset.d=dir===1?'1':'-1';
    const val=s=>k==='wrongp'?N(s.wrong)/Math.max(1,N(s.answers)):k==='class_id'?clsName(s.class_id):s[k];
    ST.students.sort((a,b)=>{const x=val(a),y=val(b);return (typeof x==='string'?String(x).localeCompare(String(y)):N(x)-N(y))*dir;});students();});
}

/* ---------- Hard questions ---------- */
function hard(){
  const decks=[...new Set(ST.questions.map(q=>q.deck))];
  const f=ST.hardDeck||'',min=ST.hardMin||3;
  const rows=ST.questions.filter(q=>(!f||q.deck===f)&&N(q.students)>=1&&N(q.attempts)>=min).map(q=>{const info=C.q[q.deck+'|'+q.qid]||{};
    return Object.assign({},q,{text:info.text||'(question '+q.qid+')',where:info.where||q.area,firstRate:N(q.first_try_wrong)/Math.max(1,N(q.students)),rate:N(q.wrong)/Math.max(1,N(q.attempts))});})
    .sort((a,b)=>b.firstRate-a.firstRate||b.attempts-a.attempts).slice(0,80);
  V().innerHTML='<section class="panel"><div class="filters"><label>Stop <select id="hd"><option value="">All stops</option>'+decks.map(d=>'<option value="'+d+'"'+(d===f?' selected':'')+'>'+esc(deckName(d))+'</option>').join('')+'</select></label>'+
    '<label>At least <input id="hm" type="number" min="1" value="'+min+'" style="width:4em"> attempts</label></div>'+
    '<p class="tiny">Sorted by how many students missed it on their <b>first</b> try. Lesson questions are answered until right, so they show where the explanation needs work.</p>'+
    (rows.length?'<table class="tbl"><thead><tr><th>Missed first try</th><th>Stop</th><th>Where</th><th>Question</th><th>Students</th><th>All attempts wrong</th></tr></thead><tbody>'+rows.map(q=>
      '<tr><td><span class="ibar hot"><i style="width:'+(100*q.firstRate)+'%"></i></span>'+Math.round(100*q.firstRate)+'%</td><td>'+esc(deckName(q.deck))+'</td><td class="tiny">'+esc(q.where)+'<br>'+esc(q.qid)+'</td><td class="qtext">'+esc(q.text.slice(0,220))+'</td><td>'+N(q.students)+'</td><td>'+N(q.wrong)+' of '+N(q.attempts)+'</td></tr>').join('')+'</tbody></table>':'<p class="empty">Not enough answers yet.</p>')+'</section>';
  $('#hd').onchange=e=>{ST.hardDeck=e.target.value;hard();};$('#hm').onchange=e=>{ST.hardMin=Math.max(1,+e.target.value||1);hard();};
}

/* ---------- I don't understand / Feedback ---------- */
function msgCard(m){
  return '<article class="msg'+(m.status==='done'?' done':'')+'" data-mid="'+m.id+'"><header><b>'+esc(m.deck?deckName(m.deck):'General')+'</b><span>'+esc(m.username||'guest')+' · '+fmtD(m.created_at)+'</span></header>'+
    (m.context?'<p class="ctx2">'+esc(m.context)+'</p>':'')+'<p class="body2">'+esc(m.body).replace(/\n/g,'<br>')+'</p>'+
    '<footer><button class="btn small ghost" data-st="'+(m.status==='done'?'new':'done')+'">'+(m.status==='done'?'Mark as new':(m.kind==='question'?'Discussed ✓':'Handled ✓'))+'</button><button class="link danger" data-rm>Delete</button></footer></article>';
}
function messages(kind){
  const all=ST.msgs.filter(m=>m.kind===kind),list=all.filter(m=>ST.msgFilter==='all'||m.status==='new');
  const groups={};list.forEach(m=>{const k=m.deck?deckName(m.deck):'General';(groups[k]=groups[k]||[]).push(m);});
  V().innerHTML='<section class="panel"><div class="filters"><div class="seg"><button data-f="new" class="'+(ST.msgFilter==='new'?'on':'')+'">New ('+all.filter(m=>m.status==='new').length+')</button><button data-f="all" class="'+(ST.msgFilter==='all'?'on':'')+'">All ('+all.length+')</button></div>'+
    (kind==='question'?'<button class="btn small ghost" id="copy">Copy new questions as class notes</button>':'')+'</div>'+
    (kind==='question'?'<p class="tiny">Students must write at least 18 words (what they understand, and what confuses them) before a question sends.</p>':'')+
    (list.length?Object.entries(groups).map(([g,ms])=>'<h3 class="grp">'+esc(g)+' <span>'+ms.length+'</span></h3><div class="msgs">'+ms.map(msgCard).join('')+'</div>').join(''):'<p class="empty">Nothing here.</p>')+'</section>';
  $$('[data-f]').forEach(b=>b.onclick=()=>{ST.msgFilter=b.dataset.f;messages(kind);});
  $$('.msg').forEach(el=>{const id=+el.dataset.mid||el.dataset.mid,m=ST.msgs.find(x=>String(x.id)===String(el.dataset.mid));
    $('[data-st]',el).onclick=async e=>{try{await BACK.setMessage(m.id,e.target.dataset.st);m.status=e.target.dataset.st;draw();}catch(err){alert(niceErr(err));}};
    $('[data-rm]',el).onclick=async()=>{if(!confirm('Delete this message?'))return;try{await BACK.deleteMessage(m.id);ST.msgs=ST.msgs.filter(x=>x!==m);draw();}catch(err){alert(niceErr(err));}};});
  if($('#copy'))$('#copy').onclick=async()=>{const txt=Object.entries(groups).map(([g,ms])=>g+'\n'+ms.filter(m=>m.status==='new').map(m=>'- ('+(m.context||'')+') '+m.body.replace(/\n/g,' / ')).join('\n')).join('\n\n');
    try{await navigator.clipboard.writeText(txt);toast('Copied');}catch(e){prompt('Copy this:',txt);}};
}

/* ---------- Due dates ---------- */
function due(){
  if(!ST.cls){V().innerHTML='<section class="panel"><p class="empty">Pick a class at the top to set its due dates.</p>'+(ST.classes.length?'':'<p>You have no classes yet. Make one on the Classes tab.</p>')+'</section>';return;}
  const cur={};ST.due.filter(d=>d.class_id===ST.cls).forEach(d=>{cur[d.stop]=d.due_at;});
  const loc=d=>{if(!d)return '';const x=new Date(d);x.setMinutes(x.getMinutes()-x.getTimezoneOffset());return x.toISOString().slice(0,16);};
  V().innerHTML='<section class="panel"><p class="tiny">Due dates show on the student map and in each stop’s panel ("2 days left", "past due"). They are reminders only. Leave a stop blank for no due date.</p>'+
    C.worlds.map(w=>'<h3 class="grp">World '+w.world+': '+esc(w.title)+'</h3><div class="duegrid">'+w.nodes.filter(n=>n.kind!=='start').map(n=>{const k=w.id+':'+n.id;
      return '<label class="dueitem'+(n.deck?'':' off')+'"><span>'+esc(n.title)+(n.kind!=='main'?' <em class="kind">'+n.kind+'</em>':'')+'</span><input type="datetime-local" data-stop="'+k+'" value="'+loc(cur[k])+'"'+(n.deck?'':' disabled')+'></label>';}).join('')+'</div>').join('')+'</section>';
  $$('[data-stop]').forEach(inp=>inp.onchange=async()=>{const k=inp.dataset.stop,v=inp.value?new Date(inp.value).toISOString():null;
    try{await BACK.setDue(ST.cls,k,v);ST.due=ST.due.filter(d=>!(d.class_id===ST.cls&&d.stop===k));if(v)ST.due.push({class_id:ST.cls,stop:k,due_at:v});toast(v?'Saved':'Cleared');inp.classList.add('saved');}
    catch(e){alert(niceErr(e));}});
}

/* ---------- Completion codes ---------- */
function parseCSV(t){const rows=[];let r=[],f='',q=false;for(let i=0;i<t.length;i++){const c=t[i];
  if(q){if(c==='"'){if(t[i+1]==='"'){f+='"';i++;}else q=false;}else f+=c;}
  else if(c==='"')q=true;else if(c===','){r.push(f);f='';}else if(c==='\n'||c==='\r'){if(c==='\r'&&t[i+1]==='\n')i++;r.push(f);rows.push(r);r=[];f='';}else f+=c;}
  if(f||r.length){r.push(f);rows.push(r);}return rows.filter(x=>x.some(v=>v.trim()));}
const CODE_RE=/CG-[A-Z2-9]{6}/gi;
function codes(){
  V().innerHTML='<section class="panel"><h2>How it works</h2><ol class="how"><li>When a student clears a stop, the app gives them a one-time code like <code>CG-7K3QXM</code>. It is tied to their username and that stop.</li>'+
    '<li>In Canvas, make a quiz (or survey) with a text-answer question: “Paste your completion code(s).” Students paste their codes there.</li>'+
    '<li>Download the quiz’s <b>Student Analysis</b> report (a CSV) and drop it below. Names stay in your browser; only the codes are sent to the server to be checked.</li>'+
    '<li>Review the results, then press <b>Mark as used</b>. A used code can never count again, and a code pasted by two students is flagged.</li></ol></section>'+
    '<section class="panel"><h2>Check codes</h2><div class="drop" id="drop">Drop the Canvas CSV here, or <label class="link">choose a file<input type="file" id="file" accept=".csv,text/csv" hidden></label>, or paste below (one student per line: name, code).</div>'+
    '<textarea id="paste" rows="5" placeholder="Jane Doe, CG-7K3QXM"></textarea><div class="row"><button class="btn small" id="check">Check codes</button></div><div id="cres"></div></section>';
  const run=async rows=>{
    if(!rows.length)return;
    let head=rows[0].map(h=>h.toLowerCase()),ni=head.findIndex(h=>h==='name'||h==='student'||h==='student name'),start=1;
    if(ni<0){ni=0;start=head.join(' ').match(CODE_RE)?0:1;}
    const items=[];rows.slice(start).forEach(r=>{const name=(r[ni]||'').trim();const found=(r.join(' ').match(CODE_RE)||[]).map(c=>c.toUpperCase());
      if(!found.length)items.push({name,code:'',status:'none'});[...new Set(found)].forEach(code=>items.push({name,code}));});
    const all=[...new Set(items.filter(i=>i.code).map(i=>i.code))];
    let info=[];try{info=all.length?await BACK.checkCodes(all):[];}catch(e){$('#cres').innerHTML='<p class="err">'+esc(niceErr(e))+'</p>';return;}
    const byCode={};info.forEach(c=>{byCode[c.code]=c;});
    const users={};items.forEach(i=>{if(i.code)(users[i.code]=users[i.code]||new Set()).add(i.name.toLowerCase());});
    items.forEach(i=>{if(!i.code)return;const c=byCode[i.code];
      i.stop=c?stopName(c.stop):'';
      i.status=!c?'invalid':c.redeemed_at?'used':users[i.code].size>1?'shared':'ok';i.when=c&&c.redeemed_at;});
    const lab={ok:['ok','Valid, new'],used:['bad','Already used'],shared:['bad','Pasted by more than one student'],invalid:['bad','Not a real code'],none:['muted','No code found']};
    const per={};items.filter(i=>i.status==='ok').forEach(i=>{per[i.name]=(per[i.name]||0)+1;});
    ST.okCodes=[...new Set(items.filter(i=>i.status==='ok').map(i=>i.code))];ST.codeItems=items;
    $('#cres').innerHTML='<p><b>'+ST.okCodes.length+'</b> valid new codes from <b>'+Object.keys(per).length+'</b> students. '+
      (ST.okCodes.length?'<button class="btn small" id="redeem">Mark '+ST.okCodes.length+' as used</button> ':'')+'<button class="btn small ghost" id="dl">Download results (CSV)</button></p>'+
      '<table class="tbl"><thead><tr><th>Student</th><th>Code</th><th>Stop</th><th>Status</th></tr></thead><tbody>'+items.map(i=>'<tr><td>'+esc(i.name)+'</td><td><code>'+esc(i.code)+'</code></td><td>'+esc(i.stop||'')+'</td><td class="'+lab[i.status][0]+'">'+lab[i.status][1]+(i.when?' ('+fmtDay(i.when)+')':'')+'</td></tr>').join('')+'</tbody></table>'+
      '<h3>Valid codes per student</h3><table class="tbl compact"><tbody>'+Object.entries(per).sort().map(([n,c])=>'<tr><td>'+esc(n)+'</td><td>'+c+'</td></tr>').join('')+'</tbody></table>';
    if($('#redeem'))$('#redeem').onclick=async()=>{try{const n=await BACK.redeemCodes(ST.okCodes);toast(n+' codes marked as used');$('#redeem').remove();}catch(e){alert(niceErr(e));}};
    $('#dl').onclick=()=>{const csv='Student,Code,Stop,Status\n'+items.map(i=>[i.name,i.code,i.stop||'',lab[i.status][1]].map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(',')).join('\n');
      const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));a.download='calcgame-codes.csv';a.click();};
  };
  const readFile=f=>{const r=new FileReader();r.onload=()=>run(parseCSV(String(r.result)));r.readAsText(f);};
  $('#file').onchange=e=>{if(e.target.files[0])readFile(e.target.files[0]);};
  const d=$('#drop');d.ondragover=e=>{e.preventDefault();d.classList.add('over');};d.ondragleave=()=>d.classList.remove('over');
  d.ondrop=e=>{e.preventDefault();d.classList.remove('over');if(e.dataTransfer.files[0])readFile(e.dataTransfer.files[0]);};
  $('#check').onclick=()=>run([['name','code'],...$('#paste').value.split('\n').filter(l=>l.trim()).map(l=>{const m=l.match(CODE_RE)||[];return [l.replace(CODE_RE,'').replace(/[,;\t]+\s*$/,'').trim(),m.join(' ')];})]);
}

/* ---------- Classes ---------- */
function classes(){
  const count=id=>ST.students.filter(s=>s.class_id===id).length;
  const gen=()=>{const a='ABCDEFGHJKMNPQRSTUVWXYZ23456789';let s='';for(let i=0;i<6;i++)s+=a[Math.floor(Math.random()*a.length)];return s;};
  V().innerHTML='<section class="panel"><p class="tiny">Students need a class code to sign up. Make one class per section if you want separate leaderboards and due dates.</p>'+
    (ST.classes.length?'<table class="tbl"><thead><tr><th>Class</th><th>Code</th><th>Students'+(ST.cls?' (all classes)':'')+'</th><th>Made</th><th></th></tr></thead><tbody>'+ST.classes.map(c=>'<tr><td>'+esc(c.name)+'</td><td><code class="big">'+esc(c.code)+'</code></td><td>'+(ST.cls?'':count(c.id))+'</td><td>'+fmtDay(c.created_at)+'</td><td><button class="link danger" data-dc="'+c.id+'">Delete</button></td></tr>').join('')+'</tbody></table>':'<p class="empty">No classes yet.</p>')+
    '<h2>New class</h2><div class="row"><label>Name <input id="cn" placeholder="Calc 1, section 3"></label><label>Code <input id="cc" value="'+gen()+'" maxlength="12" style="width:9em;text-transform:uppercase"></label><button class="btn small" id="mk">Create</button></div></section>';
  $('#mk').onclick=async()=>{const name=$('#cn').value.trim(),code=$('#cc').value.trim().toUpperCase();
    if(!name)return alert('Give the class a name.');if(!/^[A-Z0-9]{4,12}$/.test(code))return alert('Codes are 4 to 12 letters or digits.');
    try{await BACK.createClass(name,code);toast('Class created');refresh();}catch(e){alert(niceErr(e));}};
  $$('[data-dc]').forEach(b=>b.onclick=async()=>{if(!confirm('Delete this class? Students stay, but lose their class (and leaderboard) until they rejoin.'))return;try{await BACK.deleteClass(b.dataset.dc);refresh();}catch(e){alert(niceErr(e));}});
}

/* ---------- Setup ---------- */
function setup(){
  V().innerHTML='<section class="panel"><h2>Server</h2><p>'+(BACK.kind==='mock'?'<b>Mock mode.</b> Everything is stored in this browser only, for trying things out.':'Connected to Supabase at <code>'+esc(CFG.supabaseUrl)+'</code>.')+'</p></section>'+
    '<section class="panel"><h2>What students’ accounts store</h2><ul><li>A username they made up, a password (stored hashed by Supabase), a class, and a character.</li><li>Their game progress, which questions they got right or wrong, and when they finished lessons, drill sets and stops.</li><li>Messages they send with “Feedback” or “I don’t understand”.</li></ul>'+
    '<p>No real names, emails or student IDs. The app asks students not to use their real names as usernames. If someone does, you can remove the account on the Students tab.</p>'+
    '<p>Suggested Canvas note: “This is an optional study tool I built. Using it is voluntary and does not affect your grade. It is hosted outside UVU and does not collect your name or email; please pick a username that is not your name. All course materials remain available in Canvas.”</p></section>'+
    '<section class="panel"><h2>Forgot passwords</h2><p>Students cannot reset passwords by email (there is no email). Use <b>Reset password</b> on the Students tab and tell them the new one in person.</p></section>';
}

/* ---------- start ---------- */
(async()=>{
  R.innerHTML='<p class="empty">Loading…</p>';
  try{await loadContent();}catch(e){}
  if(!BACK)return signInScreen();
  try{const uid=await BACK.init();if(uid)return enter();}catch(e){return signInScreen(niceErr(e));}
  signInScreen();
})();
