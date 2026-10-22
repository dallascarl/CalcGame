/* CalcGame engine, part 3: explorers added for World 2 (Derivatives).
   secant  - slide the second point toward the first and watch the secant slope settle on f'(a)
   dtrace  - slide along a curve; every slope you visit is dropped as a dot on a second graph,
             so the graph of f' appears underneath as you go
   This file loads after items.js and before app.js. */

/* ---------- secant: from the slope of a secant line to the slope of the tangent line ---------- */
/* { "type":"secant", "fn":"x^2", "a":1, "window":[x0,x1,y0,y1], "h":1 (starting gap), "goal":0.01,
     "left": true (also offer h < 0), "after":"text shown at the end ({m} is the slope found)" } */
function mountSecant(it,ix,onChange,host){
  const F=fn(it.fn),a=it.a,W=it.window,h0=Math.abs(it.h||1),goal=it.goal||0.01,fa=F(a),rows=[]; let s=0,sign=(it.h||1)<0?-1:1,done=false;
  const gw=document.createElement('div');gw.className='gwrap gw-s';host.insertBefore(gw,ix);
  ix.innerHTML='<label class="slide-l" for="sh">'+fmt('Slide to shrink the gap $h$ between the two points')+'</label>'+
    '<input type="range" id="sh" min="0" max="1" step="0.002" value="0">'+
    (it.left?'<div class="row"><button class="btn small ghost" id="sside">'+(sign>0?'Come from the left (h < 0)':'Come from the right (h > 0)')+'</button></div>':'')+
    '<div class="sec-read" id="srd"></div><table class="sec-tab"><thead><tr><th>h</th><th>slope of the secant</th></tr></thead><tbody id="stb"></tbody></table><div class="fb" id="sfb" hidden></div>';
  const hNow=()=>sign*h0*Math.pow(10,-3*s);   /* s = 0 → h0, s = 1 → h0/1000 */
  const draw=()=>{
    const h=hNow(),b=a+h,fb=F(b),m=(fb-fa)/h;
    const P=plot({window:W,pieces:[],xstep:it.xstep,ystep:it.ystep},false),r=v=>Math.round(Math.max(-9999,Math.min(9999,v))*10)/10,X=t=>r(P.sx(t)),Y=t=>r(P.sy(t));
    let o='<g clip-path="url(#'+P.clip+')"><path class="g-curve" d="'+curvePath(F,P,W)+'"/>'+
      '<line class="g-sec" x1="'+X(W[0])+'" y1="'+Y(fa+m*(W[0]-a))+'" x2="'+X(W[1])+'" y2="'+Y(fa+m*(W[1]-a))+'"/></g>'+
      '<circle class="g-pa" cx="'+X(a)+'" cy="'+Y(fa)+'" r="5"/><circle class="g-pb" cx="'+X(b)+'" cy="'+Y(fb)+'" r="5"/>';
    gw.innerHTML=P.svg.replace('</svg>',o+'</svg>');
    $('#srd',ix).innerHTML='<span>'+fmt('$h$')+'</span><b>'+sci(h,4)+'</b><span>'+fmt('slope = $frac{f(a+h) - f(a)}{h}$')+'</span><b>'+sci(m,6)+'</b>';
    /* keep a row each time h passes a power of ten, like a table on the board */
    const k=Math.floor(-Math.log10(Math.abs(h)/h0)+1e-9);
    if(!rows.some(q=>q.k===k&&q.sign===sign)){rows.push({k,sign,h,m});rows.sort((p,q)=>q.sign-p.sign||p.k-q.k);
      $('#stb',ix).innerHTML=rows.map(q=>'<tr><td>'+sci(q.h,4)+'</td><td>'+sci(q.m,6)+'</td></tr>').join('');}
    if(!done&&Math.abs(h)<=goal+1e-12){done=true;
      sayIn($('#sfb',ix),true,(it.after||'The secant slopes settle on one number, about {m}. That number is the slope of the tangent line: the derivative.').replace('{m}',sci(m,4)));onChange();}
  };
  $('#sh',ix).addEventListener('input',e=>{s=+e.target.value;draw();});
  if($('#sside',ix))$('#sside',ix).onclick=e=>{sign=-sign;e.target.textContent=sign>0?'Come from the left (h < 0)':'Come from the right (h > 0)';draw();};
  draw();
  return {kind:'pass',canGo:()=>done};
}

/* ---------- dtrace: build the graph of f' from the slopes of f ---------- */
/* { "type":"dtrace", "fn":"x^3-3*x", "window":[x0,x1,y0,y1] for f, "dwindow":[y0,y1] for f',
     "cover":0.85 (how much of the x-range to visit), "after":"..." } */
function mountDtrace(it,ix,onChange,host){
  const F=fn(it.fn),W=it.window,DW=[W[0],W[1]].concat(it.dwindow||[W[2],W[3]]),bins=40,hit=new Set(),dots=[];
  let x=it.start==null?W[0]+(W[1]-W[0])*0.05:it.start,done=false;
  const g1=document.createElement('div');g1.className='gwrap gw-s';host.insertBefore(g1,ix);
  const cap1=document.createElement('p');cap1.className='gw-cap';cap1.innerHTML=fmt('the graph of $f$');host.insertBefore(cap1,ix);
  const g2=document.createElement('div');g2.className='gwrap gw-s';host.insertBefore(g2,ix);
  const cap2=document.createElement('p');cap2.className='gw-cap';cap2.innerHTML=fmt("the graph of $f'$: one dot for each slope you visit");host.insertBefore(cap2,ix);
  ix.innerHTML='<label class="slide-l" for="dtx">'+fmt(it.pickText||'Drag to slide along the curve')+'</label><input type="range" id="dtx" min="'+W[0]+'" max="'+W[1]+'" step="'+((W[1]-W[0])/600)+'" value="'+x+'">'+
    '<div class="read lread" id="dtr"></div><div class="fb" id="dtfb" hidden></div>';
  const r=v=>Math.round(Math.max(-9999,Math.min(9999,v))*10)/10;
  const draw=()=>{
    const y=F(x),s=d1(F,x),ok=Number.isFinite(y)&&Number.isFinite(s);
    if(ok){const b=Math.min(bins-1,Math.floor(bins*(x-W[0])/(W[1]-W[0])));if(!hit.has(b)){hit.add(b);dots.push([x,s]);}}
    const P=plot({window:W,pieces:[],xstep:it.xstep,ystep:it.ystep},false),X=t=>r(P.sx(t)),Y=t=>r(P.sy(t));
    let o='<g clip-path="url(#'+P.clip+')"><path class="g-curve" d="'+curvePath(F,P,W)+'"/>';
    if(ok)o+='<line class="cx-tan '+(s>0?'up':'dn')+'" x1="'+X(W[0])+'" y1="'+Y(y+s*(W[0]-x))+'" x2="'+X(W[1])+'" y2="'+Y(y+s*(W[1]-x))+'"/>';
    o+='</g>'+(ok?'<circle class="n-p" cx="'+X(x)+'" cy="'+Y(y)+'" r="5.5"/>':'');
    g1.innerHTML=P.svg.replace('</svg>',o+'</svg>');
    const Q=plot({window:DW,pieces:[],xstep:it.xstep,ystep:it.dstep},false),X2=t=>r(Q.sx(t)),Y2=t=>r(Q.sy(t));
    let o2='<g clip-path="url(#'+Q.clip+')">'+(done?'<path class="dt-true" d="'+curvePath(t=>d1(F,t),Q,DW)+'"/>':'');
    dots.forEach(([u,v])=>{o2+='<circle class="dt-dot" cx="'+X2(u)+'" cy="'+Y2(v)+'" r="3.2"/>';});
    if(ok)o2+='<line class="g-guide" x1="'+X2(x)+'" x2="'+X2(x)+'" y1="'+Y2(DW[2])+'" y2="'+Y2(DW[3])+'"/>';
    g2.innerHTML=Q.svg.replace('</svg>',o2+'</g></svg>');
    $('#dtr',ix).innerHTML=ok?'<span>'+fmt("slope $f'(x)$")+' = <b class="'+(s>0?'up':'dn')+'">'+sci(s,3)+'</b></span><span>'+(Math.abs(s)<0.05?'flat: '+fmt("$f'$")+' crosses 0':s>0?'<b class="up">rising, so '+fmt("$f'$")+' is above the axis</b>':'<b class="dn">falling, so '+fmt("$f'$")+' is below the axis</b>')+'</span>':'<span>undefined here</span>';
    if(!done&&hit.size>=Math.ceil((it.cover||0.85)*bins)){done=true;draw();
      sayIn($('#dtfb',ix),true,it.after||"Those dots are the graph of $f'$. The dashed curve is the exact derivative.");onChange();}
  };
  $('#dtx',ix).addEventListener('input',e=>{x=+e.target.value;draw();});
  draw();
  return {kind:'pass',canGo:()=>done};
}
