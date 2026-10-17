/* CalcGame engine. All course content lives in map.json and decks/*.json.
   Nothing in this file needs to change when you add or edit a stop. */

/* Game rules, all in one place so they are easy to tune. */
const RULES={streak:5,setSize:8,masterAt:2,dailyPlays:5,misses:3,pairPts:10,clearPts:50,walkSpeed:55};

/* ---------- small helpers ---------- */
const $=(s,r=document)=>r.querySelector(s);
const app=$('#app');
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const neg=s=>String(s).replace(/-/g,'−');
function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function mpart(t){
  return esc(t).replace(/-&gt;/g,'→').replace(/&lt;=/g,'≤').replace(/&gt;=/g,'≥').replace(/!=/g,'≠')
    .replace(/\^([+-])(?![A-Za-z0-9.])/g,(_,c)=>'<sup>'+(c==='-'?'−':'+')+'</sup>')
    .replace(/\^\(([^)]*)\)|\^([+-]?[A-Za-z0-9.]+)/g,(_,a,b)=>'<sup>'+(a!=null?a:b)+'</sup>')
    .replace(/_\(([^)]*)\)|_([A-Za-z0-9]+)/g,(_,a,b)=>'<sub>'+(a!=null?a:b)+'</sub>')
    .replace(/-/g,'−').replace(/\bpi\b/g,'π').replace(/\binfty\b/g,'∞').replace(/\bsqrt\b/g,'√')
    .replace(/[A-Za-z]+/g,w=>w.length===1?'<i>'+w+'</i>':w);
}
function math(m){
  return '<span class="math">'+m.split(/(lim\[[^\]]*\]|frac\{[^{}]*\}\{[^{}]*\})/).map(t=>{const k=/^lim\[(.*)\]$/.exec(t),f=/^frac\{([^{}]*)\}\{([^{}]*)\}$/.exec(t);
    if(f)return '<span class="frac"><span>'+mpart(f[1])+'</span><span>'+mpart(f[2])+'</span></span>';
    return k?'<span class="lim"><span>lim</span><span class="lim-s">'+mpart(k[1])+'</span></span>':mpart(t);}).join('')+'</span>';
}
function fmt(s){
  return String(s).split('$').map((t,i)=>i%2?math(t):esc(t).replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/\n/g,'<br>')).join('');
}

/* ---------- expression parser (no eval) ---------- */
const FN={sin:Math.sin,cos:Math.cos,tan:Math.tan,sqrt:Math.sqrt,abs:Math.abs,exp:Math.exp,ln:Math.log,cbrt:Math.cbrt};
/* a^b, with real roots of negative numbers when b = p/q and q is odd (so x^(3/5) works for x < 0) */
function rpow(a,b){
  if(a>=0||Number.isInteger(b))return Math.pow(a,b);
  for(let q=1;q<=15;q++){const p=b*q; if(Math.abs(p-Math.round(p))<1e-9){return q%2?(Math.round(p)%2?-1:1)*Math.pow(-a,b):NaN;}}
  return NaN;
}
function compile(src){
  const s=String(src).replace(/\s+/g,''); let i=0;
  const expr=()=>{let a=term();while(s[i]==='+'||s[i]==='-'){const op=s[i++],l=a,r=term();a=op==='+'?x=>l(x)+r(x):x=>l(x)-r(x);}return a;};
  const term=()=>{let a=unary();while(s[i]==='*'||s[i]==='/'){const op=s[i++],l=a,r=unary();a=op==='*'?x=>l(x)*r(x):x=>l(x)/r(x);}return a;};
  const unary=()=>{if(s[i]==='-'){i++;const a=unary();return x=>-a(x);}return power();};
  const power=()=>{const a=atom();if(s[i]==='^'){i++;const b=unary();return x=>rpow(a(x),b(x));}return a;};
  const atom=()=>{
    if(s[i]==='('){i++;const a=expr();if(s[i]!==')')throw Error('missing )');i++;return a;}
    const num=/^\d*\.?\d+/.exec(s.slice(i));
    if(num){i+=num[0].length;const v=+num[0];return()=>v;}
    const id=/^[a-z]+/.exec(s.slice(i));
    if(id){i+=id[0].length;const n=id[0];
      if(n==='x')return x=>x; if(n==='pi')return()=>Math.PI;
      if(FN[n]){if(s[i]!=='(')throw Error(n+' needs ( )');i++;const a=expr();if(s[i]!==')')throw Error('missing )');i++;return x=>FN[n](a(x));}
      throw Error('unknown name "'+n+'"');}
    throw Error(i<s.length?'unexpected "'+s[i]+'" (write 2*x, not 2x)':'expression ends early');
  };
  const f=expr(); if(i<s.length)throw Error('unexpected "'+s[i]+'" (write 2*x, not 2x)'); return f;
}
const cache={};
const fn=e=>cache[e]||(cache[e]=compile(e));

/* ---------- graph maths (also used by the deck test) ---------- */
function valueAt(g,a){
  const d=(g.dots||[]).find(p=>p[0]===a); if(d)return d[1];
  if((g.holes||[]).some(p=>p[0]===a))return null;
  const p=g.pieces.find(p=>p.from<=a&&a<=p.to); return p?fn(p.expr)(a):null;
}
function sideLimit(g,a,dir){
  const p=g.pieces.find(p=>dir<0?(p.from<a&&a<=p.to):(p.from<=a&&a<p.to)); if(!p)return null;
  const v=fn(p.expr)(a+dir*1e-6); return Number.isFinite(v)&&Math.abs(v)<1e4?v:null;
}
const EXTASK=['absmax','absmin','argmax','argmin'];
/* Reads the highest or lowest point off a graph the way a student would. 'NONE' when it is never reached. */
function extTruth(g,q){
  const want=/max$/.test(q.ask)?1:-1,[,,y0,y1]=g.window,holes=g.holes||[],dots=g.dots||[],pts=[];
  let step=0;
  for(const p of g.pieces||[]){
    const f=fn(p.expr),N=2000; step=Math.max(step,(p.to-p.from)/N);
    for(let k=0;k<=N;k++){
      const x=p.from+(p.to-p.from)*k/N; if(holes.some(h=>Math.abs(h[0]-x)<1e-9))continue;
      const d=dots.find(d=>Math.abs(d[0]-x)<1e-9),y=d?d[1]:f(x); if(!Number.isFinite(y))continue;
      pts.push({x,y,open:(k===0&&/L/.test(p.arrow||''))||(k===N&&/R/.test(p.arrow||''))});
    }
  }
  dots.forEach(d=>pts.push({x:d[0],y:d[1],open:false}));
  if(!pts.length)return 'NONE';
  let b=pts[0]; pts.forEach(t=>{if(want*(t.y-b.y)>1e-9)b=t;});
  if(b.open||b.y>y1+1e-9||b.y<y0-1e-9||holes.some(h=>Math.abs(h[0]-b.x)<=step*1.5))return 'NONE';
  if(q.ask==='absmax'||q.ask==='absmin')return b.y;
  const xs=[]; pts.forEach(t=>{if(Math.abs(t.y-b.y)<1e-5&&!xs.some(v=>Math.abs(v-t.x)<0.05))xs.push(t.x);});
  return xs.length>1?'MULTI':b.x;
}
function truth(g,q){
  if(EXTASK.includes(q.ask))return extTruth(g,q);
  if(q.ask==='value'){const v=valueAt(g,q.at);return v==null?'UND':v;}
  const L=sideLimit(g,q.at,-1),R=sideLimit(g,q.at,1);
  if(q.side==='left')return L==null?'DNE':L;
  if(q.side==='right')return R==null?'DNE':R;
  return L!=null&&R!=null&&Math.abs(L-R)<1e-3?(L+R)/2:'DNE';
}
function evalAt(g,x){
  const sp=[...(g.holes||[]),...(g.dots||[])].find(p=>Math.abs(p[0]-x)<0.005); if(sp)return valueAt(g,sp[0]);
  const p=g.pieces.find(p=>p.from<=x&&x<=p.to); return p?fn(p.expr)(x):null;
}

/* ---------- graph drawing ---------- */
let plotN=0;
function plot(g,marker){
  const [x0,x1,y0,y1]=g.window,m=14,W=320,u=(W-2*m)/(x1-x0);
  /* keep the picture a sensible shape: squares unless that would make it very tall or very flat */
  const nat=2*m+u*(y1-y0),H=Math.min(Math.max(nat,0.62*W),1.25*W),uy=(H-2*m)/(y1-y0);
  /* autoTicks: 1-2-5 spacing at any scale, for zoomed-in pictures */
  const nice=g.autoTicks?n=>{const raw=n/6,p=Math.pow(10,Math.floor(Math.log10(raw))),f=raw/p;return (f<1.5?1:f<3.5?2:f<7.5?5:10)*p;}
    :n=>n<=9?1:n<=18?2:n<=45?5:n<=90?10:n<=180?20:50,tx=g.xstep||nice(x1-x0),ty=g.ystep||nice(y1-y0);
  const xt=[],yt=[],rt=v=>Math.round(v*1e6)/1e6;
  for(let k=Math.ceil(x0/tx-1e-9);k*tx<=x1+1e-9;k++)if(k!==0)xt.push(rt(k*tx));
  for(let k=Math.ceil(y0/ty-1e-9);k*ty<=y1+1e-9;k++)if(k!==0)yt.push(rt(k*ty));
  const sx=x=>m+(x-x0)*u,sy=y=>m+(y1-y)*uy,r=n=>Math.round(n*10)/10;
  const ax=Math.min(Math.max(0,x0),x1),ay=Math.min(Math.max(0,y0),y1);
  let s='<svg class="graph" viewBox="0 0 '+W+' '+r(H)+'" role="img" aria-label="Graph of the function f"><rect class="g-bg" x="'+m+'" y="'+m+'" width="'+(W-2*m)+'" height="'+r(H-2*m)+'"/>';
  xt.forEach(x=>{s+='<line class="g-grid" x1="'+r(sx(x))+'" x2="'+r(sx(x))+'" y1="'+m+'" y2="'+r(H-m)+'"/>';});
  yt.forEach(y=>{s+='<line class="g-grid" x1="'+m+'" x2="'+(W-m)+'" y1="'+r(sy(y))+'" y2="'+r(sy(y))+'"/>';});
  s+='<line class="g-axis" x1="'+r(sx(ax))+'" x2="'+r(sx(ax))+'" y1="'+m+'" y2="'+r(H-m)+'"/><line class="g-axis" x1="'+m+'" x2="'+(W-m)+'" y1="'+r(sy(ay))+'" y2="'+r(sy(ay))+'"/>';
  xt.forEach(x=>{s+='<text class="g-t" text-anchor="middle" x="'+r(sx(x))+'" y="'+r(sy(ay)+11)+'">'+neg(x)+'</text>';});
  yt.forEach(y=>{s+='<text class="g-t" text-anchor="end" x="'+r(sx(ax)-4)+'" y="'+r(sy(y)+3.5)+'">'+neg(y)+'</text>';});
  for(const v of g.vlines||[])s+='<line class="g-vline" x1="'+r(sx(v))+'" x2="'+r(sx(v))+'" y1="'+m+'" y2="'+r(H-m)+'"/>';
  for(const p of g.pieces||[]){
    let f; try{f=fn(p.expr);}catch(e){continue;}
    let d='',pen=false; const N=96;
    for(let k=0;k<=N;k++){const x=p.from+(p.to-p.from)*k/N,y=f(x);
      if(Number.isFinite(y)&&y>=y0-0.5&&y<=y1+0.5){d+=(pen?'L':'M')+r(sx(x))+' '+r(sy(y));pen=true;}else pen=false;}
    s+='<path class="g-curve" d="'+d+'"/>';
    for(const end of ['L','R'])if((p.arrow||'').includes(end)){
      const xe=end==='L'?p.from:p.to,dx=(end==='L'?1:-1)*(p.to-p.from)*0.01,ye=f(xe),yi=f(xe+dx);
      if(!Number.isFinite(ye)||!Number.isFinite(yi)||ye<y0||ye>y1)continue;
      const ex=sx(xe),ey=sy(ye),vx=ex-sx(xe+dx),vy=ey-sy(yi),n=Math.hypot(vx,vy)||1,ux=vx/n,uy=vy/n;
      s+='<polygon class="g-arrow" points="'+r(ex+ux*5)+','+r(ey+uy*5)+' '+r(ex-ux*5-uy*4.2)+','+r(ey-uy*5+ux*4.2)+' '+r(ex-ux*5+uy*4.2)+','+r(ey-uy*5-ux*4.2)+'"/>';
    }
  }
  const clip='pc'+(++plotN);
  s+='<clipPath id="'+clip+'"><rect x="'+m+'" y="'+m+'" width="'+(W-2*m)+'" height="'+r(H-2*m)+'"/></clipPath>';
  /* tangents: x-values where the tangent to the first piece is drawn, with a dashed drop to the axis */
  for(const t of g.tangents||[]){
    let F; try{F=fn(g.pieces[0].expr);}catch(e){continue;}
    const y=F(t),d=numDeriv(F,t); if(!Number.isFinite(y)||!Number.isFinite(d))continue;
    s+='<g clip-path="url(#'+clip+')"><line class="g-tan" x1="'+r(sx(x0))+'" y1="'+r(sy(y+d*(x0-t)))+'" x2="'+r(sx(x1))+'" y2="'+r(sy(y+d*(x1-t)))+'"/>'+
      '<line class="g-guide" x1="'+r(sx(t))+'" x2="'+r(sx(t))+'" y1="'+r(sy(ay))+'" y2="'+r(sy(y))+'"/></g>';
  }
  for(const [x,y] of g.holes||[])s+='<circle class="g-hole" cx="'+r(sx(x))+'" cy="'+r(sy(y))+'" r="4.4"/>';
  for(const [x,y] of g.dots||[])s+='<circle class="g-dot" cx="'+r(sx(x))+'" cy="'+r(sy(y))+'" r="4.8"/>';
  /* labels: [x, y, "text"]; text is placed just above the point */
  for(const [x,y,t] of g.labels||[])s+='<text class="g-lab" text-anchor="middle" x="'+r(sx(x))+'" y="'+r(sy(y)-7)+'">'+esc(t)+'</text>';
  if(marker)s+='<path class="g-guide mk-g" d=""/><circle class="g-mk mk-d" cx="-20" cy="-20" r="5.5"/>';
  return {svg:s+'</svg>',sx,sy,ax,ay,clip};
}


/* ---------- content loading ---------- */
let MAP=null,DECK=null,WORLDS=[]; const DECKS={};
async function getJSON(path){
  const r=await fetch(path,{cache:'no-cache'}); if(!r.ok)throw Error('Could not load '+path+' ('+r.status+')');
  const t=await r.text(); try{return JSON.parse(t);}catch(e){throw Error(path+' is not valid JSON: '+e.message);}
}
const nodeById=id=>MAP.nodes.find(n=>n.id===id);

/* ---------- saved progress (this browser only for now) ---------- */
const KEY='calcgame.v1';
const fresh=()=>({world:'',pos:{},decks:{},streak:0,plays:0,points:0,day:'',playsToday:0,setDay:{},game:null,preview:false});
let S=fresh();
try{const raw=localStorage.getItem(KEY); if(raw)S=Object.assign(fresh(),JSON.parse(raw));}catch(e){}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(S));}catch(e){}};
const today=()=>{const d=new Date();return d.getFullYear()+'-'+(d.getMonth()+1)+'-'+d.getDate();};
function rollDay(){if(S.day!==today()){S.day=today();S.playsToday=0;}}
function awardPlay(){rollDay();if(S.playsToday>=RULES.dailyPlays)return false;S.plays++;S.playsToday++;return true;}
const ds=id=>S.decks[id]||(S.decks[id]={lessonAt:0,lessonDone:false,q:{},sets:{}});
const isMastered=q=>((ds(DECK.id).q[q.id]||{}).right||0)>=RULES.masterAt;
const drillKinds=d=>Object.keys(d.drills||{});

/* A stop is cleared when its lesson is finished and one set of each drill is done. */
function deckCleared(d){
  if(!d||d.error)return false; const p=ds(d.id);
  return (!d.lesson||p.lessonDone)&&drillKinds(d).every(k=>(p.sets[k]||0)>0);
}
function nodeCleared(n){return n.kind==='start'||(!!n.deck&&deckCleared(DECKS[n.deck]));}
function nodeOpen(n){return S.preview||(n.requires||[]).every(id=>{const r=nodeById(id);return r&&nodeCleared(r);});}

/* A correct answer builds the streak only on questions not yet mastered. */
function record(q,ok){
  if(S.preview)return 'Preview mode: not recorded.';
  const all=ds(DECK.id).q,r=all[q.id]||(all[q.id]={right:0,wrong:0}),was=r.right>=RULES.masterAt; let note='';
  if(ok){r.right++;
    if(was)note='You have already mastered this one, so it does not add to your streak.';
    else{S.streak++; if(S.streak>=RULES.streak){S.streak=0; note=awardPlay()?'Streak complete. You earned a game play!':'Streak complete, but you have reached today’s limit of '+RULES.dailyPlays+' plays.';}}
  }else{r.wrong++; if(S.streak>0)note='Streak reset.'; S.streak=0;}
  save(); return note;
}

/* ---------- screen plumbing ---------- */
let keyHook=null,itemKeys=null;
document.addEventListener('keydown',e=>{if(keyHook)keyHook(e);});
app.addEventListener('click',e=>{
  const w=e.target.closest('[data-world]');
  if(w){const m=WORLDS.find(x=>x.id===w.dataset.world);if(m&&m!==MAP&&!walking){MAP=m;S.world=m.id;save();home();window.scrollTo(0,0);}return;}
  const b=e.target.closest('[data-go]');if(b&&!b.disabled)go(b.dataset.go);});
function screen(p){
  keyHook=null;itemKeys=null;
  app.innerHTML=(p.top||'')+'<main class="body">'+(p.body||'')+'</main>'+(p.foot?'<footer class="foot">'+p.foot+'</footer>':'');
}
const bar=(label,prog,right)=>'<header class="bar"><button class="x" data-go="home" aria-label="Back to the map">←</button><div class="bar-mid"><span class="bar-l">'+label+'</span>'+(prog!=null?'<div class="prog"><i style="width:'+prog+'%"></i></div>':'')+'</div>'+(right||'')+'</header>';
const pips=()=>'<div class="streak" role="img" aria-label="Streak '+S.streak+' of '+RULES.streak+'">'+Array.from({length:RULES.streak},(_,k)=>'<i class="'+(k<S.streak?'on':'')+'"></i>').join('')+'</div>';
function toast(m){const t=document.createElement('div');t.className='toast';t.setAttribute('role','status');t.textContent=m;app.appendChild(t);setTimeout(()=>t.remove(),2600);}
function feedback(el,ok,msg,note){
  el.hidden=false;el.className='fb '+(ok?'good':'bad');
  el.innerHTML='<strong>'+(ok?'✓ Correct':'✗ Not quite')+'</strong>'+(msg?'<span>'+fmt(msg)+'</span>':'')+(note?'<em>'+esc(note)+'</em>':'');
  el.scrollIntoView({block:'nearest'});
}
function enterKey(btn){
  keyHook=e=>{
    if(e.key==='Enter'){if(!e.target.closest('button')&&!btn.disabled){btn.click();e.preventDefault();}}
    else if(itemKeys)itemKeys(e);
  };
}
function go(name){
  if(name.indexOf('drill:')===0)return drill(name.slice(6));
  ({home,lesson,game,test}[name]||home)();
}

/* ---------- item players: one per item type ---------- */
function mountItem(it,host,onChange){
  let h='';
  if(it.title)h+='<h2>'+fmt(it.title)+'</h2>';
  const text=it.text||(it.type==='graph'?'Use the graph of $f$.':'');
  if(text&&it.type!=='bank')h+='<p class="txt">'+fmt(text)+'</p>';
  if(it.show&&it.fn)h+='<div class="gwrap">'+plot(autoGraph(it.fn),false).svg+'</div>';
  if(it.graph&&DECK.graphs[it.graph])h+='<div class="gwrap">'+plot(DECK.graphs[it.graph],it.type==='explore').svg+'</div>';
  host.innerHTML=h+'<div class="ix"></div>';
  const M={info:()=>({kind:'pass',canGo:()=>true}),explore:mountExplore,graph:mountGraphQ,mc:mountMC,tf:mountMC,bank:mountBank,num:mountNum,crit:mountCrit,extrema:mountExtrema,multi:mountMulti,newton:mountNewton,bisect:mountBisect}[it.type];
  return M(it,$('.ix',host),onChange,host);
}
function answerLabel(q){
  if(q.ask==='absmax')return 'Absolute maximum =';
  if(q.ask==='absmin')return 'Absolute minimum =';
  if(q.ask==='argmax')return 'The maximum occurs at $x$ =';
  if(q.ask==='argmin')return 'The minimum occurs at $x$ =';
  if(q.ask==='value')return '$f('+q.at+')$ =';
  return '$lim[x->'+q.at+(q.side==='left'?'^-':q.side==='right'?'^+':'')+'] f(x)$ =';
}
function answerText(q){
  if(q.type==='graph')return typeof q.answer==='string'?(q.answer==='UND'?'undefined':q.answer==='NONE'?'none (there is no such point)':'DNE'):neg(q.answer);
  if(q.type==='num')return neg(q.answer);
  if(q.type==='multi')return q.fails?(q.failText||'Newton’s method breaks down here'):q.parts.map(p=>p.label+' '+neg(+p.answer.toFixed(4))).join(', ');
  if(q.type==='crit')return q.answers.length?q.answers.map(neg).join(', '):'no critical numbers';
  if(q.type==='mc')return q.options[q.answer];
  if(q.type==='tf')return q.answer?'True':'False';
  return q.blanks.join(', ');
}
function mountGraphQ(q,ix,onChange){
  const ext=EXTASK.includes(q.ask),sp=ext?'NONE':q.ask==='value'?'UND':'DNE',spWord=ext?'None':q.ask==='value'?'Undefined':'DNE'; let val='',locked=false;
  ix.innerHTML='<div class="ans"><span>'+fmt(answerLabel(q))+'</span><output class="ans-box empty" aria-live="polite">?</output></div>'+
    padHTML('<button class="key wide sp" data-k="'+sp+'" aria-pressed="false">'+spWord+'</button>');
  const box=$('.ans-box',ix),spB=$('.sp',ix);
  const show=()=>{box.textContent=val===sp?spWord:(val===''?'?':neg(val));box.classList.toggle('empty',val==='');spB.setAttribute('aria-pressed',val===sp);};
  const press=k=>{
    if(locked)return;
    if(k==='back')val=val===sp?'':val.slice(0,-1);
    else if(k===sp)val=val===sp?'':sp;
    else{ if(val===sp)val=''; val=editVal(val,k,6); }
    show();onChange();
  };
  ix.addEventListener('click',e=>{const b=e.target.closest('.key');if(b)press(b.dataset.k);});
  itemKeys=padKeys(press);
  return {kind:'q',
    canGo:()=>val===sp||!Number.isNaN(parseVal(val)),
    check:()=>typeof q.answer==='string'?val===q.answer:(val!==sp&&Math.abs(parseVal(val)-q.answer)<=(q.tol==null?0.01:q.tol)),
    lock(reveal,ok){locked=true;box.classList.add(ok?'is-right':'is-wrong');},
    reset(){locked=false;val='';box.classList.remove('is-right','is-wrong');show();onChange();}};
}
function mountMC(it,ix,onChange){
  const opts=it.type==='tf'?['True','False']:it.options,right=it.type==='tf'?(it.answer?0:1):it.answer; let sel=-1,locked=false;
  ix.innerHTML='<div class="opts '+it.type+'">'+opts.map((o,i)=>'<button class="opt" data-i="'+i+'" aria-pressed="false">'+fmt(o)+'</button>').join('')+'</div>';
  const all=()=>ix.querySelectorAll('.opt');
  ix.addEventListener('click',e=>{const b=e.target.closest('.opt');if(!b||locked)return;sel=+b.dataset.i;all().forEach((x,i)=>x.setAttribute('aria-pressed',i===sel));onChange();});
  return {kind:'q',canGo:()=>sel>=0,check:()=>sel===right,
    lock(reveal){locked=true;all().forEach((x,i)=>{x.disabled=true;if(i===sel)x.classList.add(sel===right?'is-right':'is-wrong');else if(reveal&&i===right)x.classList.add('is-right');});},
    reset(){locked=false;sel=-1;all().forEach(x=>{x.disabled=false;x.className='opt';x.setAttribute('aria-pressed','false');});onChange();}};
}
function mountBank(it,ix,onChange){
  const parts=it.text.split('___'),n=it.blanks.length,chips=shuffle([...it.blanks,...(it.distractors||[])]);
  let fill=Array(n).fill(null),locked=false,marks=null;
  const draw=()=>{
    ix.innerHTML='<p class="txt bank-t">'+parts.map((p,i)=>fmt(p)+(i<n?'<button class="blank'+(marks?(marks[i]?' is-right':' is-wrong'):'')+'" data-b="'+i+'" aria-label="Blank '+(i+1)+'">'+(fill[i]!=null?esc(chips[fill[i]]):'&nbsp;')+'</button>':'')).join('')+
      '</p><div class="chips">'+chips.map((c,i)=>'<button class="chip" data-c="'+i+'"'+(fill.includes(i)||locked?' disabled':'')+'>'+esc(c)+'</button>').join('')+'</div>';
  };
  ix.addEventListener('click',e=>{
    if(locked)return;
    const c=e.target.closest('.chip'),b=e.target.closest('.blank');
    if(c){const slot=fill.indexOf(null);if(slot<0)return;fill[slot]=+c.dataset.c;}
    else if(b)fill[+b.dataset.b]=null; else return;
    draw();onChange();
  });
  draw();
  const got=i=>fill[i]!=null&&chips[fill[i]]===it.blanks[i];
  return {kind:'q',canGo:()=>!fill.includes(null),check:()=>it.blanks.every((_,i)=>got(i)),
    lock(){locked=true;marks=it.blanks.map((_,i)=>got(i));draw();},
    reset(){locked=false;marks=null;fill=Array(n).fill(null);draw();onChange();}};
}
function mountExplore(sl,ix,onChange,host){
  const g=DECK.graphs[sl.graph],P=plot(g,true),a=sl.target.at,w=sl.target.within==null?0.15:sl.target.within,[x0,x1]=g.window;
  let L=false,R=false;
  ix.innerHTML='<label class="slide-l" for="xs">Drag to move along the graph</label><input type="range" id="xs" min="'+x0+'" max="'+x1+'" step="0.01" value="'+(sl.start==null?x0+0.4:sl.start)+'">'+
    '<div class="read"><span>'+fmt('$x$ =')+' <b id="rx"></b></span><span>'+fmt('$f(x)$ =')+' <b id="rf"></b></span></div>'+
    '<div class="goals"><span class="goal" id="gl">Close from the left</span><span class="goal" id="gr">Close from the right</span></div><div class="fb good" id="after" hidden></div>';
  const xs=$('#xs',ix),dot=$('.mk-d',host),guide=$('.mk-g',host);
  const up=()=>{
    const x=+xs.value,y=evalAt(g,x);
    $('#rx',ix).textContent=neg(x.toFixed(2));$('#rf',ix).textContent=y==null?'undefined':neg(y.toFixed(2));
    if(y==null){dot.setAttribute('cx',-20);guide.setAttribute('d','');}
    else{const px=P.sx(x),py=P.sy(y);dot.setAttribute('cx',px);dot.setAttribute('cy',py);
      guide.setAttribute('d','M'+px+' '+P.sy(P.ay)+'L'+px+' '+py+'L'+P.sx(P.ax)+' '+py);}
    if(x<a-0.004&&x>=a-w-1e-9)L=true; if(x>a+0.004&&x<=a+w+1e-9)R=true;
    $('#gl',ix).classList.toggle('on',L);$('#gr',ix).classList.toggle('on',R);
    if(L&&R&&sl.after){const af=$('#after',ix);if(af.hidden){af.hidden=false;af.innerHTML="<span>"+fmt(sl.after)+"</span>";af.scrollIntoView({block:"nearest"});}}
    onChange();
  };
  xs.addEventListener('input',up);up();
  return {kind:'pass',canGo:()=>L&&R};
}


/* ---------- number pad shared by the typed-answer items ---------- */
/* answers may be typed as decimals or fractions such as 7/4 or -1/3 */
function parseVal(s){
  s=String(s); if(!/\d/.test(s))return NaN;
  if(s.includes('/')){const [a,b]=s.split('/'),n=parseFloat(a),d=parseFloat(b);return Number.isFinite(n)&&Number.isFinite(d)&&d!==0?n/d:NaN;}
  return parseFloat(s);
}
function editVal(val,k,max){
  if(k==='clear')return ''; if(k==='back')return val.slice(0,-1);
  if(k==='-')return val[0]==='-'?val.slice(1):'-'+val;
  const tail=val.split('/').pop();
  if(k==='.')return tail.includes('.')?val:val+(tail===''||tail==='-'?'0.':'.');
  if(k==='/')return val.includes('/')||!/\d$/.test(val)?val:val+'/';
  return val.replace(/\D/g,'').length<(max||9)?val+k:val;
}
const PADKEYS=['7','8','9','back','4','5','6','-','1','2','3','.','0','/'];
const padHTML=last=>'<div class="pad">'+PADKEYS.map(k=>'<button class="key" data-k="'+k+'"'+(k==='back'?' aria-label="Delete"':k==='-'?' aria-label="Negative sign"':k==='/'?' aria-label="Fraction bar"':'')+'>'+(k==='back'?'⌫':k==='-'?'−':k==='/'?'a/b':k)+'</button>').join('')+last+'</div>';
const padKeys=press=>e=>{
  if(/^[0-9]$/.test(e.key))press(e.key); else if(e.key==='-'||e.key==='.'||e.key==='/')press(e.key);
  else if(e.key==='Backspace')press('back'); else return false; e.preventDefault(); return true;
};
function makePad(ix,o){
  let val='',locked=false;
  ix.innerHTML='<div class="ans"><span>'+fmt(o.label||'Answer =')+'</span><output class="ans-box empty" aria-live="polite">?</output></div>'+
    padHTML(o.extra?'<button class="key wide sp" data-k="extra">'+esc(o.extra)+'</button>':'<button class="key wide" data-k="clear">Clear</button>');
  const box=$('.ans-box',ix),show=()=>{box.textContent=val===''?'?':neg(val);box.classList.toggle('empty',val==='');};
  const press=k=>{
    if(locked)return;
    if(k==='extra'){o.onExtra&&o.onExtra();return;}
    val=editVal(val,k); show();o.onChange&&o.onChange();
  };
  ix.addEventListener('click',e=>{const b=e.target.closest('.key');if(b)press(b.dataset.k);});
  itemKeys=padKeys(press);
  return {get:()=>val,num:()=>parseVal(val),clear(){val='';show();},
    lock(ok){locked=true;box.classList.add(ok?'is-right':'is-wrong');},
    reset(){locked=false;val='';box.classList.remove('is-right','is-wrong');show();}};
}
function mountNum(q,ix,onChange){
  const P=makePad(ix,{label:q.label||'Answer =',onChange});
  return {kind:'q',canGo:()=>!Number.isNaN(P.num()),check:()=>Math.abs(P.num()-q.answer)<=(q.tol==null?0.01:q.tol),
    lock(reveal,ok){P.lock(ok);},reset(){P.reset();onChange();}};
}
/* enter every critical number: type one, tap Add; tap a chip to remove it */
function critWidget(ix,o){
  let vals=[],none=false,locked=false; const pad=document.createElement('div'),list=document.createElement('div');
  ix.appendChild(pad); ix.appendChild(list);
  const P=makePad(pad,{label:o.label||'$x$ =',extra:'Add to list',onChange:()=>{upd();o.onChange&&o.onChange();},onExtra:add});
  function add(){const v=P.num(); if(locked||Number.isNaN(v))return; if(!vals.some(w=>Math.abs(w-v)<1e-9))vals.push(v); none=false; P.clear(); draw(); o.onChange&&o.onChange();}
  const upd=()=>{};
  function draw(){
    list.className='critlist';
    list.innerHTML='<p class="tiny">'+(vals.length?'Your list (tap one to remove it):':'Your list is empty.')+'</p><div class="chips">'+
      vals.slice().sort((a,b)=>a-b).map(v=>'<button class="chip" data-v="'+v+'"'+(locked?' disabled':'')+'>x = '+neg(+v.toFixed(4))+'</button>').join('')+'</div>'+
      (o.allowNone?'<button class="btn small ghost nonebtn" aria-pressed="'+none+'"'+(locked?' disabled':'')+'>There are no critical numbers</button>':'');
  }
  list.addEventListener('click',e=>{
    if(locked)return;
    const c=e.target.closest('.chip'),n=e.target.closest('.nonebtn');
    if(c){const v=+c.dataset.v;vals=vals.filter(w=>Math.abs(w-v)>1e-9);}
    else if(n){none=!none;if(none){vals=[];P.clear();}}
    else return; draw(); o.onChange&&o.onChange();
  });
  draw();
  const all=()=>{const v=P.num();return Number.isNaN(v)||vals.some(w=>Math.abs(w-v)<1e-9)?vals.slice():vals.concat([v]);};
  return {canGo:()=>none||all().length>0,
    entered:()=>all(),
    check:()=>{const a=all().sort((x,y)=>x-y),k=o.answers.slice().sort((x,y)=>x-y);
      if(!k.length)return none&&!a.length; return !none&&a.length===k.length&&k.every((v,i)=>Math.abs(v-a[i])<=0.01);},
    lock(ok){locked=true;const v=P.num();if(!Number.isNaN(v)&&!vals.some(w=>Math.abs(w-v)<1e-9))vals.push(v);P.clear();P.lock(ok);draw();},
    reset(){locked=false;vals=[];none=false;P.reset();draw();}};
}
function mountCrit(q,ix,onChange){
  const W=critWidget(ix,{answers:q.answers,allowNone:true,onChange});
  return {kind:'q',canGo:W.canGo,check:W.check,lock:(r,ok)=>W.lock(ok),reset(){W.reset();onChange();}};
}
/* the "test every candidate" lesson widget: crit numbers, endpoints, table of values, tap the max, tap the min */
function autoGraph(f){
  const [a,b]=f.domain,F=fn(f.expr); let lo=Infinity,hi=-Infinity;
  for(let k=0;k<=400;k++){const y=F(a+(b-a)*k/400);if(Number.isFinite(y)){lo=Math.min(lo,y);hi=Math.max(hi,y);}}
  const px=Math.max((b-a)*0.12,0.3),py=Math.max((hi-lo)*0.15,0.5),dots=[[a,F(a)],[b,F(b)]];
  (f.mark||[]).forEach(x=>dots.push([x,F(x)]));
  return {window:[Math.floor(a-px),Math.ceil(b+px),Math.floor(lo-py),Math.ceil(hi+py)],pieces:[{expr:f.expr,from:a,to:b}],dots};
}
const trim=v=>{const t=+v.toFixed(3);return neg(String(t));};
function mountExtrema(it,ix,onChange,host){
  const F=fn(it.fn.expr),[a,b]=it.fn.domain; let phase='crit',done=false,cand=[],step=0;
  ix.innerHTML='<div class="ext-given">'+(it.deriv?'<p class="txt">'+fmt(it.deriv)+'</p>':'')+'</div><div id="x-body"></div><div class="fb" id="x-fb" hidden></div>';
  const body=$('#x-body',ix),fb=$('#x-fb',ix);
  const say=(ok,msg)=>{fb.hidden=false;fb.className='fb '+(ok?'good':'bad');fb.innerHTML='<span>'+fmt(msg)+'</span>';};
  const crit=()=>{
    body.innerHTML='<p class="txt"><strong>Step 1.</strong> '+fmt(it.step1||'Find the critical numbers inside the interval and add them to your list.')+'</p><div id="cw"></div><button class="btn small" id="cchk">Check my list</button>';
    const W=critWidget($('#cw',body),{answers:it.crit,allowNone:it.crit.length===0,onChange:()=>{$('#cchk',body).disabled=!W.canGo();}});
    const btn=$('#cchk',body);btn.disabled=true;
    btn.onclick=()=>{
      if(W.check()){say(true,it.afterCrit||'Those are all of them. Now add the two endpoints.');W.lock(true);btn.remove();table();}
      else say(false,it.hint||'Not quite. Set the derivative equal to 0, and also look for places where it does not exist.');
    };
  };
  const table=()=>{
    cand=[{x:a,tag:'endpoint'},...it.crit.filter(c=>c>a&&c<b).map(c=>({x:c,tag:'critical'})),{x:b,tag:'endpoint'}]
      .sort((p,q)=>p.x-q.x).map(c=>Object.assign(c,{y:F(c.x)}));
    phase='max'; draw();
  };
  const draw=()=>{
    const mx=Math.max(...cand.map(c=>c.y)),mn=Math.min(...cand.map(c=>c.y));
    const msg=phase==='max'?'**Steps 2 and 3.** Here is every candidate with its value $f(x)$. Tap the **largest** value.':phase==='min'?'Now tap the **smallest** value.':'';
    let t=$('#tbl',body); const tb=document.createElement('div'); tb.id='tbl';
    tb.innerHTML=(msg?'<p class="txt">'+fmt(msg)+'</p>':'')+'<div class="cand">'+cand.map((c,i)=>
      '<button class="cand-r'+(c.pick?' is-'+c.pick:'')+'" data-i="'+i+'"'+(phase==='done'?' disabled':'')+'><span>x = '+trim(c.x)+'<em>'+c.tag+'</em></span><b>f(x) = '+trim(c.y)+'</b></button>').join('')+'</div>';
    if(t)t.replaceWith(tb); else body.appendChild(tb);
    tb.onclick=e=>{
      const r=e.target.closest('.cand-r');if(!r||phase==='done')return; const c=cand[+r.dataset.i];
      if(phase==='max'){
        if(Math.abs(c.y-mx)<1e-9){cand.forEach(k=>{if(Math.abs(k.y-mx)<1e-9)k.pick='max';});phase='min';say(true,'Yes. The largest value is '+trim(mx)+', so the absolute maximum is '+trim(mx)+'.');draw();}
        else say(false,'Not that one. Look for the largest $f(x)$ in the right-hand column.');
      }else if(phase==='min'){
        if(Math.abs(c.y-mn)<1e-9){cand.forEach(k=>{if(Math.abs(k.y-mn)<1e-9)k.pick='min';});phase='done';done=true;
          const xm=cand.filter(k=>k.pick==='max').map(k=>trim(k.x)).join(' and '),xn=cand.filter(k=>k.pick==='min').map(k=>trim(k.x)).join(' and ');
          say(true,'**Absolute maximum: '+trim(mx)+'** (at $x$ = '+xm+').\n**Absolute minimum: '+trim(mn)+'** (at $x$ = '+xn+').'+(it.after?'\n'+it.after:''));
          const g=document.createElement('div');g.className='gwrap';g.innerHTML=plot(autoGraph(Object.assign({},it.fn,{mark:cand.map(k=>k.x)})),false).svg;body.appendChild(g);
          draw();onChange();g.scrollIntoView({block:'nearest'});}
        else say(false,'Not that one. Look for the smallest $f(x)$. Negative numbers count as smaller.');
      }
    };
  };
  crit();
  return {kind:'pass',canGo:()=>done};
}

/* ---------- multi: several answer boxes sharing one pad (f(x0), f'(x0), x1 ...) ---------- */
function mountMulti(q,ix,onChange){
  const n=q.parts.length; let vals=Array(n).fill(''),cur=0,fail=false,locked=false,marks=null;
  ix.innerHTML='<div class="multi"></div>'+(q.fail?'<button class="btn small ghost failbtn" aria-pressed="false">'+esc(q.failText||'Newton’s method breaks down here')+'</button>':'')+
    padHTML('<button class="key wide" data-k="next">Next box ↓</button>');
  const box=$('.multi',ix),fb=$('.failbtn',ix);
  const okAt=i=>Math.abs(parseVal(vals[i])-q.parts[i].answer)<=(q.parts[i].tol!=null?q.parts[i].tol:q.tol!=null?q.tol:0.001);
  const draw=()=>{
    box.innerHTML=q.parts.map((p,i)=>'<button class="mrow'+(i===cur&&!locked&&!fail?' on':'')+(fail?' off':'')+'" data-p="'+i+'"'+(locked?' disabled':'')+'><span>'+fmt(p.label)+'</span><output class="ans-box'+(vals[i]===''?' empty':'')+
      (marks?(marks[i]?' is-right':' is-wrong'):'')+'">'+(vals[i]===''?'?':neg(vals[i]))+'</output></button>').join('');
    if(fb)fb.setAttribute('aria-pressed',fail);
  };
  const press=k=>{
    if(locked)return;
    if(k==='next')cur=(cur+1)%n; else{ if(fail){fail=false;} vals[cur]=editVal(vals[cur],k); }
    draw();onChange();
  };
  ix.addEventListener('click',e=>{
    if(locked)return;
    const k=e.target.closest('.key'),r=e.target.closest('.mrow');
    if(k)return press(k.dataset.k);
    if(r){cur=+r.dataset.p;fail=false;draw();onChange();return;}
    if(e.target.closest('.failbtn')){fail=!fail;draw();onChange();}
  });
  const keys=padKeys(press);
  itemKeys=e=>{ if(e.key==='ArrowDown'||e.key==='Tab'&&!e.shiftKey){press('next');e.preventDefault();}
    else if(e.key==='ArrowUp'||e.key==='Tab'){cur=(cur+n-1)%n;draw();e.preventDefault();} else keys(e); };
  draw();
  return {kind:'q',
    canGo:()=>fail||vals.every(v=>!Number.isNaN(parseVal(v))),
    check:()=>q.fails?fail:(!fail&&q.parts.every((_,i)=>okAt(i))),
    lock(reveal,ok){locked=true; if(!fail)marks=q.parts.map((_,i)=>okAt(i));
      if(fb){fb.disabled=true; if(fail)fb.classList.add(q.fails?'is-right':'is-wrong'); else if(reveal&&q.fails)fb.classList.add('is-right');}
      draw();},
    reset(){locked=false;marks=null;fail=false;cur=0;vals=Array(n).fill('');if(fb){fb.disabled=false;fb.classList.remove('is-right','is-wrong');}draw();onChange();}};
}

/* ---------- Newton explorer: drag x0, watch the tangent hit the axis, step to x1, x2, ... ---------- */
const SUBD='₀₁₂₃₄₅₆₇₈₉',sub=k=>String(k).split('').map(d=>SUBD[+d]).join('');
const fix=(v,d)=>neg(String(+v.toFixed(d==null?6:d)));
/* a window around [a,b] tall enough for the curve there, always showing the x-axis */
function viewOf(F,a,b){
  let lo=0,hi=0; for(let k=0;k<=240;k++){const y=F(a+(b-a)*k/240);if(Number.isFinite(y)){lo=Math.min(lo,y);hi=Math.max(hi,y);}}
  const py=(hi-lo)*0.12||1; return [a,b,lo-py,hi+py];
}
function mountNewton(it,ix,onChange,host){
  const F=fn(it.fn),D=it.dfn?fn(it.dfn):(x=>numDeriv(F,x)),W0=it.window,[lo,hi]=it.range||[W0[0],W0[1]];
  const tol=it.tol||0.0005,minSteps=it.minSteps||2,pick=it.pick!==false;
  let xs=[it.start==null?(lo+hi)/2:it.start],phase=pick?'pick':'iter',zoom=1,done=false;
  const gw=document.createElement('div');gw.className='gwrap gw-s';host.insertBefore(gw,ix);
  const nextOf=x=>{const d=D(x);return Math.abs(d)<1e-9||!Number.isFinite(d)?null:x-F(x)/d;};
  const view=()=>{if(zoom===1)return W0;const c=xs[xs.length-1],w=(W0[1]-W0[0])/zoom;return viewOf(F,c-w/2,c+w/2);};
  const drawG=()=>{
    const V=view(),P=plot({window:V,pieces:[{expr:it.fn,from:V[0],to:V[1]}],autoTicks:zoom>1||it.autoTicks,xstep:zoom===1?it.xstep:0,ystep:zoom===1?it.ystep:0},false);
    const r=v=>Math.round(Math.max(-9999,Math.min(9999,v))*10)/10,X=x=>r(P.sx(x)),Y=y=>r(P.sy(y)),last=xs.length-1;
    let o='<g clip-path="url(#'+P.clip+')">';
    xs.forEach((x,k)=>{const y=F(x),cls=k<last?' old':'';
      o+='<line class="n-v'+cls+'" x1="'+X(x)+'" x2="'+X(x)+'" y1="'+Y(0)+'" y2="'+Y(y)+'"/>';
      if(k<last)o+='<line class="n-t old" x1="'+X(x)+'" y1="'+Y(y)+'" x2="'+X(xs[k+1])+'" y2="'+Y(0)+'"/>';
      else{const d=D(x);o+='<line class="n-t" x1="'+X(V[0])+'" y1="'+Y(y+d*(V[0]-x))+'" x2="'+X(V[1])+'" y2="'+Y(y+d*(V[1]-x))+'"/>';}
    });
    xs.forEach((x,k)=>{o+='<circle class="n-x'+(k<last?' old':'')+'" cx="'+X(x)+'" cy="'+Y(0)+'" r="'+(k<last?3:4.5)+'"/>';});
    const nx=nextOf(xs[last]),cur=xs[last];
    o+='<circle class="n-p" cx="'+X(cur)+'" cy="'+Y(F(cur))+'" r="5"/>';
    if(nx!=null)o+='<circle class="n-next" cx="'+X(nx)+'" cy="'+Y(0)+'" r="5.5"/>';
    o+='</g>';
    const lab=(x,t,dy)=>x>=V[0]&&x<=V[1]?'<text class="n-lab" text-anchor="middle" x="'+X(x)+'" y="'+(Y(0)+dy)+'">'+t+'</text>':'';
    const below=F(cur)>0?-8:17; o+=lab(cur,'x'+sub(last),below);
    if(nx!=null&&Math.abs(P.sx(nx)-P.sx(cur))>16)o+=lab(nx,'x'+sub(last+1),below);
    gw.innerHTML=P.svg.replace('</svg>',o+'</svg>');
  };
  const say=(ok,msg)=>{const fb=$('#nfb',ix);fb.hidden=false;fb.className='fb '+(ok?'good':'bad');fb.innerHTML='<span>'+fmt(msg)+'</span>';};
  const table=()=>'<div class="ntab"><span>n</span><span>'+fmt('$x_n$')+'</span><span>'+fmt('$f(x_n)$')+'</span>'+
    xs.map((x,k)=>'<span>'+k+'</span><span>'+fix(x)+'</span><span>'+fix(F(x),6)+'</span>').join('')+'</div>';
  const ui=()=>{
    if(phase==='pick'){
      ix.innerHTML='<label class="slide-l" for="nx0">'+fmt(it.pickText||'Drag to choose your first guess $x_0$')+'</label>'+
        '<input type="range" id="nx0" min="'+lo+'" max="'+hi+'" step="'+((hi-lo)/400)+'" value="'+xs[0]+'"><div class="read" id="nrd"></div>'+
        '<button class="btn small" id="nlock">Use this guess</button><div class="fb" id="nfb" hidden></div>';
      const s=$('#nx0',ix),rd=()=>{const x=+s.value,d=D(x),nx=nextOf(x);xs=[x];
        $('#nrd',ix).innerHTML='<span>'+fmt('$x_0$ =')+' <b>'+fix(x,2)+'</b></span><span>'+fmt("$f'(x_0)$ =")+' <b>'+fix(d,2)+'</b></span><span>'+(nx==null?'Tangent is flat':'Tangent hits the axis at '+fmt('$x_1$ =')+' <b>'+fix(nx,3)+'</b>')+'</span>';
        drawG();};
      s.addEventListener('input',rd);rd();
      $('#nlock',ix).onclick=()=>{phase='iter';ui();};
    }else{
      ix.innerHTML='<div class="row nrow"><button class="btn small" id="nstep">Next guess '+fmt('$x_'+xs.length+'$')+'</button>'+
        '<button class="btn small ghost" id="zin" aria-label="Zoom in">Zoom +</button><button class="btn small ghost" id="zout" aria-label="Zoom out"'+(zoom===1?' disabled':'')+'>Zoom −</button></div>'+
        table()+'<div class="fb" id="nfb" hidden></div>'+(pick?'<button class="link" id="nre">Start over with a new '+fmt('$x_0$')+'</button>':'');
      $('#nstep',ix).onclick=step;
      $('#zin',ix).onclick=()=>{zoom=Math.min(zoom*4,4096);drawG();ui();};
      $('#zout',ix).onclick=()=>{zoom=Math.max(zoom/4,1);drawG();ui();};
      if($('#nre',ix))$('#nre',ix).onclick=()=>{xs=[xs[0]];phase='pick';zoom=1;ui();};
      drawG();
    }
  };
  const step=()=>{
    const x=xs[xs.length-1],nx=nextOf(x);
    if(nx==null){ui();return say(false,it.flat||"Here $f'(x)$ = 0, so the tangent line is flat. It never crosses the $x$-axis, and the formula would divide by zero. Start over with a different guess.");}
    xs.push(nx); ui();
    const n=xs.length-1;
    if(!Number.isFinite(nx)||Math.abs(nx)>1e6)return say(false,'The guesses are running away. Start over with a guess closer to the root.');
    if(Math.abs(nx-x)<tol&&n>=minSteps){
      const first=!done; done=true;
      say(true,(it.after||'Converged! The root is about {x}. That took {n} steps.').replace(/\{n\}/g,n).replace(/\{x\}/g,fix(nx,6)));
      if(first)onChange();
    }else if(nx<W0[0]||nx>W0[1])say(false,'That guess landed off the picture at $x$ = '+fix(nx,3)+'. Keep going, or start over closer to the root.');
    else if(done)say(true,'The digits have stopped changing: the root is about '+fix(nx,6)+'.');
  };
  ui();
  return {kind:'pass',canGo:()=>done||!!it.free};
}

/* ---------- bisection game: cut the interval in half, keep the half where the sign changes ---------- */
function mountBisect(it,ix,onChange,host){
  const F=fn(it.fn),goal=it.goal||0.05; let a=it.a,b=it.b,steps=0,done=false,rows=[];
  const gw=document.createElement('div');gw.className='gwrap gw-s';host.insertBefore(gw,ix);
  const sg=v=>v>0?'<b class="pos">positive</b>':v<0?'<b class="negv">negative</b>':'<b>zero</b>';
  const drawG=()=>{
    const w=b-a,V=steps===0&&it.window?it.window:viewOf(F,a-w*0.4,b+w*0.4),m=(a+b)/2;
    const P=plot({window:V,pieces:[{expr:it.fn,from:V[0],to:V[1]}],autoTicks:steps>0||it.autoTicks,xstep:steps===0?it.xstep:0,ystep:steps===0?it.ystep:0},false);
    const r=v=>Math.round(v*10)/10,X=x=>r(P.sx(x)),Y=y=>r(P.sy(Math.max(V[2],Math.min(V[3],y))));
    let o='<rect class="b-band" x="'+X(a)+'" y="'+Y(V[3])+'" width="'+r(P.sx(b)-P.sx(a))+'" height="'+r(P.sy(V[2])-P.sy(V[3]))+'"/>';
    o+='<line class="n-v" x1="'+X(m)+'" x2="'+X(m)+'" y1="'+Y(0)+'" y2="'+Y(F(m))+'"/>';
    [[a,'a'],[b,'b'],[m,'m']].forEach(([x,t])=>{const y=F(x);
      o+='<circle class="'+(t==='m'?'n-p':y>0?'b-pos':'b-neg')+'" cx="'+X(x)+'" cy="'+Y(y)+'" r="5"/><text class="n-lab" text-anchor="middle" x="'+X(x)+'" y="'+(Y(0)-8)+'">'+t+'</text>';});
    gw.innerHTML=P.svg.replace('</svg>',o+'</svg>');
  };
  const say=(ok,msg)=>{const fb=$('#bfb',ix);fb.hidden=false;fb.className='fb '+(ok?'good':'bad');fb.innerHTML='<span>'+msg+'</span>';};
  const ui=()=>{
    const m=(a+b)/2,fa=F(a),fb=F(b),fm=F(m);
    ix.innerHTML='<div class="bq"><p>Interval ['+fix(a,5)+', '+fix(b,5)+'], width '+fix(b-a,5)+'</p>'+
      '<p>'+fmt('$f(a)$')+' = '+fix(fa,3)+' '+sg(fa)+' · '+fmt('$f(b)$')+' = '+fix(fb,3)+' '+sg(fb)+'</p>'+
      '<p>Midpoint '+fmt('$m$')+' = '+fix(m,5)+', and '+fmt('$f(m)$')+' = '+fix(fm,3)+' '+sg(fm)+'</p></div>'+
      (done?'':'<p class="txt">'+fmt(it.ask||'Which half must contain the root?')+'</p><div class="duo"><button class="btn small ghost" data-h="L">Left half ['+fix(a,4)+', '+fix(m,4)+']</button><button class="btn small ghost" data-h="R">Right half ['+fix(m,4)+', '+fix(b,4)+']</button></div>')+
      '<div class="fb" id="bfb" hidden></div>'+
      (rows.length?'<div class="ntab b3"><span>step</span><span>interval</span><span>width</span>'+rows.map((q,k)=>'<span>'+(k+1)+'</span><span>['+fix(q[0],5)+', '+fix(q[1],5)+']</span><span>'+fix(q[1]-q[0],5)+'</span>').join('')+'</div>':'')+
      '<p class="tiny">Goal: an interval narrower than '+fix(goal,4)+'. Steps so far: '+steps+'.</p>';
    drawG();
  };
  ix.addEventListener('click',e=>{
    const h=e.target.closest('[data-h]'); if(!h||done)return;
    const m=(a+b)/2,fa=F(a),fm=F(m),right=fa*fm<=0?'L':'R';
    if(h.dataset.h!==right){
      const side=h.dataset.h==='L'?['a','m',fa,fm]:['m','b',fm,F(b)];
      return say(false,'Not that half. At '+side[0]+' and '+side[1]+' the function is '+sg(side[2])+' and '+sg(side[3])+'. With the same sign at both ends, the graph does not have to cross the axis in between. Look for the half where the sign <b>changes</b>.');
    }
    if(right==='L')b=m; else a=m; steps++; rows.push([a,b]);
    if(b-a<=goal){done=true;ui();say(true,fmt((it.after||'Done in {n} steps. The root is in [{a}, {b}].').replace(/\{n\}/g,steps).replace(/\{a\}/g,fix(a,5)).replace(/\{b\}/g,fix(b,5))));onChange();}
    else{ui();say(true,'Yes. The sign changes on that half, so the root is in ['+fix(a,5)+', '+fix(b,5)+']. Cut it again.');}
  });
  ui();
  return {kind:'pass',canGo:()=>done};
}

/* ---------- the map (home screen) ---------- */
const MARK={review:'↺',extra:'★',boss:'♛',start:'GO'};
const KIND={main:'Level',review:'Review',extra:'Extra',boss:'Boss',start:'Start'};
const HERO='<svg viewBox="0 0 30 34" aria-hidden="true"><ellipse cx="15" cy="31.5" rx="9" ry="2.2" style="fill:var(--ink);opacity:.25"/><rect x="5" y="9" width="20" height="21" rx="9" style="fill:var(--gold);stroke:var(--ink);stroke-width:2"/><path d="M4 13 Q15 -3 26 13 Z" style="fill:var(--curve);stroke:var(--ink);stroke-width:2;stroke-linejoin:round"/><circle cx="11" cy="19" r="2" style="fill:var(--ink)"/><circle cx="19" cy="19" r="2" style="fill:var(--ink)"/></svg>';
const edgesOf=n=>n.from||n.requires||[];
const masteryOf=kind=>{const qs=DECK.drills[kind].questions;return {n:qs.filter(isMastered).length,of:qs.length};};
function route(a,b){ // shortest way along the drawn roads
  const adj={}; MAP.nodes.forEach(n=>edgesOf(n).forEach(m=>{(adj[n.id]=adj[n.id]||[]).push(m);(adj[m]=adj[m]||[]).push(n.id);}));
  const prev={},q=[a]; prev[a]=null;
  while(q.length){const c=q.shift(); if(c===b)break; (adj[c]||[]).forEach(x=>{if(!(x in prev)){prev[x]=c;q.push(x);}});}
  if(!(b in prev))return null; const p=[]; for(let c=b;c!=null;c=prev[c])p.unshift(c); return p;
}
let walking=false;
function home(){
  rollDay(); walking=false;
  const H=MAP.height,lvl={}; let num=0;
  MAP.nodes.forEach(n=>{if(n.kind==='main')lvl[n.id]=++num;});
  if(!nodeById(S.pos[MAP.id]))S.pos[MAP.id]=MAP.nodes[0].id;
  let svg='<svg class="roads" viewBox="0 0 100 '+H+'" aria-hidden="true">';
  (MAP.regions||[]).forEach(r=>{svg+='<rect class="region" x="'+r.x+'" y="'+r.y+'" width="'+r.w+'" height="'+r.h+'" rx="4"/><text class="region-t" x="'+(r.x+3)+'" y="'+(r.y+5.5)+'">'+esc(r.label)+'</text>';});
  MAP.nodes.forEach(n=>edgesOf(n).forEach(id=>{const m=nodeById(id); if(!m)return; const side=n.kind==='review'||n.kind==='extra';
    svg+='<line class="road'+(side?' side':nodeCleared(m)?' open':'')+'" x1="'+m.x+'" y1="'+m.y+'" x2="'+n.x+'" y2="'+n.y+'"/>';}));
  svg+='</svg>';
  const tiles=MAP.nodes.map(n=>{const open=nodeOpen(n),done=nodeCleared(n)&&n.kind!=='start';
    return '<button class="node k-'+n.kind+(open?'':' locked')+(done?' done':'')+'" data-n="'+n.id+'" style="left:'+n.x+'%;top:'+(100*n.y/H)+'%" aria-label="'+esc(n.title)+(open?'':', locked')+(done?', cleared':'')+'"><span class="sq">'+(n.kind==='main'?lvl[n.id]:MARK[n.kind])+'</span><span class="nl">'+esc(n.label||n.title)+'</span></button>';}).join('');
  const left=RULES.streak-S.streak;
  screen({
    top:'<header class="hud"><div class="hud-a"><div><p class="eyebrow">'+esc(MAP.course)+' · World '+MAP.world+' of '+WORLDS.length+'</p><h1>'+esc(MAP.title)+'</h1></div><div class="hud-p"><b>'+S.points+'</b><span class="kick">game points</span></div></div>'+
      '<nav class="worlds" aria-label="Worlds">'+WORLDS.map(w=>'<button class="wt'+(w===MAP?' on':'')+'" data-world="'+w.id+'" aria-pressed="'+(w===MAP)+'"><b>'+w.world+'</b><span>'+esc(w.short||w.title)+'</span></button>').join('')+'</nav>'+
      '<div class="hud-b">'+pips()+'<span class="tiny">'+left+' more new '+(left===1?'answer':'answers')+' for a play</span><button class="mb" data-go="game">Match Board'+(S.plays?' · '+S.plays:'')+'</button></div></header>',
    body:(S.preview?'<p class="banner">Preview mode is on. Every stop is open and nothing is recorded.</p>':'')+
      '<div class="map" style="aspect-ratio:100/'+H+'">'+svg+tiles+'<div class="hero-ch" id="ch">'+HERO+'</div></div>'+
      '<p class="tiny"><button class="link" data-go="test">Instructor: deck test</button></p>',
    foot:'<div class="stop" id="stop"></div>'});
  const ch=$('#ch');
  const place=n=>{ch.style.left=n.x+'%';ch.style.top=(100*n.y/H)+'%';};
  const act=(to,name,status,off)=>'<button class="act" data-go="'+to+'"'+(off?' disabled':'')+'><b>'+esc(name)+'</b><span>'+status+'</span></button>';
  const stopHTML=n=>{
    const open=nodeOpen(n),d=n.deck?DECKS[n.deck]:null;
    let h='<div class="stop-h"><span class="badge k-'+n.kind+'">'+(n.kind==='main'?'Level '+lvl[n.id]:KIND[n.kind])+'</span><h2>'+esc(n.title)+'</h2>'+(nodeCleared(n)&&n.kind!=='start'?'<span class="clr">Cleared ✓</span>':'')+'</div>';
    if(n.blurb)h+='<p class="tiny">'+esc(n.blurb)+'</p>';
    if(n.kind==='start')return h;
    if(!open)return h+'<p class="note">Locked. Clear '+(n.requires||[]).map(nodeById).filter(r=>r&&!nodeCleared(r)).map(r=>r.title).join(' and ')+' first.</p>';
    if(!n.deck)return h+'<p class="note">Coming soon. This stop is still being built.</p>';
    if(!d||d.error)return h+'<p class="note bad">'+esc(d?d.error:'Deck not loaded')+'</p>';
    const p=ds(d.id),ready=!d.lesson||p.lessonDone||S.preview; let a='';
    if(d.lesson)a+=act('lesson','Lesson',p.lessonDone?'Done ✓':p.lessonAt>0?'Step '+(p.lessonAt+1)+' of '+d.lesson.slides.length:d.lesson.slides.length+' steps');
    drillKinds(d).forEach(k=>{const m=masteryOf(k);a+=act('drill:'+k,d.drills[k].title,ready?m.n+' of '+m.of+' mastered'+((p.sets[k]||0)>0?' ✓':''):'After the lesson',!ready);});
    return h+'<div class="acts">'+a+'</div>';
  };
  const select=id=>{
    const n=nodeById(id),d=n.deck?DECKS[n.deck]:null; S.pos[MAP.id]=id; save(); DECK=d&&!d.error?d:null;
    $('#stop').innerHTML=stopHTML(n);
    app.querySelectorAll('.node').forEach(b=>b.classList.toggle('here',b.dataset.n===id));
  };
  $('.map').onclick=e=>{
    const b=e.target.closest('.node'); if(!b||walking)return;
    const id=b.dataset.n,n=nodeById(id); if(id===S.pos[MAP.id])return;
    if(!nodeOpen(n)){$('#stop').innerHTML=stopHTML(n);toast('Locked for now');return;}
    const path=route(S.pos[MAP.id],id),still=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
    if(!path||path.length<2||still){place(n);return select(id);}
    const pts=path.map(nodeById); let seg=0,t0=null; walking=true; ch.classList.add('walk');
    const step=ts=>{
      if(!document.body.contains(ch)){walking=false;return;}
      if(t0==null)t0=ts;
      const a=pts[seg],c=pts[seg+1],len=Math.hypot(c.x-a.x,c.y-a.y)||1,f=Math.min(1,(ts-t0)*RULES.walkSpeed/1000/len);
      ch.style.left=(a.x+(c.x-a.x)*f)+'%';ch.style.top=(100*(a.y+(c.y-a.y)*f)/H)+'%';
      if(f>=1){seg++;t0=ts;
        if(seg>=pts.length-1){walking=false;ch.classList.remove('walk');select(id);ch.scrollIntoView({block:'nearest',behavior:'smooth'});return;}}
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  place(nodeById(S.pos[MAP.id])); select(S.pos[MAP.id]); ch.scrollIntoView({block:'center'});
}

/* ---------- lesson ---------- */
function lesson(){
  if(!DECK||!DECK.lesson)return home();
  const slides=DECK.lesson.slides,p=ds(DECK.id); let i=p.lessonDone?0:Math.min(p.lessonAt,slides.length-1);
  const show=()=>{
    const sl=slides[i],last=i===slides.length-1;
    screen({top:bar('Lesson · step '+(i+1)+' of '+slides.length,100*i/slides.length,S.preview?'<button class="link" id="skip">Skip</button>':''),
      body:'<article class="item"></article><div class="fb" hidden></div>',
      foot:(i>0?'<button class="btn ghost" id="prev">Back</button>':'')+'<button class="btn" id="go">Continue</button>'});
    const goB=$('#go'),fb=$('.fb'); let phase='answer',C=null;
    const upd=()=>{ if(!C)return;
      goB.textContent=C.kind==='pass'||phase==='right'?(last?'Finish lesson':'Continue'):phase==='wrong'?'Try again':'Check';
      goB.disabled=phase==='answer'&&!C.canGo(); };
    C=mountItem(sl,$('.item'),upd); upd();
    const next=()=>{
      if(last){ const before=deckCleared(DECK),first=!p.lessonDone; let won=false;
        if(!S.preview){p.lessonDone=true;p.lessonAt=0;if(first)won=awardPlay();save();}
        home(); toast(S.preview?'End of lesson (preview)':!before&&deckCleared(DECK)?'Stop cleared!':won?'Practice unlocked, and you earned a game play!':'Practice unlocked'); return; }
      i++; if(!S.preview&&!p.lessonDone){p.lessonAt=i;save();} show();
    };
    goB.onclick=()=>{
      if(C.kind==='pass'||phase==='right')return next();
      if(phase==='wrong'){phase='answer';fb.hidden=true;C.reset();return upd();}
      const ok=C.check();
      if(ok){phase='right';C.lock(true,true);upd();feedback(fb,true,sl.explain||'');}
      else{phase='wrong';C.lock(false,false);upd();feedback(fb,false,sl.hint||'Look again and give it another try.');}
    };
    if($('#prev'))$('#prev').onclick=()=>{i--;show();};
    if($('#skip'))$('#skip').onclick=next;
    enterKey(goB);
  };
  show();
}

/* ---------- drills ---------- */
function drill(kind){
  if(!DECK||!DECK.drills||!DECK.drills[kind])return home();
  const p=ds(DECK.id); if(DECK.lesson&&!p.lessonDone&&!S.preview)return home();
  const D=DECK.drills[kind],all=D.questions;
  const set=S.preview?all.slice():shuffle([...shuffle(all.filter(q=>!isMastered(q))),...shuffle(all.filter(isMastered))].slice(0,RULES.setSize));
  let i=0,score=0;
  const finish=()=>{
    let msg='Preview mode: nothing was recorded.',cleared='';
    if(!S.preview){ rollDay(); const key=DECK.id+':'+kind,before=deckCleared(DECK);
      p.sets[kind]=(p.sets[kind]||0)+1;
      if(!before&&deckCleared(DECK))cleared='<p class="verdict">Stop cleared! A new road is open on the map.</p>';
      if(S.setDay[key]===S.day)msg='You already collected today’s play for finishing this drill.';
      else{S.setDay[key]=S.day;msg=awardPlay()?'You earned a game play for finishing the set.':'You have reached today’s limit of '+RULES.dailyPlays+' plays. More tomorrow.';}
      save(); }
    const m=masteryOf(kind);
    screen({top:bar(D.title,100),
      body:'<div class="done"><p class="eyebrow">Set complete</p><p class="big">'+score+'<small> of '+set.length+'</small></p>'+cleared+'<p class="txt">'+msg+'</p><p class="tiny">Mastered '+m.n+' of '+m.of+' questions in this drill</p><span class="meter"><i style="width:'+(100*m.n/m.of)+'%"></i></span></div>',
      foot:'<button class="btn ghost" data-go="home">Map</button>'+(S.plays>0?'<button class="btn" data-go="game">Play Match Board</button>':'<button class="btn" data-go="drill:'+kind+'">Another set</button>')});
  };
  const show=()=>{
    const q=set[i];
    screen({top:bar(D.title+' · '+(i+1)+' of '+set.length,100*i/set.length,pips()),
      body:'<article class="item"></article><div class="fb" hidden></div>',foot:'<button class="btn" id="go" disabled>Check</button>'});
    const goB=$('#go'),fb=$('.fb'); let done=false,C=null;
    C=mountItem(q,$('.item'),()=>{if(C&&!done)goB.disabled=!C.canGo();});
    goB.onclick=()=>{
      if(done){i++;return i<set.length?show():finish();}
      const ok=C.check(); done=true; C.lock(true,ok); if(ok)score++;
      const note=record(q,ok);
      goB.textContent=i===set.length-1?'See results':'Next'; goB.disabled=false;
      $('.streak').outerHTML=pips();
      feedback(fb,ok,(ok?'':'Answer: '+answerText(q)+'\n')+(q.explain||''),note);
    };
    enterKey(goB);
  };
  show();
}

/* ---------- Match Board minigame: the board is saved between plays ---------- */
const NAMES=['circle','square','triangle','diamond','star','plus','ring','hexagon'];
const poly=(n,ro,ri)=>Array.from({length:ri?2*n:n},(_,k)=>{const a=-Math.PI/2+k*Math.PI*(ri?1:2)/n,r=ri&&k%2?ri:ro;return (20+r*Math.cos(a)).toFixed(1)+','+(20+r*Math.sin(a)).toFixed(1);}).join(' ');
const TINT=['var(--curve)','var(--teal)','var(--gold)','var(--ink)'];
function face(v){
  const c='style="fill:'+TINT[v%4]+'"';
  const s=[ '<circle cx="20" cy="20" r="14" '+c+'/>','<rect x="7" y="7" width="26" height="26" rx="3" '+c+'/>','<polygon points="20,5 36,33 4,33" '+c+'/>',
    '<polygon points="20,3 37,20 20,37 3,20" '+c+'/>','<polygon points="'+poly(5,17,7)+'" '+c+'/>','<path d="M15 4h10v11h11v10H25v11H15V25H4V15h11z" '+c+'/>',
    '<circle cx="20" cy="20" r="11" style="fill:none;stroke:'+TINT[v%4]+';stroke-width:6"/>','<polygon points="'+poly(6,16)+'" '+c+'/>' ][v];
  return '<svg viewBox="0 0 40 40" aria-hidden="true">'+s+'</svg>';
}
function newBoard(){const c=[];for(let k=0;k<8;k++)c.push(k,k);shuffle(c);return {cards:c,matched:c.map(()=>false),live:0,cleared:0};}
function game(){
  if(!S.game)S.game=newBoard();
  let open=[],busy=false;
  const draw=()=>{
    const G=S.game,found=G.matched.filter(Boolean).length/2;
    const msg=G.live>0?'Flip two cards. A pair scores '+RULES.pairPts+' points. '+RULES.misses+' misses ends this play, and the board stays as you left it.'
      :S.plays>0?'Your board is saved. Use a play to keep going.'
      :'Your board is saved. Earn a play in the drills: get '+RULES.streak+' new questions right in a row, or finish a set.';
    screen({top:bar('Match Board',null,'<span class="pts">'+S.points+' pts</span>'),
      body:'<div class="g-head"><div><span class="kick">Misses left</span><div class="lives">'+Array.from({length:RULES.misses},(_,k)=>'<i class="'+(k<G.live?'on':'')+'"></i>').join('')+'</div></div><div class="r"><span class="kick">Pairs found</span><b>'+found+' of 8</b></div></div>'+
        '<div class="board'+(G.live>0?'':' idle')+'">'+G.cards.map((v,k)=>{const up=G.matched[k]||open.includes(k);
          return '<button class="card'+(up?' up':'')+(G.matched[k]?' ok':'')+'" data-k="'+k+'" aria-label="'+(up?NAMES[v]:'Hidden card '+(k+1))+'">'+(up?face(v):'?')+'</button>';}).join('')+'</div>'+
        '<p class="tiny">'+msg+'</p>',
      foot:G.live>0?'':'<button class="btn" id="use"'+(S.plays<1?' disabled':'')+'>'+(S.plays<1?'No plays yet':'Use a play ('+S.plays+' ready)')+'</button>'});
    if($('#use'))$('#use').onclick=()=>{if(S.plays<1)return;S.plays--;S.game.live=RULES.misses;save();draw();};
    $('.board').onclick=e=>{const b=e.target.closest('.card');if(b)flip(+b.dataset.k);};
  };
  const flip=k=>{
    const G=S.game; if(G.live<1||busy||G.matched[k]||open.includes(k))return;
    open.push(k); if(open.length<2)return draw();
    const [a,b]=open;
    if(G.cards[a]===G.cards[b]){
      G.matched[a]=G.matched[b]=true;S.points+=RULES.pairPts;open=[];
      if(G.matched.every(Boolean)){
        S.points+=RULES.clearPts;const live=G.live,cleared=(G.cleared||0)+1;busy=true;save();draw();
        setTimeout(()=>{S.game=newBoard();S.game.live=live;S.game.cleared=cleared;busy=false;save();if($('.board')){draw();toast('Board cleared! +'+RULES.clearPts+' bonus');}},900);
        return;
      }
      save();return draw();
    }
    busy=true;draw();
    setTimeout(()=>{open=[];G.live--;busy=false;save();if($('.board'))draw();},900);
  };
  draw();
}


/* ---------- deck test ---------- */
/* numeric helpers used only by the deck test */
function numDeriv(F,x){const h=1e-5;return (F(x+h)-F(x-h))/(2*h);}
function bf(expr,dom){const F=fn(expr),[a,b]=dom,N=40000;let mx=-Infinity,mn=Infinity,xmx=a,xmn=a;
  for(let k=0;k<=N;k++){const x=a+(b-a)*k/N,y=F(x);if(!Number.isFinite(y))continue;if(y>mx){mx=y;xmx=x;}if(y<mn){mn=y;xmn=x;}}return {mx,mn,xmx,xmn};}
/* finds where f' is 0 or does not exist, by scanning the derivative */
function critScan(expr,dom){
  const F=fn(expr),[a,b]=dom,N=Math.round((b-a)/0.005),d=[],out=[];
  for(let k=0;k<=N;k++){const x=a+(b-a)*k/N;d.push({x,v:numDeriv(F,x),f:F(x)});}
  const add=x=>{if(!out.some(v=>Math.abs(v-x)<0.04))out.push(Math.round(x*1000)/1000);};
  for(let i=1;i<d.length-1;i++){
    const p=d[i],q=d[i+1]; if(!Number.isFinite(p.f)||!Number.isFinite(q.f))continue;
    if(!Number.isFinite(p.v)||!Number.isFinite(q.v)||Math.abs(p.v)>1e3){add(p.x);continue;}
    const nb=Math.max(Math.abs(p.v-d[i-1].v),d[i+2]?Math.abs(d[i+2].v-q.v):0);
    if(Math.abs(q.v-p.v)>40||Math.abs(q.v-p.v)>0.3+8*nb){add((p.x+q.x)/2);continue;}
    if(p.v*q.v<0){add(p.x-p.v*(q.x-p.x)/(q.v-p.v));continue;}
    if(Math.abs(p.v)<1e-3&&Math.abs(p.v)<=Math.abs(d[i-1].v)&&Math.abs(p.v)<=Math.abs(q.v))add(p.x);
  }
  return out.sort((x,y)=>x-y);
}
function validate(D){
  const out=[],add=(l,m)=>out.push({l,m}),seen=new Set(),gOK={},used=new Set();
  const showA=v=>typeof v==='string'?v:String(Math.round(v*1000)/1000);
  for(const [name,g] of Object.entries(D.graphs||{})){
    let good=true; const bad=m=>{good=false;add('fail','Graph '+name+': '+m);};
    const w=g.window;
    if(!Array.isArray(w)||w.length!==4||!(w[0]<w[1])||!(w[2]<w[3])){bad('window must be [xmin, xmax, ymin, ymax]');gOK[name]=false;continue;}
    if(!(g.pieces||[]).length)bad('has no pieces');
    (g.pieces||[]).forEach((p,k)=>{
      try{const f=compile(p.expr); if(!(p.from<p.to))throw Error('"from" must be less than "to"');
        if(!Number.isFinite(f((p.from+p.to)/2)))throw Error('gives no value in the middle of its range');
        if(p.from<w[0]||p.to>w[1])add('warn','Graph '+name+', piece '+(k+1)+': runs past the window');
      }catch(e){bad('piece '+(k+1)+' "'+p.expr+'": '+e.message);}
    });
    [...(g.holes||[]),...(g.dots||[])].forEach(p=>{if(p[0]<w[0]||p[0]>w[1]||p[1]<w[2]||p[1]>w[3])bad('point ('+p[0]+', '+p[1]+') is outside the window');});
    gOK[name]=good; if(good)add('pass','Graph '+name+' draws');
  }
  const check=(q,where,inLesson)=>{
    const errs=[],warns=[],tag=where+' '+(q.id||'(no id)');
    if(!q.id)errs.push('missing id'); else if(seen.has(q.id))errs.push('this id is used twice'); else seen.add(q.id);
    const types=inLesson?['info','explore','graph','mc','tf','bank','num','crit','extrema','multi','newton','bisect']:['graph','mc','tf','bank','num','crit','multi'];
    if(!types.includes(q.type))errs.push('type "'+q.type+'" is not allowed here');
    for(const k of ['title','text','hint','explain','after'])if(q[k]&&String(q[k]).split('$').length%2===0)errs.push('unmatched $ in '+k);
    const g=(D.graphs||{})[q.graph];
    if(q.graph){used.add(q.graph);if(!g)errs.push('graph "'+q.graph+'" does not exist');}
    if((q.type==='graph'||q.type==='explore')&&!q.graph)errs.push('needs a graph');
    if(q.type!=='graph'&&q.type!=='explore'&&q.type!=='extrema'&&!q.text&&!q.title)errs.push('has no text');
    if(q.type==='graph'){
      if(![ 'value','limit',...EXTASK].includes(q.ask))errs.push('ask must be "value", "limit", "absmax", "absmin", "argmax" or "argmin"');
      else if(EXTASK.includes(q.ask)){
        if(g&&gOK[q.graph]){const t=extTruth(g,q);
          if(t==='MULTI')errs.push('the extreme value is reached at more than one x, so asking for the location is ambiguous');
          else{const same=typeof t==='string'?q.answer===t:(typeof q.answer==='number'&&Math.abs(q.answer-t)<0.011);
            if(!same)errs.push('answer key says '+showA(q.answer)+' but the graph gives '+showA(t));}}
      }
      else if(typeof q.at!=='number')errs.push('"at" must be a number');
      else if(q.ask==='limit'&&!['left','right','both'].includes(q.side))errs.push('side must be "left", "right" or "both"');
      else if(!EXTASK.includes(q.ask)&&g&&gOK[q.graph]){const t=truth(g,q),same=typeof t==='string'?q.answer===t:(typeof q.answer==='number'&&Math.abs(q.answer-t)<1e-3);
        if(!same)errs.push('answer key says '+showA(q.answer)+' but the graph gives '+showA(t));}
    }
    if(q.type==='explore'){
      if(!q.target||typeof q.target.at!=='number')errs.push('needs target.at');
      else if(g&&gOK[q.graph]&&(q.target.at<=g.window[0]||q.target.at>=g.window[1]))errs.push('target is outside the graph window');
    }
    if(q.type==='mc'){
      if(!Array.isArray(q.options)||q.options.length<2)errs.push('needs at least 2 options');
      else{ if(!Number.isInteger(q.answer)||q.answer<0||q.answer>=q.options.length)errs.push('answer must be the position of the correct option (0 is the first)');
        if(new Set(q.options).size!==q.options.length)errs.push('two options are identical'); }
    }
    if(q.type==='tf'&&typeof q.answer!=='boolean')errs.push('answer must be true or false');
    const fnOK=f=>{try{if(!f||typeof f.expr!=='string'||!Array.isArray(f.domain)||!(f.domain[0]<f.domain[1]))throw Error('needs "expr" and "domain": [a, b]');
      const F=compile(f.expr); if(!Number.isFinite(F((f.domain[0]+f.domain[1])/2)))throw Error('gives no value in the middle of the interval'); return true;}catch(e){errs.push('function: '+e.message);return false;}};
    if(q.type==='num'){
      if(typeof q.answer!=='number')errs.push('answer must be a number');
      if(q.verify&&fnOK(q.verify)){const B=bf(q.verify.expr,q.verify.domain),want={max:B.mx,min:B.mn,argmax:B.xmx,argmin:B.xmn}[q.verify.ask];
        if(want==null)errs.push('verify.ask must be max, min, argmax or argmin');
        else if(Math.abs(want-q.answer)>Math.max(0.011,q.tol||0))errs.push('answer key says '+showA(q.answer)+' but the function gives '+showA(want)+' on that interval');}
    }
    if(q.type==='crit'){
      if(!Array.isArray(q.answers)||q.answers.some(v=>typeof v!=='number'))errs.push('answers must be a list of numbers (empty if there are none)');
      else if(q.verify&&fnOK({expr:q.verify.expr,domain:q.verify.range||[-5,5]})){
        const found=critScan(q.verify.expr,q.verify.range||[-5,5]);
        if(found.length!==q.answers.length||!q.answers.every(v=>found.some(w=>Math.abs(w-v)<0.03)))errs.push('answer key lists '+q.answers.join(', ')+' but scanning the function finds critical numbers at '+(found.map(v=>showA(v)).join(', ')||'none'));
        if(q.verify.dexpr){const F=fn(q.verify.expr),D=compile(q.verify.dexpr);for(const x of [-1.3,0.7,2.2])if(Number.isFinite(F(x))&&Math.abs(numDeriv(F,x)-D(x))>1e-3)errs.push('the derivative formula does not match the function at x = '+x);}
      }
    }
    if(q.type==='extrema'){
      if(fnOK(q.fn)){
        const [a,b]=q.fn.domain,cs=q.crit||[],B=bf(q.fn.expr,q.fn.domain),F=fn(q.fn.expr),list=[a,b,...cs.filter(c=>c>a&&c<b)];
        const best=(w)=>list.reduce((m,x)=>w*(F(x)-m)>0?F(x):m,F(list[0]));
        if(Math.abs(best(1)-B.mx)>1e-3||Math.abs(best(-1)-B.mn)>1e-3)errs.push('testing the listed points gives max '+showA(best(1))+' and min '+showA(best(-1))+', but the function really reaches '+showA(B.mx)+' and '+showA(B.mn)+' (a critical number may be missing)');
        const found=critScan(q.fn.expr,[a+0.02,b-0.02]);
        if(found.length!==cs.filter(c=>c>a&&c<b).length||!found.every(v=>cs.some(w=>Math.abs(w-v)<0.03)))errs.push('crit list does not match the critical numbers found by scanning ('+(found.map(v=>showA(v)).join(', ')||'none')+')');
      }
    }
    if(q.type==='multi'){
      if(!Array.isArray(q.parts)||!q.parts.length)errs.push('needs a list of parts');
      else{
        q.parts.forEach((p,k)=>{if(!p.label)errs.push('part '+(k+1)+' has no label');else if(String(p.label).split('$').length%2===0)errs.push('unmatched $ in part '+(k+1));
          if(!q.fails&&typeof p.answer!=='number')errs.push('part '+(k+1)+' answer must be a number');});
        if(q.fails&&!q.fail)errs.push('"fails" is true but there is no "fail" button to press');
        /* verify: {expr, x0, dexpr?}. Parts with calc "x1", "f(x0)", "f'(x0)" are recomputed by running Newton's method */
        if(q.verify){ try{
          const F=compile(q.verify.expr),Dx=q.verify.dexpr?compile(q.verify.dexpr):null,d=x=>Dx?Dx(x):numDeriv(F,x),xs=[q.verify.x0];
          if(Dx)for(const x of [-1.3,0.7,2.2])if(Number.isFinite(F(x))&&Math.abs(numDeriv(F,x)-Dx(x))>1e-3)errs.push('dexpr does not match the derivative of expr at x = '+x);
          for(let k=0;k<6;k++){const x=xs[k],dd=d(x);if(Math.abs(dd)<1e-7)break;xs.push(x-F(x)/dd);}
          const broke=Math.abs(d(q.verify.x0))<1e-7;
          if(q.fails&&!broke)errs.push("marked as failing, but f'(x0) is not 0");
          if(!q.fails&&broke)errs.push("f'(x0) = 0 here, so Newton's method fails; set \"fails\": true");
          if(!q.fails&&!broke)q.parts.forEach((p,k)=>{ if(!p.calc)return;
            let m,v; if((m=/^x(\d)$/.exec(p.calc)))v=xs[+m[1]]; else if((m=/^f\(x(\d)\)$/.exec(p.calc)))v=F(xs[+m[1]]); else if((m=/^f'\(x(\d)\)$/.exec(p.calc)))v=d(xs[+m[1]]);
            else return errs.push('part '+(k+1)+': calc must look like x1, f(x0) or f\'(x0)');
            if(v==null||Math.abs(v-p.answer)>Math.max(0.0011,p.tol||q.tol||0))errs.push('part '+(k+1)+' answer key says '+showA(p.answer)+' but Newton\'s method gives '+showA(v));});
        }catch(e){errs.push('verify: '+e.message);} }
      }
    }
    if(q.type==='newton'||q.type==='bisect'){
      try{const F=compile(q.fn),w=q.window;
        if(!Array.isArray(w)||w.length!==4||!(w[0]<w[1])||!(w[2]<w[3]))throw Error('window must be [xmin, xmax, ymin, ymax]');
        if(q.dfn){const Dx=compile(q.dfn);for(const x of [w[0]*0.7+w[1]*0.3,(w[0]+w[1])/2])if(Math.abs(numDeriv(F,x)-Dx(x))>1e-3)throw Error('dfn does not match the derivative of fn');}
        if(q.type==='bisect'){if(!(F(q.a)*F(q.b)<0))throw Error('f(a) and f(b) must have opposite signs');}
        else if(q.pick===false){let x=q.start,ok=false;for(let k=0;k<40&&Number.isFinite(x);k++){const nx=x-F(x)/numDeriv(F,x);if(Math.abs(nx-x)<(q.tol||0.0005)){ok=true;break;}x=nx;}
          if(!ok)warns.push('starting at '+q.start+', Newton\'s method does not settle within 40 steps');}
      }catch(e){errs.push(e.message);}
    }
    if(q.type==='bank'){
      const n=String(q.text||'').split('___').length-1;
      if(!Array.isArray(q.blanks)||!q.blanks.length)errs.push('needs blanks');
      else{ if(n!==q.blanks.length)errs.push('text has '+n+' blanks but the key lists '+q.blanks.length);
        const chips=[...q.blanks,...(q.distractors||[])];
        if(new Set(chips).size!==chips.length)errs.push('the word bank repeats a word');
        if(!(q.distractors||[]).length)warns.push('word bank has no extra words'); }
    }
    const isQ=['graph','mc','tf','bank','multi'].includes(q.type);
    if(isQ&&inLesson&&!q.hint)warns.push('no hint for a wrong answer');
    if(isQ&&!inLesson&&!q.explain)warns.push('no explanation');
    errs.forEach(e=>add('fail',tag+': '+e)); warns.forEach(x=>add('warn',tag+': '+x));
    if(!errs.length)add('pass',tag+' ('+q.type+')');
  };
  const slides=(D.lesson||{}).slides||[];
  if(!D.id)add('fail','Deck has no id');
  if(D.lesson&&!slides.length)add('fail','Lesson has no slides');
  if(!D.lesson&&!Object.keys(D.drills||{}).length)add('fail','Deck has no lesson and no drills');
  slides.forEach(q=>check(q,'Lesson',true));
  for(const kind of Object.keys(D.drills||{})){
    const dr=D.drills[kind],qs=dr.questions||[],name=dr.title||kind;
    if(!dr.title)add('fail','Drill "'+kind+'" has no title');
    if(!qs.length)add('fail',name+' has no questions');
    else if(qs.length<RULES.setSize)add('warn',name+' has '+qs.length+' questions, fewer than one set of '+RULES.setSize);
    qs.forEach(q=>check(q,name,false));
  }
  Object.keys(D.graphs||{}).forEach(n=>{if(!used.has(n))add('warn','Graph '+n+' is never used');});
  return out;
}
function validateMap(M){
  const out=[],add=(l,m)=>out.push({l,m:M.title+' · '+m}),ids=new Set(),kinds=['start','main','review','extra','boss'];
  if(!(M.height>0))add('fail','Map: height must be a positive number');
  (M.nodes||[]).forEach(n=>{
    const tag='Stop '+(n.id||'(no id)'),errs=[];
    if(!n.id)errs.push('missing id'); else if(ids.has(n.id))errs.push('this id is used twice'); ids.add(n.id);
    if(!n.title)errs.push('missing title');
    if(!kinds.includes(n.kind))errs.push('kind "'+n.kind+'" must be one of '+kinds.join(', '));
    if(!(n.x>=0&&n.x<=100)||!(n.y>=0&&n.y<=M.height))errs.push('x or y is off the map');
    [...(n.requires||[]),...(n.from||[])].forEach(r=>{if(!(M.nodes||[]).some(m=>m.id===r))errs.push('points to "'+r+'", which is not a stop');});
    if(n.deck){const d=DECKS[n.deck]; if(!d||d.error)errs.push(d?d.error:'deck "'+n.deck+'" did not load'); else if(d.id!==n.deck)errs.push('the deck file says its id is "'+d.id+'" but the map says "'+n.deck+'"');}
    errs.forEach(e=>add('fail',tag+': '+e));
    if(n.kind!=='start'&&!(n.requires||[]).length)add('warn',tag+': has no "requires", so it is open from the beginning');
    if(!errs.length)add('pass',tag+' ('+n.kind+(n.deck?', deck '+n.deck:', no deck yet')+')');
  });
  if(!(M.nodes||[]).some(n=>n.kind==='start'))add('fail','Map: needs one stop with kind "start"');
  return out;
}
function test(){
  let res=[]; WORLDS.forEach(w=>{res=res.concat(validateMap(w));});
  const ids=Object.keys(DECKS).filter(id=>!DECKS[id].error);
  ids.forEach(id=>{res=res.concat(validate(DECKS[id]).map(r=>({l:r.l,m:id+' · '+r.m})));});
  const cnt=l=>res.filter(r=>r.l===l).length,f=cnt('fail'),w=cnt('warn'),p=cnt('pass');
  const li=l=>res.filter(r=>r.l===l).map(r=>'<li class="'+l+'"><b>'+(l==='fail'?'Error':l==='warn'?'Warning':'OK')+'</b>'+esc(r.m)+'</li>').join('');
  const allNodes=[].concat(...WORLDS.map(w=>w.nodes)),soon=allNodes.filter(n=>n.kind!=='start'&&!n.deck).length;
  const rows=ids.map(id=>{const d=DECKS[id];return '<span>'+esc(id)+'</span><span>'+(d.lesson?d.lesson.slides.length+' steps, ':'')+drillKinds(d).reduce((s,k)=>s+d.drills[k].questions.length,0)+' questions</span>';}).join('');
  screen({top:bar('Deck test',null),
    body:'<div class="test"><h2>Deck test</h2>'+
      '<p class="verdict'+(f?' bad':'')+'">'+(f?f+(f===1?' error':' errors')+' to fix before students see this':'Map and decks are ready: no errors')+(w?', '+w+(w===1?' warning':' warnings'):'')+'</p>'+
      (f||w?'<ul class="res">'+li('fail')+li('warn')+'</ul>':'')+
      '<details><summary>'+p+' checks passed</summary><ul class="res">'+li('pass')+'</ul></details>'+
      '<p class="tiny">Every graph question is solved from its own graph and compared with the answer key.</p>'+
      '<h3>What is built</h3><div class="kv"><span>Worlds</span><span>'+WORLDS.length+'</span><span>Stops on the maps</span><span>'+allNodes.filter(n=>n.kind!=='start').length+'</span><span>Stops still to build</span><span>'+soon+'</span>'+rows+'</div>'+
      '<h3>Preview</h3><label class="switch" for="pv"><input type="checkbox" id="pv"'+(S.preview?' checked':'')+'> Preview mode</label>'+
      '<p class="tiny">Opens every stop on the map, adds Skip to lessons, runs every drill question in deck order, and records nothing.</p>'+
      '<h3>Testing tools</h3><div class="row"><button class="btn small ghost" id="addplay">Add a game play</button><button class="btn small ghost" id="reset">Reset my progress</button></div></div>'});
  $('#pv').onchange=e=>{S.preview=e.target.checked;save();};
  $('#addplay').onclick=()=>{S.plays++;save();toast('Play added. You have '+S.plays+'.');};
  let armed=false;
  $('#reset').onclick=e=>{
    if(!armed){armed=true;e.target.textContent='Tap again to erase progress';return;}
    const pv=S.preview;S=fresh();S.preview=pv;save();test();toast('Progress reset');
  };
}

/* ---------- start up ---------- */
async function boot(){
  app.innerHTML='<main class="body"><p class="tiny">Loading the map…</p></main>';
  try{const idx=await getJSON('worlds.json'); WORLDS=await Promise.all(idx.worlds.map(getJSON));
    WORLDS.forEach(w=>{if(!w.id)throw Error('A map file has no "id"');}); WORLDS.sort((a,b)=>a.world-b.world);
    MAP=WORLDS.find(w=>w.id===S.world)||WORLDS[0]; S.world=MAP.id;}
  catch(e){app.innerHTML='<main class="body"><p class="verdict bad">'+esc(e.message)+'</p><p class="tiny">If you opened index.html straight from a folder, it cannot read the map and deck files. Open the GitHub Pages address instead.</p></main>';return;}
  const ids=[...new Set([].concat(...WORLDS.map(w=>w.nodes)).map(n=>n.deck).filter(Boolean))];
  await Promise.all(ids.map(async id=>{try{DECKS[id]=await getJSON('decks/'+id+'.json');}catch(e){DECKS[id]={error:e.message};}}));
  home();
}
boot();
