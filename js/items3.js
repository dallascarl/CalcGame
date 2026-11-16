/* CalcGame engine, part 4: item types added for World 0 (The Toolkit).
   cancel    - tap a factor on top and the same factor on the bottom to cancel them (or say nothing cancels)
   transform - shift, flip and stretch a graph until it lies on the dashed target
   ucircle   - the unit circle: explore it, tap one angle, or tap every angle that solves an equation
   This file loads after items2.js and before app.js. */

/* ---------- cancel: what is allowed to cancel in a fraction ---------- */
/* { "type":"cancel", "top":{"op":"*","parts":["2","x","(x + 3)"]}, "bot":{"op":"*","parts":["x","(x - 1)"]} }
   op "*": the parts are factors (drawn side by side). op "+": the parts are terms and carry their signs ("x^2", "+ 3x").
   Only a factor of the whole top cancels with the same factor of the whole bottom, so the answer is worked out
   from the data: every matching pair when both sides are products, and nothing at all otherwise. */
function cancelPairs(q){
  if(q.top.op!=='*'||q.bot.op!=='*')return [];
  const used=new Set(),out=[];
  q.top.parts.forEach((t,i)=>{const j=q.bot.parts.findIndex((b,k)=>b===t&&!used.has(k));if(j>=0){used.add(j);out.push([i,j]);}});
  return out;
}
function cancelSide(side,cut){
  const left=side.parts.filter((p,i)=>!cut.has(i));
  if(!left.length)return '1';
  return side.op==='*'?left.join(''):left.join(' ').replace(/^\+ /,'');
}
/* the simplified fraction, in math markup */
function cancelResult(q,pairs){
  const T=new Set(pairs.map(p=>p[0])),B=new Set(pairs.map(p=>p[1])),t=cancelSide(q.top,T),b=cancelSide(q.bot,B);
  return b==='1'?t:'frac{'+t+'}{'+b+'}';
}
function cancelAnswer(q){const P=cancelPairs(q);return P.length?'$'+cancelResult(q,P)+'$':'nothing cancels';}
function mountCancel(q,ix,onChange){
  const legal=cancelPairs(q); let pairs=[],pick=null,none=false,locked=false,shown=null,tried=false;
  ix.innerHTML='<div class="cfrac" role="group" aria-label="Fraction: tap a piece on top, then the same piece on the bottom"></div>'+
    '<p class="tiny chow">Tap a piece on top, then the matching piece on the bottom, to cancel them. Tap a crossed-out piece to put it back.</p>'+
    '<div class="row"><button class="btn small ghost cnone" aria-pressed="false">Nothing cancels</button></div><div class="cres" hidden></div>';
  const box=$('.cfrac',ix),nb=$('.cnone',ix),res=$('.cres',ix);
  const side=(s,name)=>'<div class="cside c'+s.op.charCodeAt(0)+'">'+s.parts.map((p,i)=>{
      const use=shown||pairs,k=use.findIndex(pr=>pr[name==='t'?0:1]===i);
      const sg=s.op!=='*'&&i?/^\s*([+\-−])\s*(.+)$/.exec(p):null; if(sg)p=sg[2];
      return (s.op==='*'&&i?'<span class="cdot" aria-hidden="true">·</span>':sg?'<span class="cdot" aria-hidden="true">'+(sg[1]==='+'?'+':'−')+'</span>':'')+'<button class="cchip'+(k>=0?' cut c'+(k%4):'')+(pick&&pick.s===name&&pick.i===i?' on':'')+'" data-s="'+name+'" data-i="'+i+'"'+(locked?' disabled':'')+
        ' aria-pressed="'+(k>=0)+'">'+math(p)+'</button>';}).join('')+'</div>';
  const draw=()=>{box.innerHTML=side(q.top,'t')+'<div class="cbar"></div>'+side(q.bot,'b');nb.setAttribute('aria-pressed',none);nb.disabled=locked;};
  box.addEventListener('click',e=>{
    const b=e.target.closest('.cchip'); if(!b||locked)return;
    const s=b.dataset.s,i=+b.dataset.i,k=pairs.findIndex(pr=>pr[s==='t'?0:1]===i);
    if(k>=0){pairs.splice(k,1);pick=null;}
    else if(!pick||pick.s===s)pick={s,i};
    else{const t=s==='t'?i:pick.i,bt=s==='b'?i:pick.i;
      if(q.top.parts[t]===q.bot.parts[bt]){pairs.push([t,bt]);none=false;}
      else if(typeof toast==='function')toast('Those two pieces are not the same.');
      pick=null;}
    draw();onChange();
  });
  nb.onclick=()=>{if(locked)return;none=!none;if(none){pairs=[];pick=null;}draw();onChange();};
  draw();
  const good=()=>none?!legal.length:(q.top.op==='*'&&q.bot.op==='*'&&pairs.length===legal.length);
  const why=()=>{
    if(good())return '';
    if(q.top.op==='+'||q.bot.op==='+'){const w=q.top.op==='+'&&q.bot.op==='+'?'top and the bottom are sums':q.top.op==='+'?'top is a sum':'bottom is a sum';
      return 'Only **factors** cancel: pieces that multiply the whole top and the whole bottom. Here the '+w+', so those pieces are **terms**, and terms never cancel.';}
    return legal.length?'Every factor that appears on both the top and the bottom cancels. Look again for a matching pair.':'No factor on top matches a factor on the bottom, so nothing cancels.';
  };
  return {kind:'q',canGo:()=>none||pairs.length>0,
    check:()=>{tried=true;return good();},
    summary:()=>good()?'':why(),
    lock(final,ok){locked=true;if(final){shown=legal;res.hidden=false;
        res.innerHTML=fmt(legal.length?'What is left: $'+cancelResult(q,legal)+'$':'Nothing cancels. The fraction stays as it is.');}
      box.classList.add(ok?'is-right':'is-wrong');draw();},
    reset(){locked=false;pairs=[];pick=null;none=false;shown=null;res.hidden=true;box.classList.remove('is-right','is-wrong');draw();onChange();}};
}

/* ---------- transform: move a graph onto its target ---------- */
/* { "type":"transform", "base":"x^2", "window":[-6,6,-6,6], "target":{"h":2,"k":-3,"a":1},
     "controls":["h","k"] (add "flip" and "stretch" to use them), "name":"f", "start":{"h":0,"k":0,"a":1} }
   The student's curve is y = a·f(x - h) + k. Stretch cycles 1, 2, 1/2. */
function tfLabel(S,name){
  const a=S.a,h=S.h,k=S.k,n=v=>neg(String(v)),A=a===1?'':a===-1?'-':a===0.5?'frac{1}{2}':a===-0.5?'-frac{1}{2}':String(a);
  return 'y = '+A+(name||'f')+'(x'+(h?(h>0?' - '+h:' + '+(-h)):'')+')'+(k?(k>0?' + '+k:' - '+(-k)):'');
}
function mountTransform(q,ix,onChange,host){
  const F=fn(q.base),W=q.window,T=Object.assign({h:0,k:0,a:1},q.target),ctl=q.controls||['h','k'],st0=Object.assign({h:0,k:0,a:1},q.start||{});
  let S=Object.assign({},st0),locked=false,state='';
  const gw=document.createElement('div');gw.className='gwrap gw-s';host.insertBefore(gw,ix);
  const B=(id,lab,aria)=>'<button class="key tkey" data-t="'+id+'" aria-label="'+aria+'">'+lab+'</button>';
  ix.innerHTML='<div class="tread" aria-live="polite"></div><div class="tctl">'+
    (ctl.includes('h')?'<div class="tgrp"><span class="kick">Left / right</span><div>'+B('h-','←','Shift left')+B('h+','→','Shift right')+'</div></div>':'')+
    (ctl.includes('k')?'<div class="tgrp"><span class="kick">Up / down</span><div>'+B('k-','↓','Shift down')+B('k+','↑','Shift up')+'</div></div>':'')+
    (ctl.includes('flip')?'<div class="tgrp"><span class="kick">Flip</span><div>'+B('flip','⇅','Flip over the x-axis')+'</div></div>':'')+
    (ctl.includes('stretch')?'<div class="tgrp"><span class="kick">Stretch</span><div>'+B('st','×2 / ×½','Change the vertical stretch')+'</div></div>':'')+'</div>'+
    '<p class="tiny">'+fmt('Dashed: the target. Solid: your graph. Move yours until it sits on the target.')+'</p>';
  const G=(P,s)=>t=>s.a*F(t-s.h)+s.k;
  const draw=()=>{
    const P=plot({window:W,pieces:[],xstep:q.xstep,ystep:q.ystep},false);
    const o='<g clip-path="url(#'+P.clip+')"><path class="g-curve g-dash tf-t" d="'+curvePath(G(P,T),P,W,240)+'"/><path class="g-curve'+(state?' tf-'+state:'')+'" d="'+curvePath(G(P,S),P,W,240)+'"/></g>';
    gw.innerHTML=P.svg.replace('</svg>',o+'</svg>');
    $('.tread',ix).innerHTML=fmt('Your graph: $'+tfLabel(S,q.name)+'$');
  };
  const lim=(v,lo,hi)=>Math.max(lo,Math.min(hi,v));
  ix.addEventListener('click',e=>{
    const b=e.target.closest('.tkey'); if(!b||locked)return; const t=b.dataset.t;
    if(t==='h-')S.h=lim(S.h-1,W[0]+1,W[1]-1); else if(t==='h+')S.h=lim(S.h+1,W[0]+1,W[1]-1);
    else if(t==='k-')S.k=lim(S.k-1,W[2]+1,W[3]-1); else if(t==='k+')S.k=lim(S.k+1,W[2]+1,W[3]-1);
    else if(t==='flip')S.a=-S.a;
    else if(t==='st'){const m=Math.abs(S.a),s=S.a<0?-1:1;S.a=s*(m===1?2:m===2?0.5:1);}
    draw();onChange();
  });
  draw();
  const moved=()=>S.h!==st0.h||S.k!==st0.k||S.a!==st0.a;
  return {kind:'q',canGo:()=>moved()||(T.h===st0.h&&T.k===st0.k&&T.a===st0.a),
    check:()=>S.h===T.h&&S.k===T.k&&S.a===T.a,
    summary:()=>'The target is $'+tfLabel(T,q.name)+'$.',
    lock(final,ok){locked=true;state=ok?'ok':'no';if(final&&!ok)S=Object.assign({},T);draw();ix.querySelectorAll('.tkey').forEach(b=>{b.disabled=true;});},
    reset(){locked=false;state='';ix.querySelectorAll('.tkey').forEach(b=>{b.disabled=false;});draw();onChange();}};
}
function transformAnswer(q){return '$'+tfLabel(Object.assign({h:0,k:0,a:1},q.target),q.name)+'$';}

/* ---------- ucircle: the unit circle with its 16 standard angles ---------- */
/* { "type":"ucircle", "ask":"explore", "need":[1,2,3], "after":"..." }      visit those angles (index 0 = 0, 1 = π/6, 2 = π/4, ...)
   { "type":"ucircle", "ask":"angle", "answer":7 }                           tap one angle (here 5π/6); no labels are shown
   { "type":"ucircle", "ask":"where", "answers":[1,7] }                      tap every angle that works (e.g. sin θ = 1/2)
   "labels": true shows the angle names on the picture; "coords": true shows (cos θ, sin θ) after the answer. */
const UC=(()=>{
  const fr=[[0,1],[1,6],[1,4],[1,3],[1,2],[2,3],[3,4],[5,6],[1,1],[7,6],[5,4],[4,3],[3,2],[5,3],[7,4],[11,6]];
  const ex=v=>{const a=Math.abs(v),s=v<-1e-9?'-':'';
    return a<1e-9?'0':Math.abs(a-1)<1e-9?s+'1':Math.abs(a-0.5)<1e-9?s+'frac{1}{2}':Math.abs(a-Math.SQRT1_2)<1e-9?s+'frac{sqrt2}{2}':s+'frac{sqrt3}{2}';};
  return fr.map(([n,d],i)=>{const t=Math.PI*n/d;
    return {i,t,deg:Math.round(180*n/d),lab:n===0?'0':d===1?(n===1?'pi':n+'pi'):'frac{'+(n===1?'':n)+'pi}{'+d+'}',
      short:n===0?'0':d===1?(n===1?'π':n+'π'):(n===1?'':n)+'π/'+d,c:ex(Math.cos(t)),s:ex(Math.sin(t)),x:Math.cos(t),y:Math.sin(t)};});
})();
function ucAnswer(q){
  if(q.ask==='angle')return '$theta = '+UC[q.answer].lab+'$';
  if(q.ask==='where')return q.answers.length?'$theta = $ '+q.answers.map(i=>'$'+UC[i].lab+'$').join(' and '):'none of them';
  return '';
}
function mountUcircle(q,ix,onChange,host){
  const ask=q.ask||'explore',need=q.need||[],seen=new Set(); let sel=ask==='where'?new Set():null,cur=null,locked=false,marks=null;
  const gw=document.createElement('div');gw.className='gwrap ucw';host.insertBefore(gw,ix);
  ix.innerHTML='<div class="ucread" aria-live="polite"></div>'+(ask==='explore'&&need.length?'<div class="goals ucgoals"></div>':'')+(ask==='explore'?'<div class="fb good" id="ucafter" hidden></div>':'');
  const C=160,R=112,X=p=>(C+R*p.x).toFixed(1),Y=p=>(C-R*p.y).toFixed(1);
  const draw=()=>{
    let s='<svg class="graph uc" viewBox="0 0 320 320" role="group" aria-label="The unit circle"><rect class="g-bg" x="2" y="2" width="316" height="316" rx="10"/>'+
      '<line class="g-axis" x1="18" x2="302" y1="'+C+'" y2="'+C+'"/><line class="g-axis" x1="'+C+'" x2="'+C+'" y1="18" y2="302"/><circle class="uc-c" cx="'+C+'" cy="'+C+'" r="'+R+'"/>'+
      (q.labels?'':'<text class="g-t" x="'+(C+R+6)+'" y="'+(C+13)+'">1</text><text class="g-t" x="'+(C+5)+'" y="'+(C-R-5)+'">1</text>');
    const p=cur!=null?UC[cur]:null;
    if(p){ /* the triangle: cos θ along the axis, sin θ straight up */
      s+='<line class="uc-cos" x1="'+C+'" y1="'+C+'" x2="'+X(p)+'" y2="'+C+'"/><line class="uc-sin" x1="'+X(p)+'" y1="'+C+'" x2="'+X(p)+'" y2="'+Y(p)+'"/>'+
         '<line class="uc-r" x1="'+C+'" y1="'+C+'" x2="'+X(p)+'" y2="'+Y(p)+'"/>';
      if(p.t>0){const r=24,big=p.t>Math.PI?1:0;s+='<path class="uc-arc" d="M'+(C+r)+' '+C+'A'+r+' '+r+' 0 '+big+' 0 '+(C+r*p.x).toFixed(1)+' '+(C-r*p.y).toFixed(1)+'"/>';}
    }
    UC.forEach(a=>{
      const on=sel?sel.has(a.i):cur===a.i,mk=marks?marks[a.i]:'';
      s+='<g class="uc-pt'+(on?' on':'')+(mk?' '+mk:'')+(seen.has(a.i)&&ask==='explore'?' seen':'')+'" data-a="'+a.i+'" role="button" tabindex="0" aria-label="'+(q.labels||ask==='explore'?a.short+', '+a.deg+' degrees':'point '+(a.i+1))+'" aria-pressed="'+on+'">'+
        '<circle class="uc-hit" cx="'+X(a)+'" cy="'+Y(a)+'" r="15"/><circle class="uc-dot" cx="'+X(a)+'" cy="'+Y(a)+'" r="7"/></g>';
      if(q.labels){const ax=Math.abs(a.x)<1e-9,ay=Math.abs(a.y)<1e-9,lx=C+(R+(ay?20:22))*a.x+(ax?15:0),ly=C-(R+(ax?14:19))*a.y+4-(ay?10:0);s+='<text class="uc-lab" text-anchor="middle" x="'+lx.toFixed(1)+'" y="'+ly.toFixed(1)+'">'+a.short+'</text>';}
    });
    gw.innerHTML=s+'</svg>';
    const rd=$('.ucread',ix);
    if(ask==='explore'||(locked&&q.coords!==false&&p))rd.innerHTML=p?'<span>'+fmt('$theta = '+p.lab+'$')+' <i class="tiny">('+p.deg+'°)</i></span><span class="uc-cs">'+fmt('$cos theta = '+p.c+'$')+'</span><span class="uc-sn">'+fmt('$sin theta = '+p.s+'$')+'</span>':'<span class="tiny">Tap a point on the circle.</span>';
    else rd.innerHTML=sel?'<span class="tiny">'+(sel.size?sel.size+' selected. Tap again to remove one.':'Tap every point that works.')+'</span>':'<span class="tiny">'+(cur==null?'Tap the point.':'Tap another point to change your answer.')+'</span>';
    const g=$('.ucgoals',ix); if(g)g.innerHTML=need.map(i=>'<span class="goal'+(seen.has(i)?' on':'')+'">'+math(UC[i].lab)+'</span>').join('');
  };
  const tap=i=>{ if(locked)return;
    if(sel){sel.has(i)?sel.delete(i):sel.add(i);cur=i;} else cur=i;
    seen.add(i); draw();
    if(ask==='explore'&&q.after&&need.every(k=>seen.has(k))){const af=$('#ucafter',ix);if(af.hidden){af.hidden=false;af.innerHTML='<span>'+fmt(q.after)+'</span>';af.scrollIntoView({block:'nearest'});}}
    onChange(); };
  gw.addEventListener('click',e=>{const g=e.target.closest('.uc-pt');if(g)tap(+g.dataset.a);});
  gw.addEventListener('keydown',e=>{const g=e.target.closest('.uc-pt');if(g&&(e.key==='Enter'||e.key===' ')){tap(+g.dataset.a);e.preventDefault();e.stopPropagation();}});
  draw();
  if(ask==='explore')return {kind:'pass',canGo:()=>need.length?need.every(k=>seen.has(k)):seen.size>0};
  const right=()=>sel?(sel.size===q.answers.length&&q.answers.every(i=>sel.has(i))):cur===q.answer;
  return {kind:'q',canGo:()=>sel?sel.size>0:cur!=null,check:right,
    lock(final,ok){locked=true;marks={};
      if(sel){sel.forEach(i=>{marks[i]=q.answers.includes(i)?'ok':'no';});if(final)q.answers.forEach(i=>{if(!sel.has(i))marks[i]='miss';});}
      else{marks[cur]=ok?'ok':'no';if(final&&!ok){marks[q.answer]='miss';}}
      draw();},
    reset(){locked=false;marks=null;if(sel)sel=new Set();cur=null;draw();onChange();}};
}
