/* Checks every formula answer in tools/gen/out/*.manifest.json with the app's own parser (js/items.js),
   against the true values computed by the generator. Run: node tools/gen/verify.js */
const fs=require('fs'),path=require('path'),root=path.join(__dirname,'..','..');
const app=fs.readFileSync(path.join(root,'js/app.js'),'utf8'),items=fs.readFileSync(path.join(root,'js/items.js'),'utf8');
const grab=(src,a,b)=>src.slice(src.indexOf(a),src.indexOf(b));
eval(grab(app,'function rpow','function compile'));
eval(grab(items,'const XFN','const closeParens'));
let bad=0,n=0;
for(const f of fs.readdirSync(path.join(__dirname,'out')).filter(f=>f.endsWith('.manifest.json'))){
  for(const m of JSON.parse(fs.readFileSync(path.join(__dirname,'out',f),'utf8'))){
    n++; let F;
    try{F=xcompile(m.answer,m.vars);}catch(e){bad++;console.log('PARSE',m.deck,m.id,JSON.stringify(m.answer),e.message);continue;}
    let c=null;
    for(const [env,want] of m.samples){let got=F(env);
      if(m.upToC){if(c==null)c=got-want;got-=c;}
      if(!(Math.abs(got-want)<=1e-6*Math.max(1,Math.abs(want)))){bad++;console.log('WRONG',m.deck,m.id,JSON.stringify(m.answer),JSON.stringify(env),'got',got,'want',want);break;}}
  }
}
console.log(n+' answers checked, '+bad+' problems');
process.exit(bad?1:0);
