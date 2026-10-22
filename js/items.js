/* CalcGame engine, part 2: item types added for World 3.
   expr (typed formulas), interval (interval notation), order (put steps in order),
   steps (multi-part word problems), sketch (draw a graph from its data),
   optim, rr, curvex and ratio (lesson explorers).
   This file loads before app.js and uses its helpers ($, fmt, plot, fn, ...) when items are shown. */

let CTX='drill';            /* 'lesson', 'drill' or 'exam'; set by app.js when a screen opens */
let stepEnter=null;         /* Enter key inside a multi-part problem checks the current step */

/* ---------- numbers ---------- */
const SUPD={'-':'⁻','0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'};
function sci(v,d){
  d=d||6; if(v==null||Number.isNaN(v))return 'undefined'; if(!Number.isFinite(v))return v>0?'∞':'−∞'; if(v===0)return '0';
  const a=Math.abs(v); if(a>=1e-4&&a<1e7)return neg(String(+v.toPrecision(d)));
  const e=Math.floor(Math.log10(a)),m=v/Math.pow(10,e);
  return neg(String(+m.toPrecision(3)))+'×10'+String(e).split('').map(c=>SUPD[c]).join('');
}
const nice=v=>v===-Infinity?'−∞':v===Infinity?'∞':neg(String(+(+v).toFixed(3)));

/* ---------- expressions in several variables, with implied multiplication (2rh, 3x(x+1)) ---------- */
const XFN={sin:Math.sin,cos:Math.cos,tan:Math.tan,sec:x=>1/Math.cos(x),csc:x=>1/Math.sin(x),cot:x=>1/Math.tan(x),
  sqrt:Math.sqrt,cbrt:Math.cbrt,ln:Math.log,log:Math.log,exp:Math.exp,abs:Math.abs,arctan:Math.atan,arcsin:Math.asin,arccos:Math.acos,
  sinh:Math.sinh,cosh:Math.cosh,tanh:Math.tanh};
function xtokens(src,vars){
  const s=String(src).replace(/\s+/g,'').replace(/π/g,'pi').replace(/[−–]/g,'-').replace(/[×·]/g,'*').replace(/÷/g,'/')
    .replace(/√/g,'sqrt').replace(/′/g,"'");
  const names=[...new Set([...vars,...Object.keys(XFN),'pi','e'])].sort((a,b)=>b.length-a.length),out=[]; let i=0;
  while(i<s.length){
    const num=/^\d*\.?\d+/.exec(s.slice(i)); if(num){out.push({t:'n',v:+num[0]});i+=num[0].length;continue;}
    if('+-*/^()'.includes(s[i])){out.push({t:s[i]});i++;continue;}
    const nm=names.find(n=>s.startsWith(n,i));
    if(nm){i+=nm.length;
      if(vars.includes(nm))out.push({t:'v',v:nm});
      else if(XFN[nm])out.push({t:'f',v:nm});
      else out.push({t:'n',v:nm==='pi'?Math.PI:Math.E});
      continue;}
    throw Error('I can’t read "'+s[i]+'" here');
  }
  return out;
}
function xcompile(src,vars){
  const T=xtokens(src,vars||['x']); let i=0;
  const pk=()=>T[i]||{},atomStart=t=>t.t==='n'||t.t==='v'||t.t==='f'||t.t==='(';
  const expr=()=>{let a=term();while(pk().t==='+'||pk().t==='-'){const op=T[i++].t,l=a,r=term();a=op==='+'?e=>l(e)+r(e):e=>l(e)-r(e);}return a;};
  const term=()=>{let a=unary();
    for(;;){const t=pk();
      if(t.t==='*'||t.t==='/'){i++;const l=a,r=unary();a=t.t==='*'?e=>l(e)*r(e):e=>l(e)/r(e);}
      else if(atomStart(t)){const l=a,r=power();a=e=>l(e)*r(e);}
      else break;}
    return a;};
  const unary=()=>{if(pk().t==='-'){i++;const a=unary();return e=>-a(e);}if(pk().t==='+'){i++;return unary();}return power();};
  const power=()=>{const a=atom();if(pk().t==='^'){i++;const b=unary();return e=>rpow(a(e),b(e));}return a;};
  const atom=()=>{const t=T[i++]||{};
    if(t.t==='n'){const v=t.v;return()=>v;}
    if(t.t==='v'){const n=t.v;return e=>e[n];}
    if(t.t==='('){const a=expr();if((T[i++]||{}).t!==')')throw Error('a ( is missing its )');return a;}
    if(t.t==='f'){const f=XFN[t.v];
      if(pk().t==='('){i++;const a=expr();if((T[i++]||{}).t!==')')throw Error('a ( is missing its )');return e=>f(a(e));}
      const a=power();return e=>f(a(e));}
    throw Error(t.t?'"'+t.t+'" is in an odd place':'the expression ends early');};
  if(!T.length)throw Error('empty');
  const f=expr(); if(i<T.length)throw Error('"'+(T[i].v||T[i].t)+'" is in an odd place'); return f;
}
const closeParens=s=>{let d=0;for(const c of s){if(c==='(')d++;else if(c===')')d--;}return s+')'.repeat(Math.max(0,d));};
/* two formulas are the same if they agree at many random points */
function xequiv(a,b,vars,ranges){
  let A,B; try{A=xcompile(a,vars);B=xcompile(b,vars);}catch(e){return false;}
  let good=0;
  for(let k=0;k<60&&good<10;k++){
    const env={}; vars.forEach(v=>{const r=(ranges&&ranges[v])||[0.35,2.65];env[v]=r[0]+(r[1]-r[0])*Math.random();});
    const y=B(env),x=A(env); if(!Number.isFinite(y))continue; if(!Number.isFinite(x))return false;
    if(Math.abs(x-y)>1e-6*Math.max(1,Math.abs(y)))return false; good++;
  }
  return good>=4;
}
/* typed formula shown nicely: √, π, ·, superscripts, italic letters */
const FNAMES=/^(sin|cos|tan|sec|csc|cot|ln|log|exp|abs|arctan|arcsin|arccos|sqrt|cbrt|sinh|cosh|tanh)$/;
function pexp(s){
  let t=esc(s).replace(/sqrt\(/g,'√(').replace(/cbrt\(/g,'∛(').replace(/pi/g,'π').replace(/inf/g,'∞').replace(/\*/g,'·').replace(/-/g,'−')
    .replace(/[A-Za-zθ]+/g,w=>FNAMES.test(w)?w:w.split('').map(c=>'\u0001'+c+'\u0002').join(''));
  t=t.replace(/\^\(([^()]*)\)/g,'<sup>$1</sup>').replace(/\^(−?[0-9.]+|\u0001.\u0002'?|π)/g,'<sup>$1</sup>');
  return t.replace(/\u0001(.)\u0002/g,'<i>$1</i>');
}
/* Draw typed tokens with real fractions: "/" takes the operand just before it as the top and the next operand as the bottom
   (exactly how the answer is read, so 1/2x shows ½·x). An unfinished bottom shows an empty box. */
function texprHTML(toks){
  let i=0; const n=toks.length,BOX='<i class="ph">□</i>';
  const bare=h=>/^\(.*\)$/.test(h)?h.slice(1,-1):h,fr=(a,b)=>'<span class="frac"><span>'+bare(a)+'</span><span>'+bare(b)+'</span></span>';
  const isOpen=t=>t==='('||/\($/.test(t);
  function group(strip){ /* from an opening token to its matching ) */
    const t=toks[i++],name=t==='('?'':t==='e^('?'e^':t.slice(0,-1); const inner=seq(true); let closed=false;
    if(toks[i]===')'){i++;closed=true;}
    if(t==='e^(')return 'e<sup>'+(inner||BOX)+'</sup>';
    const nm=name==='sqrt'?'√':name==='cbrt'?'∛':name;
    return (strip&&!name?inner:esc(nm)+'('+inner+(closed?')':''));
  }
  function operand(inSup){
    if(i>=n)return null; const t=toks[i]; let h;
    if(t==='-'){i++;const o=operand(inSup);return '−'+(o==null?'':o);}
    if(/^[0-9.]$/.test(t)){h='';while(i<n&&/^[0-9.]$/.test(toks[i]))h+=toks[i++];}
    else if(isOpen(t))h=group(inSup);
    else if(['+','*','/','^',')','^2'].includes(t))return null;
    else{h=pexp(t);i++;}
    for(;;){ if(toks[i]==='^2'){i++;h+='<sup>2</sup>';}
      else if(toks[i]==='^'){i++;const e=operand(true);h+='<sup>'+(e==null?BOX:e)+'</sup>';}
      else break; }
    return h;
  }
  function seq(inParen){
    const out=[];
    while(i<n){
      const t=toks[i];
      if(t===')'){ if(inParen)break; out.push({h:')',op:true});i++;continue; }
      if(t==='/'){i++;const prev=out.length&&!out[out.length-1].op?out.pop().h:BOX,d=operand(false);out.push({h:fr(prev,d==null?BOX:d),op:false});continue;}
      if(t==='+'||t==='*'||(t==='-'&&out.length&&!out[out.length-1].op)){out.push({h:t==='+'?' + ':t==='*'?'·':' − ',op:true});i++;continue;}
      const o=operand(false); if(o==null){out.push({h:esc(t),op:true});i++;} else out.push({h:o,op:false});
    }
    return out.map(x=>x.h).join('');
  }
  return seq(false);
}
const KLAB={back:'⌫','*':'×','/':'<span class="frac kf"><span>▢</span><span>▢</span></span>','-':'−','^2':'x²','^':'xⁿ','sqrt(':'√','cbrt(':'∛',pi:'π',clear:'Clear',inf:'∞',U:'∪','(':'(',')':')',
  'sin(':'sin','cos(':'cos','tan(':'tan','ln(':'ln','e^(':'eˣ','sec(':'sec','e':'e',
  'csc(':'csc','cot(':'cot','arcsin(':'arcsin','arccos(':'arccos','arctan(':'arctan','sinh(':'sinh','cosh(':'cosh','tanh(':'tanh','abs(':'|x|'};
const keyLab=k=>KLAB[k]!=null?KLAB[k]:/'$/.test(k)?esc(k.slice(0,-1))+'′':esc(k);
/* a row of keys */
const keyRow=(ks,cls)=>ks.map(k=>k==null?'<span></span>':'<button class="key'+(cls||'')+(k==='clear'?' wide':'')+'" data-k="'+esc(k)+'"'+(k==='back'?' aria-label="Delete"':k==='/'?' aria-label="Fraction (divide)"':'')+'>'+keyLab(k)+'</button>').join('');

function mountExpr(q,ix,onChange){
  const vars=q.vars||['x'],answers=[].concat(q.answer); let toks=[],locked=false;
  const top=[...vars,...(q.keys||[])];
  ix.innerHTML='<div class="ans xans"><span>'+fmt(q.label||'Answer =')+'</span><output class="ans-box xbox empty" aria-live="polite">?</output>'+(q.post?'<span>'+fmt(q.post)+'</span>':'')+'</div><p class="tiny xerr" hidden></p>'+
    '<div class="xkeys">'+keyRow(top,' xk')+'</div>'+
    '<div class="pad pad6">'+keyRow(['7','8','9','(',')','back','4','5','6','*','/','^','1','2','3','+','-','^2','0','.','clear'])+'</div>';
  const box=$('.xbox',ix),err=$('.xerr',ix),str=()=>closeParens(toks.join(''));
  const ok=()=>{try{xcompile(str(),vars);return true;}catch(e){return false;}};
  const show=()=>{box.innerHTML=toks.length?'<span>'+texprHTML(toks)+'</span>':'?';box.classList.toggle('empty',!toks.length);
    let m='';if(toks.length)try{xcompile(str(),vars);}catch(e){m=e.message;} err.hidden=!m||!toks.length; err.textContent=m?'Not finished yet: '+m+'.':'';};
  const press=k=>{ if(locked)return;
    if(k==='back')toks.pop(); else if(k==='clear')toks=[]; else toks.push(k);
    show();onChange(); };
  ix.addEventListener('click',e=>{const b=e.target.closest('.key');if(b)press(b.dataset.k);});
  itemKeys=e=>{ if(e.key==='Backspace'){press('back');e.preventDefault();return true;}
    if(e.key.length===1&&/[0-9a-zA-Z.+\-*/^()'π]/.test(e.key)){press(e.key);e.preventDefault();return true;} return false; };
  SINK=v=>{if(locked)return;String(v).split('').forEach(c=>toks.push(c));show();onChange();};
  show();
  return {kind:'q',canGo:()=>toks.length>0&&ok(),
    check:()=>answers.some(a=>xequiv(str(),a,vars,q.ranges)),
    lock(r,good){locked=true;box.classList.add(good?'is-right':'is-wrong');},
    reset(){locked=false;toks=[];box.classList.remove('is-right','is-wrong');show();onChange();}};
}

/* ---------- interval notation: (-inf, 2) U (2, inf) ---------- */
function parseIntervals(s){
  s=String(s).replace(/\s+/g,'').replace(/∞/g,'inf').replace(/∪/g,'U').replace(/[−–]/g,'-');
  if(s===''||s==='none'||s==='{}'||s==='∅')return [];
  if(s==='R')s='(-inf,inf)';
  const iv=s.split('U').map(p=>{
    const m=/^([\[(])([^,]+),([^,]+)([\])])$/.exec(p); if(!m)throw Error('each piece should look like (a, b) or [a, b]');
    const val=t=>t==='inf'||t==='+inf'?Infinity:t==='-inf'?-Infinity:parseVal(t),a=val(m[2]),b=val(m[3]);
    if(Number.isNaN(a)||Number.isNaN(b))throw Error('an endpoint is not a number');
    if(!(a<b))throw Error('the left end must be smaller than the right end');
    if((m[1]==='['&&a===-Infinity)||(m[4]===']'&&b===Infinity))throw Error('∞ always gets a round bracket');
    return {a,b,lc:m[1]==='[',rc:m[4]===']'};
  }).sort((p,q)=>p.a-q.a);
  const out=[];  /* [0,2) U [2,5] is the same set as [0,5] */
  iv.forEach(p=>{const l=out[out.length-1];
    if(l&&Math.abs(l.b-p.a)<1e-9&&(l.rc||p.lc)){l.b=p.b;l.rc=p.rc;} else out.push(Object.assign({},p));});
  return out;
}
function sameIntervals(a,b){
  try{const A=parseIntervals(a),B=parseIntervals(b);
    return A.length===B.length&&A.every((p,i)=>{const q=B[i],eq=(x,y)=>x===y||Math.abs(x-y)<=0.011;return eq(p.a,q.a)&&eq(p.b,q.b)&&(p.a===-Infinity||p.lc===q.lc)&&(p.b===Infinity||p.rc===q.rc);});}
  catch(e){return false;}
}
const pint=s=>esc(String(s)).replace(/inf/g,'∞').replace(/U/g,' ∪ ').replace(/-/g,'−').replace(/,/g,', ');
function mountInterval(q,ix,onChange){
  let toks=[],none=false,locked=false;
  ix.innerHTML='<div class="ans xans"><span>'+fmt(q.label||'Answer:')+'</span><output class="ans-box xbox empty" aria-live="polite">?</output></div><p class="tiny xerr" hidden></p>'+
    '<div class="pad pad6">'+keyRow(['(','[',']',')',',','U','7','8','9','inf','-','back','4','5','6','.','a/b','clear','1','2','3','0'])+'</div>'+
    (q.noneText?'<button class="btn small ghost nonebtn" aria-pressed="false">'+esc(q.noneText)+'</button>':'')+
    '<p class="tiny">Use ∞ for infinity and ∪ to join pieces. Fractions like 1/2 are fine.</p>';
  const box=$('.xbox',ix),err=$('.xerr',ix),nb=$('.nonebtn',ix),str=()=>toks.join('');
  const show=()=>{
    box.innerHTML='<span>'+(none?esc(q.noneText):toks.length?pint(str()):'?')+'</span>'; box.classList.toggle('empty',!toks.length&&!none);
    let m='';if(toks.length&&!none)try{parseIntervals(str());}catch(e){m=e.message;}
    err.hidden=!m; err.textContent=m?'Not finished yet: '+m+'.':''; if(nb)nb.setAttribute('aria-pressed',none);
  };
  const press=k=>{ if(locked)return; none=false;
    if(k==='back')toks.pop(); else if(k==='clear')toks=[]; else toks.push(k==='a/b'?'/':k); show();onChange(); };
  ix.addEventListener('click',e=>{ if(locked)return;
    const b=e.target.closest('.key'); if(b)return press(b.dataset.k);
    if(e.target.closest('.nonebtn')){none=!none;if(none)toks=[];show();onChange();} });
  itemKeys=e=>{ if(e.key==='Backspace'){press('back');e.preventDefault();return true;}
    if(e.key.length===1&&/[0-9()[\],.\/\-]/.test(e.key)){press(e.key);e.preventDefault();return true;}
    if(e.key==='u'||e.key==='U'){press('U');return true;} if(e.key==='i'){press('inf');return true;} return false; };
  show();
  const valid=()=>{try{parseIntervals(str());return true;}catch(e){return false;}};
  return {kind:'q',canGo:()=>none||(toks.length>0&&valid()),
    check:()=>none?q.answer==='none':q.answer!=='none'&&[].concat(q.answer).some(a=>sameIntervals(str(),a)),
    lock(r,good){locked=true;box.classList.add(good?'is-right':'is-wrong');if(nb)nb.disabled=true;},
    reset(){locked=false;toks=[];none=false;if(nb)nb.disabled=false;box.classList.remove('is-right','is-wrong');show();onChange();}};
}

/* ---------- order: tap the cards in the right order ---------- */
function mountOrder(q,ix,onChange){
  const n=q.items.length; let mix=shuffle(q.items.map((_,i)=>i)),seq=[],locked=false,marks=null;
  if(mix.every((v,i)=>v===i)&&n>1)mix.reverse();
  const draw=()=>{
    ix.innerHTML='<p class="tiny">'+esc(q.howto||'Tap the cards in order. Tap a placed card to take it back.')+'</p>'+
      '<ol class="ord">'+Array.from({length:n},(_,k)=>{const v=seq[k];
        return '<li><button class="ord-s'+(v==null?' empty':'')+(marks?(marks[k]?' is-right':' is-wrong'):'')+'" data-s="'+k+'"'+(v==null||locked?' disabled':'')+'><span class="tag">'+(k+1)+'</span><span>'+(v==null?'':fmt(q.items[v]))+'</span></button></li>';}).join('')+'</ol>'+
      '<div class="ord-pool">'+mix.filter(i=>!seq.includes(i)).map(i=>'<button class="opt ord-c" data-i="'+i+'"'+(locked?' disabled':'')+'>'+fmt(q.items[i])+'</button>').join('')+'</div>';
  };
  ix.addEventListener('click',e=>{ if(locked)return;
    const c=e.target.closest('.ord-c'),s=e.target.closest('.ord-s');
    if(c)seq.push(+c.dataset.i); else if(s){seq.splice(+s.dataset.s,1);} else return; draw();onChange(); });
  draw();
  return {kind:'q',canGo:()=>seq.length===n,check:()=>seq.every((v,i)=>v===i),
    lock(){locked=true;marks=seq.map((v,i)=>v===i);draw();},
    reset(){locked=false;marks=null;seq=[];draw();onChange();}};
}

/* ---------- steps: a word problem worked one part at a time ---------- */
function mountSteps(it,ix,onChange){
  const n=it.steps.length,res=[]; let at=0,done=false;
  ix.innerHTML='<ol class="steps"></ol>'; const ol=$('.steps',ix);
  const run=()=>{
    if(at>=n){done=true;stepEnter=null;onChange();return;}
    const st=it.steps[at],last=at===n-1,li=document.createElement('li');
    li.className='step on';
    li.innerHTML='<p class="st-n">Part '+(at+1)+' of '+n+'</p><div class="st-item item"></div><div class="fb" hidden></div><div class="row"><button class="btn small st-go">Check</button></div>';
    ol.appendChild(li);
    const btn=$('.st-go',li),fb=$('.fb',li); let phase='answer',tries=0,C=null;
    const upd=()=>{ if(!C)return; if(C.kind==='pass'){btn.textContent=last?'Finish':'Next part';btn.disabled=!C.canGo();}
      else if(phase==='answer'){btn.textContent='Check';btn.disabled=!C.canGo();} };
    C=mountItem(st,$('.st-item',li),upd); upd();
    /* a finished part shrinks to one line of work (its "work" text, or label + answer), so the
       whole solution so far stays on screen, like lines written on paper */
    const next=()=>{li.className='step done';btn.parentNode.remove();
      const good=res[at]!==false,a=st.work||((st.label?st.label+' ':'')+(answerText(st)||''));
      if(st.type!=='info'&&a.trim()){li.innerHTML='<div class="st-work'+(good?'':' fixed')+'"><span class="st-m">'+(good?'✓':'✗')+'</span><span>'+fmt(a)+'</span></div>';}
      at++;run();
      const nx=ol.lastElementChild; if(nx&&nx!==li)nx.scrollIntoView({block:'nearest',behavior:'smooth'});};
    const reveal=()=>{C.lock(true,false);res[at]=false;
      const a=answerText(st);
      feedback(fb,false,(a?'Answer: '+a+'\n':'')+(st.explain||''));phase='next';btn.textContent=last?'Finish':'Next part';btn.disabled=false;};
    btn.onclick=()=>{
      if(C.kind==='pass'){if(C.canGo()){res[at]=true;next();}return;}
      if(phase==='next')return next();
      if(phase==='retry'){phase='answer';fb.hidden=true;C.reset();upd();return;}
      const ok=C.check(); tries++;
      if(ok){C.lock(true,true);if(res[at]==null)res[at]=true;feedback(fb,true,st.explain||'');phase='next';btn.textContent=last?'Finish':'Next part';}
      else if(CTX==='lesson'&&tries<2){C.lock(false,false);res[at]=false;feedback(fb,false,st.hint||'Not quite. Give it another try.');phase='retry';btn.textContent='Try again';}
      else reveal();
    };
    stepEnter=()=>{if(!btn.disabled)btn.click();};
  };
  run();
  const right=()=>res.filter(Boolean).length;
  if(CTX==='lesson')return {kind:'pass',canGo:()=>done};
  return {kind:'q',auto:true,canGo:()=>done,check:()=>right()===n,lock(){},reset(){},
    summary:()=>'You got '+right()+' of '+n+' parts right on the first try.'};
}

/* ---------- small helpers for the explorers ---------- */
const d1=(F,x)=>{const h=1e-5;return (F(x+h)-F(x-h))/(2*h);};
const d2=(F,x)=>{const h=1e-3;return (F(x+h)-2*F(x)+F(x-h))/(h*h);};
function sayIn(el,ok,msg){el.hidden=false;el.className='fb '+(ok?'good':'bad');el.innerHTML='<span>'+fmt(msg)+'</span>';}
/* a curve as an svg path, broken where it leaves the window or is undefined */
function curvePath(F,P,V,N){
  N=N||300; let d='',pen=false,py=null; const r=v=>Math.round(v*10)/10,H=V[3]-V[2];
  for(let k=0;k<=N;k++){const x=V[0]+(V[1]-V[0])*k/N,y=F(x);
    if(Number.isFinite(y)&&y>=V[2]-H&&y<=V[3]+H&&!(pen&&py!=null&&Math.abs(y-py)>H*1.2)){d+=(pen?'L':'M')+r(P.sx(x))+' '+r(P.sy(y));pen=true;py=y;}
    else{pen=false;py=null;}}
  return d;
}

/* ---------- sketch: place the data, mark the regions, then draw the graph ---------- */
function mountSketch(it,ix,onChange,host){
  const F=fn(it.fn),W=it.window,[x0,x1,y0,y1]=W,D=it.data||{},pre=!!it.prefill;
  const pts=(D.points||[]).map(p=>({x:p[0],y:p[1],lab:p[2]||''})),vas=D.va||[],has=D.ha||[];
  const targets=[...pts.map((p,k)=>({id:'p'+k,kind:'pt',x:p.x,y:p.y,text:(p.lab?p.lab+' ':'')+'('+nice(p.x)+', '+nice(p.y)+')'})),
    ...vas.map((v,k)=>({id:'v'+k,kind:'va',x:v,text:'Vertical asymptote $x$ = '+nice(v)})),
    ...has.map((v,k)=>({id:'h'+k,kind:'ha',y:v,text:'Horizontal asymptote $y$ = '+nice(v)}))];
  let phases=(it.phases||['place','regions','draw']).filter(p=>p!=='place'||targets.length);
  if(pre)phases=phases.filter(p=>p==='draw');
  let ph=0,sel=null,strokes=[],curS=null,locked=false,result=null,showTrue=false;
  const placed=new Set(pre?targets.map(t=>t.id):[]);
  /* where the function is defined, and where its pieces break */
  const edges=[];{const N=800;let pv=null;for(let k=0;k<=N;k++){const x=x0+(x1-x0)*k/N,ok=Number.isFinite(F(x));if(pv!=null&&ok!==pv)edges.push(x);pv=ok;}}
  const near=(a,list)=>list.some(b=>Math.abs(a-b)<(x1-x0)*0.02);
  const brk=list=>{const b=[];[...list,...vas,...edges].forEach(v=>{if(v>x0&&v<x1&&!near(v,b))b.push(v);});return [x0,...b.sort((p,q)=>p-q),x1];};
  const incB=brk(D.crit||[]),ccB=brk(D.infl||[]);
  const cellsOf=(B,kind)=>B.slice(0,-1).map((a,i)=>{const b=B[i+1],xs=[0.3,0.5,0.7].map(t=>a+(b-a)*t);
    const vals=xs.map(x=>Number.isFinite(F(x))?(kind==='inc'?d1(F,x):d2(F,x)):NaN);
    const def=vals.every(Number.isFinite),s=vals.reduce((p,v)=>p+Math.sign(v),0);
    return {a,b,truth:def?(s>0?1:-1):0,pick:pre&&def?(s>0?1:-1):0,bad:false};});
  const rows={inc:cellsOf(incB,'inc'),cc:cellsOf(ccB,'cc')};
  const regionsDone=()=>!phases.includes('regions')||phases.indexOf('regions')<ph||pre;
  /* drawing surface */
  const gw=document.createElement('div');gw.className='gwrap gw-big sk';host.insertBefore(gw,ix);
  const P=plot({window:W,pieces:[],xstep:it.xstep,ystep:it.ystep,autoTicks:it.autoTicks},false);
  gw.innerHTML=P.svg.replace('</svg>','<g class="sk-o"></g><rect class="sk-cap" x="0" y="0" width="320" height="2000"/></svg>');
  const svg=$('svg',gw),og=$('.sk-o',gw),ux=(P.sx(x1)-P.sx(x0))/(x1-x0),uy=(P.sy(y0)-P.sy(y1))/(y1-y0);
  const toMath=e=>{const p=svg.createSVGPoint();p.x=e.clientX;p.y=e.clientY;const q=p.matrixTransform(svg.getScreenCTM().inverse());return [x0+(q.x-P.sx(x0))/ux,y1-(q.y-P.sy(y1))/uy];};
  const r=v=>Math.round(Math.max(-9999,Math.min(9999,v))*10)/10,X=x=>r(P.sx(x)),Y=y=>r(P.sy(y));
  const slant=D.slant?fn(D.slant):null;
  const draw=()=>{
    let o='<g clip-path="url(#'+P.clip+')">';
    if(regionsDone())rows.inc.forEach(c=>{if(c.truth)o+='<rect class="sk-t '+(c.truth>0?'up':'dn')+'" x="'+X(c.a)+'" y="'+Y(y1)+'" width="'+r(X(c.b)-X(c.a))+'" height="'+r(Y(y0)-Y(y1))+'"/>';});
    targets.forEach(t=>{if(!placed.has(t.id))return;
      if(t.kind==='va')o+='<line class="sk-as" x1="'+X(t.x)+'" x2="'+X(t.x)+'" y1="'+Y(y1)+'" y2="'+Y(y0)+'"/>';
      if(t.kind==='ha')o+='<line class="sk-as" x1="'+X(x0)+'" x2="'+X(x1)+'" y1="'+Y(t.y)+'" y2="'+Y(t.y)+'"/>';});
    if(slant)o+='<line class="sk-as" x1="'+X(x0)+'" y1="'+Y(slant(x0))+'" x2="'+X(x1)+'" y2="'+Y(slant(x1))+'"/>';
    if(regionsDone())rows.cc.forEach(c=>{if(c.truth&&X(c.b)-X(c.a)>14)o+='<text class="sk-cc" text-anchor="middle" x="'+r((X(c.a)+X(c.b))/2)+'" y="'+(Y(y1)+15)+'">'+(c.truth>0?'∪':'∩')+'</text>';});
    if(showTrue)o+='<path class="sk-true" d="'+curvePath(F,P,W,500)+'"/>';
    strokes.concat(curS?[curS]:[]).forEach(s=>{o+='<path class="sk-ink" d="'+s.map((p,k)=>(k?'L':'M')+X(p[0])+' '+Y(p[1])).join('')+'"/>';});
    o+='</g>';
    targets.forEach(t=>{if(t.kind==='pt'&&placed.has(t.id))o+='<circle class="sk-pt" cx="'+X(t.x)+'" cy="'+Y(t.y)+'" r="4.6"/>';});
    og.innerHTML=o;
  };
  /* sign-chart strips under the graph */
  const strip=()=>{
    const row=(cells,kind,lab)=>{const h=30;let s='<svg class="sk-strip" viewBox="0 0 320 '+h+'" aria-label="'+lab+'"><text class="sk-sl" x="2" y="19">'+lab+'</text>';
      cells.forEach((c,i)=>{const a=X(c.a)+1,w=Math.max(4,X(c.b)-X(c.a)-2);
        const g=c.truth===0?'':c.pick===0?'?':kind==='inc'?(c.pick>0?'↗':'↘'):(c.pick>0?'∪':'∩');
        s+='<g class="sk-cell'+(c.truth===0?' off':'')+(c.bad?' bad':'')+(c.pick&&c.truth?' set '+(kind==='inc'?(c.pick>0?'up':'dn'):(c.pick>0?'cu':'cd')):'')+'" data-row="'+kind+'" data-i="'+i+'"><rect x="'+r(a)+'" y="3" width="'+r(w)+'" height="'+(h-6)+'" rx="5"/>'+
          (w>12?'<text text-anchor="middle" x="'+r(a+w/2)+'" y="21">'+g+'</text>':'')+'</g>';});
      return s+'</svg>';};
    return row(rows.inc,'inc',"f′")+row(rows.cc,'cc',"f″");
  };
  const ui=()=>{
    const p=phases[ph]; let h='';
    if(D.lines&&D.lines.length)h+='<details class="sk-data"'+(p==='regions'||(p==='draw'&&!phases.includes('regions')&&!pre)?' open':'')+'><summary>The data</summary><ul>'+D.lines.map(l=>'<li>'+fmt(l)+'</li>').join('')+'</ul></details>';
    if(p==='place'){
      h+='<p class="txt">'+fmt(it.placeText||'**Put the data on the graph.** Tap an item, then tap where it goes.')+'</p><div class="chips sk-chips">'+
        targets.map(t=>'<button class="chip'+(sel===t.id?' on':'')+'" data-t="'+t.id+'"'+(placed.has(t.id)?' disabled':'')+'>'+fmt(t.text)+(placed.has(t.id)?' ✓':'')+'</button>').join('')+'</div>';
    }else if(p==='regions'){
      h+='<p class="txt">'+fmt(it.regionText||'**Mark the regions.** Tap each box: in the $f′$ row choose ↗ (increasing) or ↘ (decreasing); in the $f″$ row choose ∪ (concave up) or ∩ (concave down). Gray boxes are outside the domain.')+'</p>'+
        '<div class="sk-strips">'+strip()+'</div><button class="btn small" id="skreg">Check the regions</button>';
    }else{
      h+='<p class="txt">'+fmt(it.drawText||'**Now sketch it.** Draw the graph with your finger or mouse. You can lift and draw in several strokes.')+'</p>'+
        '<div class="row"><button class="btn small ghost" id="skundo">Undo stroke</button><button class="btn small ghost" id="skclr">Clear</button>'+(locked?'<button class="btn small ghost" id="sktrue">'+(showTrue?'Hide':'Show')+' the real graph</button>':'')+'</div>';
      if(result)h+='<ul class="sk-res">'+result.items.map(c=>'<li class="'+(c.ok?'ok':'no')+'">'+(c.ok?'✓ ':'✗ ')+fmt(c.text)+'</li>').join('')+'</ul>';
    }
    h+='<div class="fb" id="skfb" hidden></div>';
    ix.innerHTML=h; draw(); svg.classList.toggle('drawing',p==='draw'&&!locked);
  };
  const say=(ok,m)=>sayIn($('#skfb',ix),ok,m);
  const nextPhase=()=>{ph++;ui();onChange();};
  ix.addEventListener('click',e=>{
    const p=phases[ph];
    const t=e.target.closest('[data-t]'); if(t&&p==='place'){sel=sel===t.dataset.t?null:t.dataset.t;ui();if(sel)say(true,'Now tap the graph where it goes.');return;}
    const c=e.target.closest('.sk-cell'); if(c&&p==='regions'){const cell=rows[c.dataset.row][+c.dataset.i];if(!cell.truth)return;cell.pick=cell.pick===1?-1:1;cell.bad=false;$('.sk-strips',ix).innerHTML=strip();return;}
    if(e.target.id==='skreg'){
      let bad=0,miss=0; ['inc','cc'].forEach(k=>rows[k].forEach(c=>{if(!c.truth)return;if(!c.pick)miss++;else if(c.pick!==c.truth){c.bad=true;bad++;}}));
      if(miss){$('.sk-strips',ix).innerHTML=strip();return say(false,'Fill in every box first ('+miss+' still show ?).');}
      if(bad){$('.sk-strips',ix).innerHTML=strip();return say(false,bad+(bad>1?' boxes are':' box is')+' wrong (outlined in red). Check the sign of '+"$f′$ or $f″$ there and fix "+(bad>1?'them':'it')+'.');}
      return nextPhase();
    }
    if(e.target.id==='skundo'&&!locked){strokes.pop();draw();onChange();}
    if(e.target.id==='skclr'&&!locked){strokes=[];draw();onChange();}
    if(e.target.id==='sktrue'){showTrue=!showTrue;ui();}
  });
  /* taps and strokes on the graph */
  svg.addEventListener('pointerdown',e=>{
    const p=phases[ph],m=toMath(e);
    if(p==='place'){
      if(!sel)return say(false,'First tap one of the items above, then tap the graph.');
      const t=targets.find(q=>q.id===sel),tx=(x1-x0)*0.055,ty=(y1-y0)*0.055;
      const hit=t.kind==='pt'?Math.abs(m[0]-t.x)<=tx&&Math.abs(m[1]-t.y)<=ty:t.kind==='va'?Math.abs(m[0]-t.x)<=tx:Math.abs(m[1]-t.y)<=ty;
      if(!hit)return say(false,'That spot is at about ('+nice(m[0])+', '+nice(m[1])+'). Use the grid to find '+t.text.replace(/\$/g,'')+'.');
      placed.add(t.id);sel=null;
      if(placed.size===targets.length){ui();say(true,'All the data is on the graph.');setTimeout(()=>{if(phases[ph]==='place')nextPhase();},650);}
      else{ui();say(true,'Placed. Pick the next item.');}
      return;
    }
    if(p!=='draw'||locked)return;
    e.preventDefault(); svg.setPointerCapture(e.pointerId); curS=[m]; draw();
  });
  svg.addEventListener('pointermove',e=>{if(!curS)return;const m=toMath(e),l=curS[curS.length-1];
    if(Math.hypot((m[0]-l[0])*ux,(m[1]-l[1])*uy)>2.5){curS.push(m);draw();}});
  const end=()=>{if(!curS)return;if(curS.length>1)strokes.push(curS);curS=null;draw();onChange();};
  svg.addEventListener('pointerup',end);svg.addEventListener('pointercancel',end);
  /* grading: does the drawing have the right features? */
  function grade(){
    const N=260,dx=(x1-x0)/N,items=[];
    const segs=[];strokes.forEach(s=>{for(let k=1;k<s.length;k++)segs.push([s[k-1],s[k]]);});
    const at=x=>{const t=F(x);let best=null;
      segs.forEach(([a,b])=>{if((a[0]-x)*(b[0]-x)<=0&&a[0]!==b[0]){const y=a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0]);if(best==null||(Number.isFinite(t)&&Math.abs(y-t)<Math.abs(best-t)))best=y;}});
      return best;};
    const vis=x=>{const y=F(x);return Number.isFinite(y)&&y>=y0&&y<=y1;};
    /* 1. key points */
    const distPx=(px,py)=>{let m=Infinity;segs.forEach(([a,b])=>{const ax=a[0]*ux,ay=a[1]*uy,bx=b[0]*ux,by=b[1]*uy,qx=px*ux,qy=py*uy,vx=bx-ax,vy=by-ay,L=vx*vx+vy*vy;
      let t=L?((qx-ax)*vx+(qy-ay)*vy)/L:0;t=Math.max(0,Math.min(1,t));m=Math.min(m,Math.hypot(ax+t*vx-qx,ay+t*vy-qy));});return m;};
    const missed=pts.filter(p=>p.x>=x0&&p.x<=x1&&p.y>=y0&&p.y<=y1&&distPx(p.x,p.y)>15);
    if(pts.length)items.push({ok:!missed.length,text:missed.length?'Your sketch misses '+missed.slice(0,3).map(p=>'('+nice(p.x)+', '+nice(p.y)+')').join(', ')+'.':'Goes through every key point.'});
    /* 2. coverage */
    let need=0,have=0,gapAt=null;
    for(let k=1;k<N;k++){const x=x0+k*dx;if(!vis(x))continue;need++;if(at(x)!=null||at(x-dx)!=null||at(x+dx)!=null)have++;else if(gapAt==null)gapAt=x;}
    const cov=need?have/need:1;
    items.push({ok:cov>=0.85,text:cov>=0.85?'Covers the whole graph.':'Part of the graph is missing (look near $x$ = '+nice(gapAt)+').'});
    /* 3. up/down and 4. bending, region by region */
    const B=brk([...(D.crit||[]),...(D.infl||[])]),upBad=[],bendBad=[];
    for(let i=0;i<B.length-1;i++){
      const a=B[i],b=B[i+1],m=(b-a)*0.1,xs=[];for(let k=0;k<=40;k++){const x=a+m+(b-a-2*m)*k/40;if(vis(x))xs.push(x);}
      if(xs.length<5||(xs[xs.length-1]-xs[0])*ux<22)continue;
      const tr=xs.map(x=>F(x)),dr=xs.map(at); const pairs=xs.map((x,k)=>[x,tr[k],dr[k]]).filter(q=>q[2]!=null);
      const lab=(a<=x0+1e-9?'(−∞':'('+nice(a))+', '+(b>=x1-1e-9?'∞)':nice(b)+')');
      if(pairs.length<5)continue;
      const f0=pairs[0],f1=pairs[pairs.length-1],tdy=(f1[1]-f0[1])*uy,ddy=(f1[2]-f0[2])*uy;
      if(Math.abs(tdy)>8&&(Math.sign(ddy)!==Math.sign(tdy)||Math.abs(ddy)<3))upBad.push('On $'+lab+'$ the graph should be going '+(tdy>0?'**up**':'**down**')+'.');
      const dev=k=>{const xa=pairs[0][0],xb=pairs[pairs.length-1][0];let s=0;pairs.forEach(q=>{const ch=q[0]===xa?q[k]:pairs[0][k]+(pairs[pairs.length-1][k]-pairs[0][k])*(q[0]-xa)/(xb-xa);s+=(q[k]-ch);});return s/pairs.length*uy;};
      const tdev=dev(1),ddev=dev(2);
      if(Math.abs(tdev)>2.5&&(Math.sign(ddev)!==Math.sign(tdev)||Math.abs(ddev)<0.8))bendBad.push('On $'+lab+'$ the graph should bend '+(tdev<0?'**up** (∪)':'**down** (∩)')+'.');
    }
    items.push({ok:!upBad.length,text:upBad.length?upBad.slice(0,2).join(' '):'Goes up and down in the right places.'});
    items.push({ok:!bendBad.length,text:bendBad.length?bendBad.slice(0,2).join(' '):'Bends the right way (concavity).'});
    /* 5. behavior at vertical asymptotes */
    const asBad=[];
    vas.forEach(v=>[-1,1].forEach(s=>{
      if(v+s*(x1-x0)*0.01<x0||v+s*(x1-x0)*0.01>x1)return;
      const t=F(v+s*1e-4); if(!Number.isFinite(t)||(t<y1&&t>y0))return;
      const top=t>0; let got=null; /* the most extreme drawn height close to the asymptote on that side */
      const zone=(x1-x0)*0.16,use=y=>{if(y!=null&&(got==null||(top?y>got:y<got)))got=y;};
      for(let k=1;k<=40;k++){const x=v+s*(x1-x0)*0.004*k; if(x<x0||x>x1)break; use(at(x));}
      strokes.forEach(st=>st.forEach(([px,py])=>{const d=(px-v)*s;if(d>0&&d<=zone)use(py);}));
      const okA=got!=null&&(top?got>y1-(y1-y0)*0.3:got<y0+(y1-y0)*0.3);
      if(!okA)asBad.push('Just '+(s<0?'left':'right')+' of $x$ = '+nice(v)+' the graph should shoot '+(top?'**up**':'**down**')+' along the asymptote.');
    }));
    if(vas.length)items.push({ok:!asBad.length,text:asBad.length?asBad.slice(0,2).join(' '):'Hugs the vertical asymptotes the right way.'});
    return {ok:items.every(c=>c.ok),items};
  }
  ui();
  return {kind:'q',canGo:()=>phases[ph]==='draw'&&strokes.length>0&&!locked,
    check:()=>{result=grade();return result.ok;},
    lock(rv,good){locked=true;showTrue=!good||CTX!=='exam';ui();},
    reset(){locked=false;result=null;showTrue=false;strokes=[];ui();onChange();},
    summary:()=>result?result.items.filter(c=>!c.ok).map(c=>c.text).join('\n'):''};
}

/* ---------- optim: drag x and watch the shape and the quantity being optimized ---------- */
function sceneSVG(sc,x){
  const W=320,H=150,v=e=>fn(e)(x);
  if(sc.type==='rect'||sc.type==='window'){
    const w=v(sc.w),h=v(sc.h),mw=sc.maxW,mh=sc.maxH,s=Math.min((W-80)/mw,(H-40)/mh),pw=Math.max(1,w*s),phh=Math.max(1,h*s),ox=(W-pw)/2,oy=sc.wall==='top'?24:(H-phh)/2+(sc.type==='window'?pw/4:0);
    let o='<svg class="scene" viewBox="0 0 '+W+' '+H+'">';
    if(sc.wall==='top')o+='<path class="sc-water" d="M10 16 Q30 8 50 16 T90 16 T130 16 T170 16 T210 16 T250 16 T290 16 T310 16"/><text class="sc-t" x="'+(W-12)+'" y="12" text-anchor="end">'+esc(sc.wallLabel||'river')+'</text>';
    o+='<rect class="sc-fill" x="'+ox+'" y="'+oy+'" width="'+pw+'" height="'+phh+'"/>';
    if(sc.type==='window')o+='<path class="sc-fill sc-line" d="M'+ox+' '+oy+' A'+(pw/2)+' '+(pw/2)+' 0 0 1 '+(ox+pw)+' '+oy+'"/>';
    o+=sc.wall==='top'?'<path class="sc-line" d="M'+ox+' '+oy+' V'+(oy+phh)+' H'+(ox+pw)+' V'+oy+'"/><line class="sc-wall" x1="'+ox+'" x2="'+(ox+pw)+'" y1="'+oy+'" y2="'+oy+'"/>':'<rect class="sc-line" x="'+ox+'" y="'+oy+'" width="'+pw+'" height="'+phh+'"/>';
    const hx=ox+pw+6,inside=hx>W-80;
    o+='<text class="sc-t" x="'+(ox+pw/2)+'" y="'+Math.min(H-3,oy+phh+14)+'" text-anchor="middle">'+esc(sc.wl||'')+' = '+sci(w,4)+'</text><text class="sc-t" x="'+(inside?Math.max(ox+4,4):hx)+'" y="'+(oy+Math.max(phh/2,10)+4)+'" text-anchor="start">'+esc(sc.hl||'')+' = '+sci(h,4)+'</text>';
    return o+'</svg>';
  }
  if(sc.type==='box'){
    const S=sc.side,s=(H-20)/S,c=x*s,ox=20,oy=10,L=S*s;
    let o='<svg class="scene" viewBox="0 0 '+W+' '+H+'"><rect class="sc-fill" x="'+ox+'" y="'+oy+'" width="'+L+'" height="'+L+'"/>';
    [[0,0],[L-c,0],[0,L-c],[L-c,L-c]].forEach(([a,b])=>{o+='<rect class="sc-cut" x="'+(ox+a)+'" y="'+(oy+b)+'" width="'+c+'" height="'+c+'"/>';});
    o+='<rect class="sc-dash" x="'+(ox+c)+'" y="'+(oy+c)+'" width="'+(L-2*c)+'" height="'+(L-2*c)+'"/><text class="sc-t" x="'+(ox+c/2)+'" y="'+(oy+c+12)+'" text-anchor="middle">x</text>';
    /* the folded box, drawn in perspective */
    const bw=(S-2*x)*s*0.62,bh=x*s*0.62,dx=bw*0.35,bx=W-bw-dx-16,by=H-14-bh;
    o+='<path class="sc-fill sc-line" d="M'+bx+' '+by+' h'+bw+' v'+bh+' h'+(-bw)+' Z"/><path class="sc-fill2 sc-line" d="M'+(bx+bw)+' '+by+' l'+dx+' '+(-dx*0.6)+' v'+bh+' l'+(-dx)+' '+(dx*0.6)+' Z"/><path class="sc-dash" d="M'+bx+' '+by+' l'+dx+' '+(-dx*0.6)+' h'+bw+'"/>';
    o+='<text class="sc-t" x="'+(bx+bw/2)+'" y="'+(H-2)+'" text-anchor="middle">base '+sci(S-2*x,3)+', height '+sci(x,3)+'</text>';
    return o+'</svg>';
  }
  return '';
}
function mountOptim(it,ix,onChange,host){
  const F=fn(it.fn),[lo,hi]=it.range,W=it.window,goal=it.goal||'max',tol=it.tol||(hi-lo)/80; let x=it.start==null?lo+(hi-lo)*0.15:it.start,done=false;
  const sc=it.scene?Object.assign({},it.scene):null;
  if(sc&&(sc.type==='rect'||sc.type==='window')){let mw=0,mh=0;for(let k=0;k<=100;k++){const t=lo+(hi-lo)*k/100;mw=Math.max(mw,fn(sc.w)(t));mh=Math.max(mh,fn(sc.h)(t)*(sc.type==='window'?1:1)+(sc.type==='window'?fn(sc.w)(t)/2:0));}sc.maxW=mw||1;sc.maxH=mh||1;}
  const sw=document.createElement('div');sw.className='gwrap scw';if(sc)host.insertBefore(sw,ix);
  const gw=document.createElement('div');gw.className='gwrap gw-s';host.insertBefore(gw,ix);
  ix.innerHTML='<label class="slide-l" for="ox">'+fmt(it.pickText||'Drag to change $x$')+'</label><input type="range" id="ox" min="'+lo+'" max="'+hi+'" step="'+((hi-lo)/600)+'" value="'+x+'"><div class="read lread" id="or"></div><div class="fb" id="ofb" hidden></div>';
  const drawAll=()=>{
    if(sc)sw.innerHTML=sceneSVG(sc,x);
    const P=plot({window:W,pieces:[{expr:it.fn,from:lo,to:hi}],xstep:it.xstep,ystep:it.ystep,autoTicks:it.autoTicks},false);
    const r=v=>Math.round(v*10)/10;
    gw.innerHTML=P.svg.replace('</svg>','<line class="n-v" x1="'+r(P.sx(x))+'" x2="'+r(P.sx(x))+'" y1="'+r(P.sy(Math.max(W[2],Math.min(W[3],0))))+'" y2="'+r(P.sy(F(x)))+'"/><circle class="n-p'+(done?' par':'')+'" cx="'+r(P.sx(x))+'" cy="'+r(P.sy(F(x)))+'" r="5.5"/></svg>');
    $('#or',ix).innerHTML='<span>'+fmt('$x$')+' = <b>'+fix(x,3)+'</b></span>'+(it.readout||[{label:it.yLabel||'Value',expr:it.fn}]).map(q=>'<span>'+fmt(q.label)+' = <b>'+sci(fn(q.expr)(x),5)+'</b>'+(q.unit?' '+esc(q.unit):'')+'</span>').join('');
  };
  $('#ox',ix).addEventListener('input',e=>{x=+e.target.value;
    if(Math.abs(x-it.best)<=tol){x=it.best;e.target.value=x;
      if(!done){done=true;drawAll();sayIn($('#ofb',ix),true,it.after||'That is the '+(goal==='max'?'largest':'smallest')+' value.');onChange();return;}}
    drawAll();});
  drawAll();
  return {kind:'pass',canGo:()=>done};
}

/* ---------- rr: related rates scenes driven by a time slider ---------- */
const RR={
  ladder:p=>({vars:[['x','bottom from wall','ft'],['y','top height','ft']],
    at:t=>{const x=p.x0+p.rate*t;return {x,y:Math.sqrt(Math.max(0,p.L*p.L-x*x))};},
    draw:(s)=>{const k=110/p.L,ox=60,oy=130;return '<line class="sc-line" x1="'+ox+'" y1="10" x2="'+ox+'" y2="'+oy+'"/><line class="sc-line" x1="'+ox+'" y1="'+oy+'" x2="310" y2="'+oy+'"/>'+
      '<line class="sc-lad" x1="'+(ox+s.x*k)+'" y1="'+oy+'" x2="'+ox+'" y2="'+(oy-s.y*k)+'"/><text class="sc-t" x="'+(ox+s.x*k/2)+'" y="'+(oy+14)+'" text-anchor="middle">x</text><text class="sc-t" x="'+(ox-6)+'" y="'+(oy-s.y*k/2)+'" text-anchor="end">y</text><text class="sc-t" x="'+(ox+s.x*k/2+8)+'" y="'+(oy-s.y*k/2-4)+'">'+p.L+'</text>';}}),
  ripple:p=>({vars:[['r','radius','cm'],['A','area','cm²']],
    at:t=>{const r=p.r0+p.rate*t;return {r,A:Math.PI*r*r};},
    draw:(s)=>{const k=60/p.rmax;return '<circle class="sc-water2" cx="160" cy="72" r="'+(s.r*k)+'"/><circle class="sc-line" fill="none" cx="160" cy="72" r="'+(s.r*k)+'"/><line class="sc-lad" x1="160" y1="72" x2="'+(160+s.r*k)+'" y2="72"/><text class="sc-t" x="'+(160+s.r*k/2)+'" y="66" text-anchor="middle">r</text>';}}),
  balloon:p=>({vars:[['V','volume','cm³'],['r','radius','cm']],
    at:t=>{const V=p.V0+p.rate*t;return {V,r:Math.cbrt(3*V/(4*Math.PI))};},
    draw:(s)=>{const k=60/p.rmax;return '<circle class="sc-fill" cx="160" cy="72" r="'+(s.r*k)+'"/><circle class="sc-line" fill="none" cx="160" cy="72" r="'+(s.r*k)+'"/><line class="sc-lad" x1="160" y1="72" x2="'+(160+s.r*k)+'" y2="72"/><text class="sc-t" x="'+(160+s.r*k/2)+'" y="66" text-anchor="middle">r</text>';}}),
  cone:p=>({vars:[['V','water volume','ft³'],['h','water depth','ft']],
    at:t=>{const V=Math.max(0,p.V0-p.rate*t);return {V,h:Math.cbrt(3*V*p.H*p.H/(Math.PI*p.R*p.R))};},
    draw:(s)=>{const k=120/p.H,top=12,cx=160,bot=top+p.H*k,wr=s.h*p.R/p.H*k,wy=bot-s.h*k;
      return '<path class="sc-water2" d="M'+(cx-wr)+' '+wy+' L'+cx+' '+bot+' L'+(cx+wr)+' '+wy+' Z"/><path class="sc-line" fill="none" d="M'+(cx-p.R*k)+' '+top+' L'+cx+' '+bot+' L'+(cx+p.R*k)+' '+top+'"/>'+
        '<line class="sc-dash" x1="'+(cx+p.R*k+14)+'" x2="'+(cx+p.R*k+14)+'" y1="'+wy+'" y2="'+bot+'"/><text class="sc-t" x="'+(cx+p.R*k+20)+'" y="'+((wy+bot)/2)+'">h</text>';}})
};
function mountRR(it,ix,onChange,host){
  const S=RR[it.scene](it),T=it.T,g=it.goal; let t=0,done=false;
  const sw=document.createElement('div');sw.className='gwrap scw';host.insertBefore(sw,ix);
  ix.innerHTML='<label class="slide-l" for="rt">'+fmt(it.pickText||'Drag to let time pass')+'</label><input type="range" id="rt" min="0" max="'+T+'" step="'+(T/600)+'" value="0">'+
    '<div class="rrtab"></div><div class="fb" id="rfb" hidden></div>';
  const rate=(v,tt)=>{const h=1e-4,a=S.at(Math.max(0,tt-h))[v],b=S.at(Math.min(T,tt+h))[v];return (b-a)/(Math.min(T,tt+h)-Math.max(0,tt-h));};
  const drawAll=()=>{const s=S.at(t);
    sw.innerHTML='<svg class="scene" viewBox="0 0 320 150">'+S.draw(s)+'</svg>';
    $('.rrtab',ix).innerHTML='<span></span><span>value</span><span>rate (per '+esc(it.unitT||'s')+')</span><span>'+fmt('$t$')+' <em>time</em></span><span>'+sci(t,4)+' '+esc(it.unitT||'s')+'</span><span></span>'+
      S.vars.map(([v,lab,u])=>'<span>'+fmt('$'+v+'$')+' <em>'+esc(lab)+'</em></span><span>'+sci(s[v],5)+' '+esc(u)+'</span><span>'+fmt('$frac{d'+v+'}{dt}$')+' = '+sci(rate(v,t),4)+'</span>').join('');
  };
  $('#rt',ix).addEventListener('input',e=>{t=+e.target.value;
    if(g&&!done){const v=S.at(t)[g.var];
      if(Math.abs(v-g.at)<=(g.tol||Math.abs(g.at)*0.01+0.01)){/* snap to the exact moment */
        let a=0,b=T;for(let k=0;k<60;k++){const m=(a+b)/2;((S.at(m)[g.var]-g.at)*(S.at(b)[g.var]-g.at)<=0)?a=m:b=m;}t=(a+b)/2;e.target.value=t;
        done=true;drawAll();sayIn($('#rfb',ix),true,(it.after||'Stopped at the moment you wanted.')+'');onChange();return;}}
    drawAll();});
  drawAll();
  return {kind:'pass',canGo:()=>done||!g};
}

/* ---------- curvex: slide along the curve; the tangent shows rising/falling and bending ---------- */
function mountCurvex(it,ix,onChange,host){
  const F=fn(it.fn),W=it.window,mode=it.mode||'slope',regs=it.regions||[],seen=new Set(); let x=it.start==null?W[0]+(W[1]-W[0])*0.1:it.start,done=!regs.length;
  const gw=document.createElement('div');gw.className='gwrap gw-s';host.insertBefore(gw,ix);
  const [lo,hi]=it.range||[W[0],W[1]];
  ix.innerHTML='<label class="slide-l" for="cx">'+fmt(it.pickText||'Drag to slide along the curve')+'</label><input type="range" id="cx" min="'+lo+'" max="'+hi+'" step="'+((hi-lo)/800)+'" value="'+x+'"><div class="read lread" id="crd"></div><div class="goals" id="cg"></div><div class="fb" id="cfb" hidden></div>';
  const drawAll=()=>{
    const P=plot({window:W,pieces:[],xstep:it.xstep,ystep:it.ystep},false),r=v=>Math.round(Math.max(-9999,Math.min(9999,v))*10)/10,X=t=>r(P.sx(t)),Y=t=>r(P.sy(t));
    const y=F(x),s=d1(F,x),c=d2(F,x),ok=Number.isFinite(y);
    let o='<g clip-path="url(#'+P.clip+')">';
    if(mode==='concave'){ /* color the curve by concavity */
      const N=300;let d={u:'',d:''},pen={u:false,d:false};
      for(let k=0;k<=N;k++){const t=W[0]+(W[1]-W[0])*k/N,v=F(t),cc=d2(F,t)>0?'u':'d';
        ['u','d'].forEach(q=>{if(q===cc&&Number.isFinite(v)&&v>W[2]-50&&v<W[3]+50){d[q]+=(pen[q]?'L':'M')+X(t)+' '+Y(v);pen[q]=true;}else pen[q]=false;});}
      o+='<path class="cx-u" d="'+d.u+'"/><path class="cx-d" d="'+d.d+'"/>';
    }else o+='<path class="g-curve" d="'+curvePath(F,P,W)+'"/>';
    if(ok)o+='<line class="cx-tan '+(mode==='concave'?'neutral':s>0?'up':'dn')+'" x1="'+X(W[0])+'" y1="'+Y(y+s*(W[0]-x))+'" x2="'+X(W[1])+'" y2="'+Y(y+s*(W[1]-x))+'"/>';
    o+='</g>'+(ok?'<circle class="n-p" cx="'+X(x)+'" cy="'+Y(y)+'" r="5.5"/>':'');
    gw.innerHTML=P.svg.replace('</svg>',o+'</svg>');
    const sgn=v=>Math.abs(v)<1e-6?'0':v>0?'positive':'negative';
    $('#crd',ix).innerHTML=ok?(mode==='slope'?'<span>'+fmt("$f'(x)$")+' = <b class="'+(s>0?'up':'dn')+'">'+sci(s,3)+'</b></span><span>'+(Math.abs(s)<1e-3?'flat tangent':s>0?'<b class="up">increasing ↗</b>':'<b class="dn">decreasing ↘</b>')+'</span>'
      :'<span>'+fmt("$f''(x)$")+' = <b>'+sci(c,3)+'</b></span><span>'+(Math.abs(c)<1e-3?'changing bend':c>0?'<b class="cu">concave up ∪</b> (curve above its tangent)':'<b class="cd">concave down ∩</b> (curve below its tangent)')+'</span>'):'<span>undefined here</span>';
    regs.forEach((g,i)=>{if(x>g[0]&&x<g[1])seen.add(i);});
    $('#cg',ix).innerHTML=regs.map((g,i)=>'<span class="goal'+(seen.has(i)?' on':'')+'">'+esc(g[2]||('('+nice(g[0])+', '+nice(g[1])+')'))+(seen.has(i)?' ✓':'')+'</span>').join('');
    if(!done&&seen.size===regs.length){done=true;sayIn($('#cfb',ix),true,it.after||'You visited every region.');onChange();}
  };
  $('#cx',ix).addEventListener('input',e=>{x=+e.target.value;drawAll();});
  drawAll();
  return {kind:'pass',canGo:()=>done};
}

/* ---------- ratio: close in on a limit and watch the two parts fight ---------- */
function mountRatio(it,ix,onChange,host){
  const f=fn(it.f),g=fn(it.g),op=it.op||'/',a=it.a,dir=it.dir||1,inf=!!it.inf,goal=it.goal||5,rows=[];
  const comb=(p,q)=>op==='/'?p/q:op==='*'?p*q:op==='-'?p-q:op==='^'?Math.pow(p,q):p+q;
  const opT={'/':'f(x) / g(x)','*':'f(x) · g(x)','-':'f(x) − g(x)','^':'f(x)^g(x)'}[op];
  let k=0,done=false;
  const gw=document.createElement('div');gw.className='gwrap gw-s';if(!inf&&it.graph!==false)host.insertBefore(gw,ix);
  ix.innerHTML='<div class="row nrow"><button class="btn small" id="rcl">'+esc(inf?'Make x bigger (×10)':'Move closer (10× closer)')+'</button></div><div class="ntab rtab"></div><div class="fb" id="rafb" hidden></div>';
  const xAt=k=>inf?(it.start||10)*Math.pow(10,k):a+dir*(it.start||1)*Math.pow(10,-k);
  const drawAll=()=>{
    const x=xAt(k);
    if(!inf&&it.graph!==false){const h=Math.abs(x-a)*2.5,V0=[a-h,a+h];let lo=Infinity,hi=-Infinity;
      for(let j=0;j<=100;j++){const t=V0[0]+(V0[1]-V0[0])*j/100;[f(t),g(t)].forEach(v=>{if(Number.isFinite(v)){lo=Math.min(lo,v);hi=Math.max(hi,v);}});}
      const pad=(hi-lo)*0.15||1,V=[V0[0],V0[1],Math.min(lo-pad,0),Math.max(hi+pad,0)];
      const P=plot({window:V,pieces:[],autoTicks:true},false);
      gw.innerHTML=P.svg.replace('</svg>','<g clip-path="url(#'+P.clip+')"><path class="g-curve" d="'+curvePath(f,P,V)+'"/><path class="ra-g" d="'+curvePath(g,P,V)+'"/></g>'+
        '<text class="ra-l f" x="20" y="28">f(x) = '+esc(it.fl||it.f)+'</text><text class="ra-l g" x="20" y="44">g(x) = '+esc(it.gl||it.g)+'</text></svg>');}
    $('.rtab',ix).innerHTML='<span>'+fmt('$x$')+'</span><span>'+fmt('$f(x)$')+'</span><span>'+fmt('$g(x)$')+'</span><span>'+esc(opT)+'</span>'+
      rows.map(q=>'<span>'+sci(q[0],7)+'</span><span>'+sci(q[1],4)+'</span><span>'+sci(q[2],4)+'</span><span><b>'+sci(q[3],6)+'</b></span>').join('');
  };
  const add=()=>{const x=xAt(k);rows.push([x,f(x),g(x),comb(f(x),g(x))]);};
  add();
  $('#rcl',ix).onclick=()=>{ if(rows.length>goal+2)return; k++;add();drawAll();
    if(!done&&rows.length>goal){done=true;sayIn($('#rafb',ix),true,it.after||'The last column has settled down.');onChange();} };
  drawAll();
  return {kind:'pass',canGo:()=>done};
}
