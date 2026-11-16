/* CalcGame code decoder (codes.html), for the instructor.
   Paste a Canvas quiz export (or any text with app codes in it); every code is read, checked and matched to a
   student number. Codes are cumulative, so a student's best result is the union of all their codes.
   Nothing here talks to a server: the pasted text, the roster and the stop choices are kept in this browser. */
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const LSK='calcgame.decoder.v1';
let WORLDS=[],STOPS=[],BYKEY={};
/* pick: {stop key: 1 = needs the before-class work, 2 = needs to be cleared} */
let ST={paste:'',roster:'',pick:{},sort:'done',dir:-1,open:'',names:true};
try{Object.assign(ST,JSON.parse(localStorage.getItem(LSK))||{});}catch(e){}
if(Array.isArray(ST.pick))ST.pick=Object.fromEntries(ST.pick.map(k=>[k,2]));
const NEED={1:'before-class work',2:'cleared'};
const keep=()=>{try{localStorage.setItem(LSK,JSON.stringify(ST));}catch(e){}};
const pad=n=>String(n).padStart(4,'0');

async function getJSON(p){const r=await fetch(p,{cache:'no-cache'});if(!r.ok)throw Error('Could not load '+p);return r.json();}
async function boot(){
  try{
    const idx=await getJSON('worlds.json');WORLDS=(await Promise.all(idx.worlds.map(getJSON))).sort((a,b)=>a.world-b.world);
    const reg=(await getJSON('stops.json')).v1;APPCODE.setRegistry(reg);
    STOPS=reg.map((key,i)=>{const [w,n]=key.split(':'),W=WORLDS.find(x=>x.id===w),N=W&&W.nodes.find(x=>x.id===n);
      return {key,i,wid:w,wnum:W?W.world:99,wtitle:W?W.title:w,title:N?N.title:n,kind:N?N.kind:'',live:!!(N&&N.deck)};});
    STOPS.forEach(s=>{BYKEY[s.key]=s;});
  }catch(e){$('#dec').innerHTML='<p class="verdict bad">'+esc(e.message)+'</p>';return;}
  shell();draw();
}

/* ---------- reading ---------- */
function roster(){
  const m=new Map();
  ST.roster.split(/\r?\n/).forEach(line=>{const k=/(^|\D)(\d{4})(?!\d)/.exec(line);if(!k)return;
    const name=line.replace(k[2],'').replace(/[,;\t]+/g,' ').replace(/\s+/g,' ').trim();m.set(+k[2],name);});
  return m;
}
function readAll(){
  const found=APPCODE.find(ST.paste),bad=[],by=new Map();let good=0;
  for(const raw of found){
    const r=APPCODE.decode(raw);
    if(!r.ok){const line=(ST.paste.split(/\r?\n/).find(l=>l.includes(raw))||'').replace(raw,'…').slice(0,60);bad.push({raw,why:r.why,line});continue;}
    good++;
    const s=by.get(r.sid)||{sid:r.sid,st:{},points:0,codes:0};
    for(const [k,v] of Object.entries(r.state))s.st[k]=Math.max(s.st[k]||0,v);
    s.points=Math.max(s.points,r.points);s.codes++;by.set(r.sid,s);
  }
  const R=roster();
  R.forEach((name,sid)=>{if(!by.has(sid))by.set(sid,{sid,st:{},points:0,codes:0});});
  const rows=[...by.values()].map(s=>{
    const pick=Object.keys(ST.pick).filter(k=>BYKEY[k]),has=k=>s.st[k]||0,keys=Object.keys(s.st);
    return Object.assign(s,{name:R.get(s.sid)||'',n:keys.filter(k=>s.st[k]===2).length,np:keys.filter(k=>s.st[k]===1).length,
      sel:pick.filter(k=>has(k)>=ST.pick[k]).length,selN:pick.length,miss:pick.filter(k=>has(k)<ST.pick[k]),
      worlds:WORLDS.map(w=>keys.filter(k=>s.st[k]===2&&k.startsWith(w.id+':')).length),
      wprep:WORLDS.map(w=>keys.filter(k=>s.st[k]===1&&k.startsWith(w.id+':')).length),unknown:R.size>0&&!R.has(s.sid)});
  });
  return {found:found.length,good,bad,rows};
}

/* ---------- layout ---------- */
function shell(){
  $('#dec').innerHTML=
    '<header class="dec-h"><h1>CalcGame <span>code decoder</span></h1><p class="tiny">Everything on this page stays in this browser. Nothing is uploaded.</p></header>'+
    '<section class="panel"><h2>1. Paste codes</h2><p class="tiny">Paste a Canvas quiz export (the Student Analysis CSV, opened in any app and copied), or codes one per line. Students can paste several codes over the term; each student gets everything any of their codes holds.</p>'+
      '<textarea id="paste" rows="7" spellcheck="false" placeholder="name,id,…,Enter your app code&#10;Jane Doe,…,K7Q2M-9XP4D-…">'+esc(ST.paste)+'</textarea>'+
      '<div class="row"><button class="btn" id="read">Read codes</button><button class="btn ghost" id="clr">Clear</button><span id="stat" class="tiny"></span></div><div id="bad"></div></section>'+
    '<div class="two">'+
      '<section class="panel"><h2>2. Roster <span class="tiny">optional</span></h2><p class="tiny">One student per line: the 4-digit number and a name, in any order. Students on the roster with no code show up as missing.</p>'+
        '<textarea id="roster" rows="6" spellcheck="false" placeholder="0423 Jane Doe&#10;1187, Sam Lee">'+esc(ST.roster)+'</textarea></section>'+
      '<section class="panel"><h2>3. Stops to check <span class="tiny" id="pickn"></span></h2><p class="tiny">Tap a stop once if its <b>before-class work</b> (lesson and theory) was due, twice if it had to be <b>cleared</b>, a third time to uncheck it. The table then shows who is done.</p><div id="pick"></div></section>'+
    '</div>'+
    '<section class="panel"><div class="ph"><h2>Students</h2><div class="row"><button class="btn small ghost" id="cp">Copy table</button><button class="btn small ghost" id="dl">Download CSV</button></div></div><div id="tbl"></div></section>'+
    '<div class="two">'+
      '<section class="panel"><div class="ph"><h2>Match Board leaderboard</h2><label class="tiny chk"><input type="checkbox" id="nm"'+(ST.names?' checked':'')+'> show names</label></div><div id="lb"></div></section>'+
      '<section class="panel"><h2>Make a code</h2><p class="tiny">For a student who lost everything, or to give credit by hand. The new code holds the stops checked in step 3 (before-class work or cleared, as marked there), plus everything in the starting code if you give one.</p>'+
        '<div class="mk"><label class="fld"><span>Student number</span><input id="mk-sid" inputmode="numeric" maxlength="4"></label><label class="fld"><span>Game points</span><input id="mk-pts" inputmode="numeric" value="0"></label></div>'+
        '<label class="fld"><span>Starting code (optional)</span><input id="mk-base" spellcheck="false"></label>'+
        '<div class="row"><button class="btn" id="mk">Make code</button></div><div id="mk-out"></div></section>'+
    '</div>';
  $('#read').onclick=()=>{ST.paste=$('#paste').value;keep();draw();};
  $('#clr').onclick=()=>{ST.paste='';$('#paste').value='';keep();draw();};
  $('#roster').oninput=e=>{ST.roster=e.target.value;keep();draw();};
  $('#nm').onchange=e=>{ST.names=e.target.checked;keep();draw();};
  $('#cp').onclick=copyTable;$('#dl').onclick=download;$('#mk').onclick=make;
  drawPick();
}
function drawPick(){
  const P=ST.pick,n=Object.keys(P).length;
  $('#pick').innerHTML=WORLDS.map(w=>{
    const ss=STOPS.filter(s=>s.wid===w.id&&s.live),on=ss.filter(s=>P[s.key]).length;
    return '<details class="pw"'+(on?' open':'')+'><summary><b>World '+w.world+'</b> '+esc(w.title)+' <span class="tiny">'+on+' of '+ss.length+'</span></summary>'+
      '<div class="row tiny">All: <button class="link" data-set="'+w.id+'" data-v="1">before class</button> · <button class="link" data-set="'+w.id+'" data-v="2">cleared</button> · <button class="link" data-set="'+w.id+'" data-v="0">none</button></div>'+
      '<div class="pl">'+ss.map(s=>{const v=P[s.key]||0;return '<button class="pk v'+v+'" data-k="'+esc(s.key)+'" aria-label="'+esc(s.title)+': '+(v?NEED[v]:'not checked')+'"><i>'+(v===2?'✓':v===1?'B':'')+'</i><span>'+esc(s.title)+(s.kind&&s.kind!=='main'?' <em>'+esc(s.kind)+'</em>':'')+'</span></button>';}).join('')+'</div></details>';
  }).join('')+'<p class="tiny pkey"><span class="pk v1"><i>B</i></span> before-class work due &nbsp; <span class="pk v2"><i>✓</i></span> must be cleared</p>';
  $('#pickn').textContent=n?n+' checked':'';
  const tidy=()=>{ST.pick=Object.fromEntries(STOPS.filter(s=>ST.pick[s.key]).map(s=>[s.key,ST.pick[s.key]]));keep();drawPick();draw();};
  $('#pick').onclick=e=>{
    const b=e.target.closest('[data-k]');
    if(b){const k=b.dataset.k,v=((ST.pick[k]||0)+1)%3;if(v)ST.pick[k]=v;else delete ST.pick[k];return tidy();}
    const a=e.target.closest('[data-set]');if(!a)return;const v=+a.dataset.v;
    STOPS.filter(s=>s.wid===a.dataset.set&&s.live).forEach(s=>{if(v)ST.pick[s.key]=v;else delete ST.pick[s.key];});tidy();
  };
}

/* ---------- results ---------- */
let LAST=null;
function sorted(rows){
  const k=ST.sort,d=ST.dir,val=r=>k==='name'?(r.name||'~').toLowerCase():k==='sid'?r.sid:k==='sel'?r.sel:k==='points'?r.points:k==='prep'?r.np:k[0]==='w'?r.worlds[+k.slice(1)]:r.n;
  return rows.slice().sort((a,b)=>{const x=val(a),y=val(b);return ((x<y?-1:x>y?1:0)*d)||(a.sid-b.sid);});
}
function draw(){
  const R=LAST=readAll(),total=STOPS.filter(s=>s.live).length;
  $('#stat').innerHTML=ST.paste.trim()?'<b>'+R.good+'</b> code'+(R.good===1?'':'s')+' read for <b>'+R.rows.filter(r=>r.codes).length+'</b> students'+(R.bad.length?' · <b class="badt">'+R.bad.length+' could not be read</b>':''):'';
  $('#bad').innerHTML=R.bad.length?'<details class="badl"><summary>Codes that could not be read</summary><ul>'+R.bad.map(b=>'<li><code>'+esc(b.raw)+'</code> '+esc(b.why)+(b.line?' <span class="tiny">From the line: '+esc(b.line)+'</span>':'')+'</li>').join('')+'</ul></details>':'';
  if(!R.rows.length){$('#tbl').innerHTML='<p class="empty tiny">No codes yet. Paste a Canvas export above and tap Read codes.</p>';$('#lb').innerHTML='';return;}
  const th=(k,t,cls)=>'<th class="'+(cls||'')+'"><button data-s="'+k+'">'+t+(ST.sort===k?(ST.dir<0?' ▾':' ▴'):'')+'</button></th>';
  const sel=Object.keys(ST.pick).length>0;
  let h='<div class="tw"><table class="tbl"><thead><tr>'+th('sid','#')+th('name','Name')+(sel?th('sel','Checked stops','num'):'')+th('done','Cleared','num')+th('prep','+ before class','num')+
    WORLDS.map((w,i)=>th('w'+i,'W'+w.world,'num w')).join('')+th('points','Points','num')+'</tr></thead><tbody>';
  for(const r of sorted(R.rows)){
    const full=sel&&r.sel===r.selN,none=!r.codes;
    h+='<tr class="'+(none?'nocode':'')+(ST.open===String(r.sid)?' open':'')+'" data-r="'+r.sid+'"><td class="mono">'+pad(r.sid)+'</td><td>'+esc(r.name)+(r.unknown?' <em class="tiny">not on roster</em>':'')+(none?' <em class="tiny">no code</em>':'')+'</td>'+
      (sel?'<td class="num"><span class="pill '+(full?'ok':r.sel?'mid':'no')+'">'+r.sel+' / '+r.selN+'</span></td>':'')+
      '<td class="num">'+r.n+' <span class="tiny">/ '+total+'</span></td><td class="num">'+(r.np?'+'+r.np:'<span class="tiny">0</span>')+'</td>'+r.worlds.map((n,i)=>'<td class="num w">'+(n||'<span class="tiny">0</span>')+(r.wprep[i]?'<span class="tiny"> +'+r.wprep[i]+'</span>':'')+'</td>').join('')+'<td class="num">'+r.points+'</td></tr>';
    if(ST.open===String(r.sid)){
      const list=v=>{const d=Object.keys(r.st).filter(k=>r.st[k]===v).map(k=>BYKEY[k]).filter(Boolean);
        return d.length?WORLDS.map(w=>{const x=d.filter(s=>s.wid===w.id);return x.length?'<span class="tiny">W'+w.world+'</span> '+x.map(s=>esc(s.title)).join(', '):'';}).filter(Boolean).join(' · '):'none';};
      h+='<tr class="det"><td colspan="'+(5+WORLDS.length+(sel?1:0))+'">'+
        (sel?'<p><b>Missing from the checked stops:</b> '+(r.miss.length?r.miss.map(k=>esc(BYKEY[k].title)+' <span class="tiny">(W'+BYKEY[k].wnum+', '+(ST.pick[k]===2&&r.st[k]===1?'before-class work done, not cleared':ST.pick[k]===2?'not cleared':'before-class work not done')+')</span>').join(', '):'none')+'</p>':'')+
        '<p><b>Cleared:</b> '+list(2)+'</p><p><b>Before-class work only:</b> '+list(1)+'</p>'+
        '<p class="tiny">'+r.codes+' code'+(r.codes===1?'':'s')+' read for this student.</p></td></tr>';
    }
  }
  $('#tbl').innerHTML=h+'</tbody></table></div>';
  $('#tbl').onclick=e=>{const b=e.target.closest('[data-s]');if(b){const k=b.dataset.s;if(ST.sort===k)ST.dir=-ST.dir;else{ST.sort=k;ST.dir=k==='name'||k==='sid'?1:-1;}keep();draw();return;}
    const tr=e.target.closest('tr[data-r]');if(tr){ST.open=ST.open===tr.dataset.r?'':tr.dataset.r;draw();}};
  const lb=R.rows.filter(r=>r.points>0).sort((a,b)=>b.points-a.points).slice(0,10);
  $('#lb').innerHTML=lb.length?'<ol class="lbl">'+lb.map(r=>'<li><span>'+esc(ST.names&&r.name?r.name:'#'+pad(r.sid))+'</span><b>'+r.points+'</b></li>').join('')+'</ol>':'<p class="tiny">No Match Board points yet.</p>';
}

/* ---------- out ---------- */
function tableRows(){
  const sel=Object.keys(ST.pick).length>0,head=['Student number','Name'].concat(sel?['Checked stops done','Checked stops total']:[],['Stops cleared','Before-class work only'],WORLDS.map(w=>'World '+w.world+' cleared'),['Game points','Missing checked stops']);
  return [head].concat(sorted(LAST.rows).map(r=>[pad(r.sid),r.name].concat(sel?[r.sel,r.selN]:[],[r.n,r.np],r.worlds,[r.points,r.miss.map(k=>BYKEY[k].title).join('; ')])));
}
async function copyTable(){
  if(!LAST||!LAST.rows.length)return;
  const t=tableRows().map(r=>r.join('\t')).join('\n'),b=$('#cp');
  try{await navigator.clipboard.writeText(t);b.textContent='Copied ✓';}catch(e){b.textContent='Copy failed';}
  setTimeout(()=>{b.textContent='Copy table';},1600);
}
function download(){
  if(!LAST||!LAST.rows.length)return;
  const q=v=>{v=String(v);return /[",\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v;};
  const csv=tableRows().map(r=>r.map(q).join(',')).join('\r\n');
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));
  a.download='calcgame-codes-'+new Date().toISOString().slice(0,10)+'.csv';document.body.appendChild(a);a.click();a.remove();
}
function make(){
  const out=$('#mk-out'),sid=$('#mk-sid').value.trim(),say=(ok,t)=>{out.innerHTML='<div class="fb '+(ok?'good':'bad')+'"><span>'+t+'</span></div>';};
  if(!/^\d{4}$/.test(sid))return say(false,'The student number must be 4 digits.');
  const st=Object.assign({},ST.pick);let pts=Math.max(0,parseInt($('#mk-pts').value,10)||0);
  const base=$('#mk-base').value.trim();
  if(base){const r=APPCODE.decode(base);if(!r.ok)return say(false,'Starting code: '+esc(r.why));
    if(r.sid!==+sid)return say(false,'The starting code belongs to student '+r.sidText+'.');for(const [k,v] of Object.entries(r.state))st[k]=Math.max(st[k]||0,v);pts=Math.max(pts,r.points);}
  const code=APPCODE.encode({sid:+sid,points:pts,state:st}),nv=v=>Object.values(st).filter(x=>x===v).length;
  say(true,'<span class="mono big">'+code+'</span><br><span class="tiny">'+nv(2)+' cleared, '+nv(1)+' with before-class work, '+(Math.floor(pts/10)*10)+' points. The student enters it under App code → Restore from a code.</span>');
}
boot();
