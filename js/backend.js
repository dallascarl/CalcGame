/* CalcGame backend: one interface, two implementations.
   - Supabase, when js/config.js has a URL and key.
   - A local mock (everything in this browser) when the page is opened with ?mock=1, for testing.
   Used by the student app (index.html) and the instructor page (instructor.html). */

const CFG=Object.assign({supabaseUrl:'',supabaseKey:'',userDomain:'users.calcgame.app'},window.CALCGAME_CONFIG||{});
const USERNAME_RE=/^[A-Za-z0-9_]{3,20}$/;
const userEmail=u=>u.trim().toLowerCase()+'@'+CFG.userDomain;

function loadScript(src){return new Promise((ok,no)=>{const s=document.createElement('script');s.src=src;s.onload=ok;s.onerror=()=>no(Error('Could not load '+src));document.head.appendChild(s);});}
const SB_LIB='https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js';

/* turn database errors into sentences a student can act on */
function niceErr(e){
  const m=(e&&(e.message||e.error_description||e.msg))||String(e);
  if(/Invalid login credentials/i.test(m))return 'That username and password do not match.';
  if(/already registered|already been registered|profiles_username_lower|duplicate key/i.test(m))return 'That username is taken. Try another.';
  if(/Password should be at least/i.test(m))return 'Use a password of at least 6 characters.';
  if(/Failed to fetch|NetworkError|network/i.test(m))return 'Cannot reach the server. Check your internet connection.';
  if(/Email not confirmed|confirm/i.test(m))return 'The server is asking for email confirmation. Your instructor needs to turn that off in Supabase.';
  if(/invalid.*email|email.*invalid/i.test(m))return 'The server rejected the sign-up address. Your instructor needs to change userDomain in js/config.js.';
  return m;
}

/* ---------------- Supabase ---------------- */
function supabaseBackend(){
  let sb=null,uid=null;
  const need=r=>{if(r.error)throw r.error;return r.data;};
  /* rpc / select with paging past the 1000-row limit */
  async function all(q){let out=[],from=0;for(;;){const r=need(await q().range(from,from+999));out=out.concat(r||[]);if(!r||r.length<1000)return out;from+=1000;}}
  const B={
    kind:'supabase',
    async init(){
      if(!window.supabase)await loadScript(SB_LIB);
      sb=window.supabase.createClient(CFG.supabaseUrl,CFG.supabaseKey,{auth:{persistSession:true,autoRefreshToken:true,storageKey:window.CALCGAME_AUTH_KEY||'calcgame.auth'}});
      const {data}=await sb.auth.getSession(); uid=data.session?data.session.user.id:null; return uid;
    },
    userId:()=>uid,
    async classOk(code){return need(await sb.rpc('class_name',{p_code:code}));},
    async usernameFree(name){return need(await sb.rpc('username_free',{p_name:name}));},
    async signUp({code,username,password,avatar}){
      const r=await sb.auth.signUp({email:userEmail(username),password});
      if(r.error)throw r.error; if(!r.data.session)throw Error('Email confirmation is on');
      uid=r.data.session.user.id;
      need(await sb.rpc('create_profile',{p_username:username,p_avatar:avatar,p_code:code}));
      return uid;
    },
    async signIn({username,password}){
      const r=await sb.auth.signInWithPassword({email:userEmail(username),password}); if(r.error)throw r.error;
      uid=r.data.session.user.id; return uid;
    },
    async signOut(){await sb.auth.signOut();uid=null;},
    async profile(){
      const p=need(await sb.from('profiles').select('*').eq('id',uid).maybeSingle()); if(!p)return null;
      if(p.class_id){const c=need(await sb.from('classes').select('name').eq('id',p.class_id).maybeSingle());p.class_name=c?c.name:'';}
      return p;
    },
    async loadSave(){const r=need(await sb.from('saves').select('data,updated_at').eq('user_id',uid).maybeSingle());return r;},
    async pushSave(data){need(await sb.from('saves').upsert({user_id:uid,data,updated_at:new Date().toISOString()}));},
    async logAnswers(rows){need(await sb.from('answers').insert(rows));},
    async logCompletion(row){need(await sb.from('completions').insert(row));},
    async myStops(){return need(await sb.from('completions').select('ref').eq('user_id',uid).eq('kind','stop')).map(r=>r.ref);},
    async syncPoints(p){return need(await sb.rpc('sync_points',{p}));},
    async leaderboard(){return need(await sb.rpc('leaderboard'));},
    async sendMessage(m){need(await sb.from('messages').insert(m));},
    async dueDates(){return need(await sb.from('due_dates').select('stop,due_at,class_id'));},
    async claimCode(stop){return need(await sb.rpc('claim_code',{p_stop:stop}));},
    async myCodes(){return need(await sb.from('codes').select('code,stop,created_at,redeemed_at').eq('user_id',uid).order('created_at'));},
    async setAvatar(a){need(await sb.rpc('set_avatar',{p_avatar:a}));},
    async touch(){await sb.rpc('touch');},
    /* instructor */
    async createInstructor({username,password}){
      const r=await sb.auth.signUp({email:userEmail(username),password});
      if(r.error)throw r.error; if(!r.data.session)throw Error('Email confirmation is on');
      uid=r.data.session.user.id; need(await sb.rpc('create_instructor_profile',{p_username:username})); return uid;
    },
    async classes(){return need(await sb.from('classes').select('*').order('created_at'));},
    async createClass(name,code){need(await sb.from('classes').insert({name,code}));},
    async deleteClass(id){need(await sb.from('classes').delete().eq('id',id));},
    async students(cls){return all(()=>sb.rpc('inst_students',{p_class:cls||null}));},
    async questions(cls){return all(()=>sb.rpc('inst_questions',{p_class:cls||null}));},
    async completions(cls){return all(()=>sb.rpc('inst_completions',{p_class:cls||null}));},
    async messages(){return all(()=>sb.rpc('inst_messages'));},
    async setMessage(id,status){need(await sb.from('messages').update({status}).eq('id',id));},
    async deleteMessage(id){need(await sb.from('messages').delete().eq('id',id));},
    async allDueDates(){return need(await sb.from('due_dates').select('*'));},
    async setDue(class_id,stop,due_at){
      if(due_at)need(await sb.from('due_dates').upsert({class_id,stop,due_at}));
      else need(await sb.from('due_dates').delete().eq('class_id',class_id).eq('stop',stop));
    },
    async checkCodes(codes){return need(await sb.rpc('check_codes',{p_codes:codes}));},
    async redeemCodes(codes){return need(await sb.rpc('redeem_codes',{p_codes:codes}));},
    async resetPassword(username,password){need(await sb.rpc('inst_reset_password',{p_username:username,p_password:password}));},
    async deleteStudent(id){need(await sb.rpc('inst_delete_student',{p_id:id}));}
  };
  return B;
}

/* ---------------- local mock (?mock=1): a pretend server inside this browser ---------------- */
function mockBackend(){
  const DBK='calcgame.mockdb',SK=window.CALCGAME_AUTH_KEY?'calcgame.mocksession.inst':'calcgame.mocksession';
  const load=()=>{try{return JSON.parse(localStorage.getItem(DBK))||null;}catch(e){return null;}};
  let db=load()||{users:[],classes:[{id:'c1',name:'Calc 1 (demo)',code:'DEMO1',created_at:new Date().toISOString()}],saves:{},answers:[],completions:[],messages:[],due:[],codes:[],seq:1};
  const persist=()=>{try{localStorage.setItem(DBK,JSON.stringify(db));}catch(e){}};
  let uid=null; try{uid=localStorage.getItem(SK)||null;}catch(e){}
  const me=()=>db.users.find(u=>u.id===uid),now=()=>new Date().toISOString(),id=()=>'m'+(db.seq++);
  const inst=()=>{const u=me();if(!u||!u.is_instructor)throw Error('instructor only');};
  const wait=v=>new Promise(r=>setTimeout(()=>r(v),40));
  const setS=v=>{uid=v;try{v?localStorage.setItem(SK,v):localStorage.removeItem(SK);}catch(e){}};
  const B={
    kind:'mock',
    async init(){if(uid&&!me())setS(null);return uid;},
    userId:()=>uid,
    async classOk(code){const c=db.classes.find(c=>c.code===String(code).trim().toUpperCase());return wait(c?c.name:null);},
    async usernameFree(n){return wait(!db.users.some(u=>u.username.toLowerCase()===n.trim().toLowerCase()));},
    async signUp({code,username,password,avatar}){
      const c=db.classes.find(c=>c.code===String(code).trim().toUpperCase()); if(!c)throw Error('That class code was not found.');
      if(!(await B.usernameFree(username)))throw Error('duplicate key');
      if(password.length<6)throw Error('Password should be at least 6 characters');
      const u={id:id(),username:username.trim(),password,avatar,class_id:c.id,is_instructor:false,points:0,created_at:now(),last_seen:now()};
      db.users.push(u);persist();setS(u.id);return wait(u.id);
    },
    async signIn({username,password}){
      const u=db.users.find(u=>u.username.toLowerCase()===username.trim().toLowerCase()&&u.password===password);
      if(!u)throw Error('Invalid login credentials'); setS(u.id); return wait(u.id);
    },
    async signOut(){setS(null);},
    async profile(){const u=me();if(!u)return null;const c=db.classes.find(c=>c.id===u.class_id);return wait(Object.assign({},u,{class_name:c?c.name:''}));},
    async loadSave(){return wait(db.saves[uid]||null);},
    async pushSave(data){db.saves[uid]={data,updated_at:now()};persist();},
    async logAnswers(rows){rows.forEach(r=>db.answers.push(Object.assign({user_id:uid,at:now()},r)));persist();},
    async logCompletion(r){db.completions.push(Object.assign({user_id:uid,at:now()},r));persist();},
    async myStops(){return db.completions.filter(c=>c.user_id===uid&&c.kind==='stop').map(c=>c.ref);},
    async syncPoints(p){const u=me();u.points=Math.max(u.points,Math.min(p,u.points+500));persist();return u.points;},
    async leaderboard(){const u=me();return wait(db.users.filter(x=>x.class_id===u.class_id&&!x.is_instructor).sort((a,b)=>b.points-a.points).slice(0,50).map(x=>({username:x.username,avatar:x.avatar,points:x.points,me:x.id===uid})));},
    async sendMessage(m){db.messages.push(Object.assign({id:db.seq++,user_id:uid,status:'new',created_at:now()},m));persist();},
    async dueDates(){const u=me();return wait(db.due.filter(d=>u&&d.class_id===u.class_id));},
    async claimCode(stop){
      if(!db.completions.some(c=>c.user_id===uid&&c.kind==='stop'&&c.ref===stop))throw Error('Clear this stop first.');
      let c=db.codes.find(c=>c.user_id===uid&&c.stop===stop); if(c)return c.code;
      const abc='ABCDEFGHJKMNPQRSTUVWXYZ23456789';let k='CG-';for(let i=0;i<6;i++)k+=abc[Math.floor(Math.random()*abc.length)];
      db.codes.push({code:k,user_id:uid,stop,created_at:now(),redeemed_at:null});persist();return wait(k);
    },
    async myCodes(){return db.codes.filter(c=>c.user_id===uid);},
    async setAvatar(a){me().avatar=a;persist();},
    async touch(){const u=me();if(u){u.last_seen=now();persist();}},
    async createInstructor({username,password}){
      if(!(await B.usernameFree(username)))throw Error('duplicate key');
      const u={id:id(),username,password,avatar:'owl',class_id:null,is_instructor:true,points:0,created_at:now(),last_seen:now()}; /* the mock skips the SQL step */
      db.users.push(u);persist();setS(u.id);return u.id;
    },
    async classes(){inst();return db.classes;},
    async createClass(name,code){inst();if(db.classes.some(c=>c.code===code))throw Error('duplicate key');db.classes.push({id:id(),name,code,created_at:now()});persist();},
    async deleteClass(cid){inst();db.classes=db.classes.filter(c=>c.id!==cid);persist();},
    async students(cls){inst();return db.users.filter(u=>!u.is_instructor&&(!cls||u.class_id===cls)).map(u=>{const a=db.answers.filter(x=>x.user_id===u.id),c=db.completions.filter(x=>x.user_id===u.id);
      return {id:u.id,username:u.username,avatar:u.avatar,class_id:u.class_id,points:u.points,created_at:u.created_at,last_seen:u.last_seen,answers:a.length,wrong:a.filter(x=>!x.ok).length,
        lessons:c.filter(x=>x.kind==='lesson').length,sets:c.filter(x=>x.kind==='drill').length,stops:new Set(c.filter(x=>x.kind==='stop').map(x=>x.ref)).size};});},
    async questions(cls){inst();const ok=new Set(db.users.filter(u=>!cls||u.class_id===cls).map(u=>u.id)),g={},seen=new Set();
      db.answers.filter(a=>ok.has(a.user_id)).forEach(a=>{const k=a.deck+'|'+a.qid,q=g[k]||(g[k]={deck:a.deck,area:a.area,qid:a.qid,attempts:0,wrong:0,students:new Set(),first_try_wrong:0});
        q.attempts++;if(!a.ok)q.wrong++;q.students.add(a.user_id);const f=a.user_id+'|'+k;if(!seen.has(f)){seen.add(f);if(!a.ok)q.first_try_wrong++;}});
      return Object.values(g).map(q=>Object.assign(q,{students:q.students.size}));},
    async completions(cls){inst();const ok=new Set(db.users.filter(u=>!cls||u.class_id===cls).map(u=>u.id));return db.completions.filter(c=>ok.has(c.user_id));},
    async messages(){inst();return db.messages.slice().reverse().map(m=>{const u=db.users.find(u=>u.id===m.user_id);return Object.assign({},m,{username:u?u.username:null,class_id:u?u.class_id:null});});},
    async setMessage(mid,status){inst();const m=db.messages.find(m=>m.id===mid);if(m)m.status=status;persist();},
    async deleteMessage(mid){inst();db.messages=db.messages.filter(m=>m.id!==mid);persist();},
    async allDueDates(){inst();return db.due;},
    async setDue(class_id,stop,due_at){inst();db.due=db.due.filter(d=>!(d.class_id===class_id&&d.stop===stop));if(due_at)db.due.push({class_id,stop,due_at});persist();},
    async checkCodes(codes){inst();const want=new Set(codes.map(c=>c.trim().toUpperCase()));return db.codes.filter(c=>want.has(c.code)).map(c=>({code:c.code,stop:c.stop,created_at:c.created_at,redeemed_at:c.redeemed_at}));},
    async redeemCodes(codes){inst();let n=0;const want=new Set(codes.map(c=>c.trim().toUpperCase()));db.codes.forEach(c=>{if(want.has(c.code)&&!c.redeemed_at){c.redeemed_at=now();n++;}});persist();return n;},
    async resetPassword(username,pw){inst();const u=db.users.find(u=>u.username.toLowerCase()===username.toLowerCase()&&!u.is_instructor);if(!u)throw Error('No student with that username.');u.password=pw;persist();},
    async deleteStudent(sid){inst();db.users=db.users.filter(u=>u.id!==sid);['answers','completions','codes'].forEach(k=>{db[k]=db[k].filter(x=>x.user_id!==sid);});delete db.saves[sid];persist();}
  };
  return B;
}

const MOCK=/[?&]mock=1/.test(location.search);
const ONLINE_CONFIGURED=MOCK||!!(CFG.supabaseUrl&&CFG.supabaseKey);
const BACK=MOCK?mockBackend():ONLINE_CONFIGURED?supabaseBackend():null;
