/* helper for shorten.py: which candidate wrong answers really are wrong, judged by the app's own parser */
const fs=require('fs'),path=require('path'),root=path.join(__dirname,'..','..');
const app=fs.readFileSync(path.join(root,'js/app.js'),'utf8'),items=fs.readFileSync(path.join(root,'js/items.js'),'utf8');
const grab=(src,a,b)=>src.slice(src.indexOf(a),src.indexOf(b));
eval(grab(app,'function rpow','function compile'));
eval(grab(items,'const XFN','const closeParens'));
const jobs=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),out={};
let seed=7;const rnd=()=>{seed=(seed*1103515245+12345)%2147483648;return seed/2147483648;};
for(const [key,j] of Object.entries(jobs)){
  const vars=j.vars&&j.vars.length?j.vars:['x'];let T;
  try{T=xcompile(j.answer,vars);}catch(e){out[key]={err:e.message};continue;}
  let envs,tv;
  for(const dflt of [[0.4,1.3],[0.05,0.3],[1.2,2.5]]){
    envs=[];for(let k=0;k<5;k++){const e={};for(const v of vars){const r=(j.ranges||{})[v]||dflt;e[v]=r[0]+(r[1]-r[0])*(0.15+0.7*rnd());}envs.push(e);}
    tv=envs.map(e=>T(e)); if(tv.every(Number.isFinite))break;}
  if(!tv.every(Number.isFinite)){out[key]={err:'truth not finite'};continue;}
  const good=[],sigs=[tv.map(v=>v.toPrecision(6)).join()];
  j.cands.forEach((c,i)=>{let F;try{F=xcompile(c,vars);}catch(e){return;}
    let v;try{v=envs.map(e=>F(e));}catch(e){return;} if(!v.every(Number.isFinite))return;
    const d=v.map((x,k)=>x-tv[k]),scale=Math.max(1,...tv.map(Math.abs));
    const same=j.upToC?d.every(x=>Math.abs(x-d[0])<1e-6*scale):d.every(x=>Math.abs(x)<1e-6*scale);
    if(same)return; const sig=(j.upToC?d.map(x=>x-d[0]):v).map(x=>x.toPrecision(6)).join();
    if(sigs.includes(sig))return; sigs.push(sig); good.push(i);});
  out[key]={good};
}
fs.writeFileSync(process.argv[3],JSON.stringify(out));
