/* Fills in the answer of every graph question whose answer is null, by reading the graph the way the app does.
   node tools/gen/graphtruth.js decks/<id>.json */
const fs=require('fs'),path=require('path'),root=path.join(__dirname,'..','..');
const app=fs.readFileSync(path.join(root,'js/app.js'),'utf8');
const grab=(a,b)=>app.slice(app.indexOf(a),app.indexOf(b));
eval(grab('const DEG=','/* ---------- graph drawing'));
const file=process.argv[2],D=JSON.parse(fs.readFileSync(file,'utf8'));let n=0;
const visit=q=>{if(q.type==='graph'&&q.answer==null){const t=truth(D.graphs[q.graph],q);q.answer=typeof t==='number'?Math.round(t*1e6)/1e6:t;n++;}(q.steps||[]).forEach(visit);};
for(const L of [D.lesson,...(D.lessons||[])])if(L)L.slides.forEach(visit);
Object.values(D.drills).forEach(d=>d.questions.forEach(visit));
fs.writeFileSync(file,JSON.stringify(D,null,1)+'\n');
console.log(file+': filled '+n+' graph answers');
