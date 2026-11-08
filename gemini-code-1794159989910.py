import os

content = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Çelik Kanat</title>
<style>
:root{--bg:#0b1020;--ship:#7ee8c1;--text:#eaf0ff;--muted:#8d98c4;--panel:#1a2244;box-sizing:border-box}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0b1020;--ship:#7ee8c1;--text:#eaf0ff;--muted:#8d98c4;--panel:#1a2244}}
:root[data-theme="dark"]{--bg:#0b1020;--ship:#7ee8c1;--text:#eaf0ff;--muted:#8d98c4;--panel:#1a2244}
html,body{margin:0;height:100%;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;overflow:hidden;touch-action:none;user-select:none;-webkit-user-select:none;overscroll-behavior:none}
canvas{position:fixed;inset:0;width:100%;height:100%}
#hud{position:fixed;top:0;left:0;right:0;display:flex;justify-content:space-between;padding:calc(env(safe-area-inset-top,0px) + 10px) 16px 0;font-weight:700;font-size:16px;pointer-events:none}
#hud span:nth-child(2){color:var(--muted);font-weight:500}
#msg{position:fixed;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;text-align:center;background:rgba(11,16,32,.88);padding:20px}
#msg h1{margin:0;font-size:32px}
#msg p{margin:0 0 6px;color:var(--muted);max-width:300px;line-height:1.4}
#msg button{font:inherit;font-weight:700;padding:13px 32px;border:0;border-radius:999px;background:var(--ship);color:#0b1020;cursor:pointer}
#msg .card{width:min(86vw,320px);border-radius:14px;background:var(--panel);color:var(--text);text-align:left;padding:14px 16px;border:2px solid var(--ship)}
#msg .card small{color:var(--muted);font-weight:400;font-size:14px}
#msg input{font:inherit;font-size:18px;text-align:center;padding:11px 14px;border-radius:12px;border:2px solid var(--panel);background:var(--bg);color:var(--text);width:min(70vw,260px);user-select:text;-webkit-user-select:text}
#msg input:focus{outline:2px solid var(--ship)}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div id="hud"><span id="sc"></span><span id="wv"></span><span id="hp"></span></div>
<div id="msg"></div>
<script>
const cv=document.getElementById('c'),ctx=cv.getContext('2d'),$=id=>document.getElementById(id);
const C={ship:'#7ee8c1',ship2:'#2a9d8f',foe:'#ff7a6b',foe2:'#8f2040',shot:'#f4d35e',ebul:'#ff5d8f',boss:'#b388ff'};
let W,H,p,bl,en,eb,pt,score,wave,tier,toSpawn,spawn,bn,btxt,mode,run=false,last,best=0,tx,ty,keys={},boss,stars=[],pname='';
try{best=+localStorage.getItem('savasBest')||0;pname=localStorage.getItem('savasName')||''}catch(e){}
for(let i=0;i<70;i++)stars.push({x:Math.random(),y:Math.random(),s:.3+Math.random()});
function fit(){const d=devicePixelRatio||1;W=innerWidth;H=innerHeight;cv.width=W*d;cv.height=H*d;ctx.setTransform(d,0,0,d,0,0)}
addEventListener('resize',fit);fit();
const UP=[
{t:'Çoklu atış',d:'+1 mermi, daha geniş ateş',ok:()=>p.gun<5,go:()=>p.gun++},
{t:'Hızlı ateş',d:'Atış hızı +%20',ok:()=>p.rate<5,go:()=>p.rate++},
{t:'Güçlü mermi',d:'Hasar +%40',ok:()=>1,go:()=>p.dmg+=.4},
{t:'Zırh',d:'+1 maksimum can ve tam onarım',ok:()=>p.max<8,go:()=>{p.max++;p.hp=p.max}},
{t:'Kalkan',d:'Her dalgada 1 vuruşu engeller',ok:()=>!p.shield,go:()=>p.shield=1}];
function start(){
  p={x:W/2,y:H*.8,vx:0,vy:0,hp:3,max:3,cd:0,inv:0,sh:0,gun:1,rate:0,dmg:1,shield:0};
  bl=[];en=[];eb=[];pt=[];score=0;wave=1;tx=p.x;ty=p.y;mode='play';boss=null;
  $('msg').style.display='none';startWave();run=true;last=performance.now();requestAnimationFrame(loop);
}
function startWave(){
  tier=(wave-1)/10|0;const k=(wave-1)%10;if(p.shield)p.sh=1;
  if(wave%10==0){toSpawn=0;const h=40+wave*5;boss={boss:1,x:W/2,y:-90,r:50,hp:h,max:h,t:0,cd:1.5,cd2:3};en.push(boss);btxt='BOSS'}
  else if(wave%10==5){toSpawn=0;const h=14+wave*3;boss={boss:1,mini:1,x:W/2,y:-90,r:34,hp:h,max:h,t:0,cd:1.5,cd2:3};en.push(boss);btxt='MİNİ BOSS'}
  else{toSpawn=3+(k>>1)+tier*2;btxt='Dalga '+wave}
  bn=2;spawn=0;hud();
}
function hud(){$('sc').textContent='Puan: '+score;$('wv').textContent='Dalga '+wave+' · Seviye '+(tier+1);$('hp').textContent='♥'.repeat(Math.max(p.hp,0))+'♡'.repeat(Math.max(p.max-p.hp,0))}
function boom(x,y,c,n){for(let i=0;i<n;i++){const a=Math.random()*6.28,s=40+Math.random()*180;pt.push({x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s,l:.6,c})}}
function addEnemy(){
  const k=(wave-1)%10,m=60,mid=W/2;
  const mk=(x,y,s,i)=>en.push({x,bx:x,y,t:0,amp:36,r:s?22:16,hp:s?3+tier*2:1+tier,s,cd:1.2+i*.35,ty:H*.2});
  if(Math.random()<Math.min(.1+k*.05+tier*.1,.6)){
    const n=Math.min(2+(k>>2)+tier,5),sx=Math.min(80,(W-2*m)/(n-1));
    for(let i=0;i<n;i++)mk(mid+(i-(n-1)/2)*sx,-30,1,i);return;
  }
  const f=['line','column','v','diag'][Math.random()*(k<2?2:4)|0],n=f=='v'?5:4+(k>3?1:0),sx=Math.min(64,(W-2*m)/(n-1));
  const d=Math.random()<.5?1:-1,cx=m+Math.random()*(W-2*m);
  for(let i=0;i<n;i++){
    const j=i-(n-1)/2;
    if(f=='line')mk(mid+j*sx,-30,0,i);
    else if(f=='v')mk(mid+j*sx,-30-Math.abs(j)*40,0,i);
    else if(f=='column')mk(cx,-30-i*48,0,i);
    else mk(mid+d*j*sx,-30-i*38,0,i);
  }
}
function lead(e){return Math.atan2(p.y-e.y,p.x-e.x)}
function aim(e,sp,a0){const a=a0??lead(e,sp);eb.push({x:e.x,y:e.y+(e.boss?30:10),vx:Math.cos(a)*sp,vy:Math.sin(a)*sp})}
function hit(){
  if(p.inv>0)return;p.inv=1.2;
  if(p.sh){p.sh=0;boom(p.x,p.y,'#7ee8ff',14);return}
  p.hp--;boom(p.x,p.y,C.ship,20);if(navigator.vibrate)navigator.vibrate(60);hud();if(p.hp<=0)over();
}
function upgrade(){
  mode='up';p.hp=Math.min(p.max,p.hp+1);hud();
  const m=$('msg');m.innerHTML='<h1>'+(wave%10==5?'Mini boss':'Boss')+' yenildi!</h1><p>Uçağın için bir gelişim seç</p>';
  UP.filter(u=>u.ok()).sort(()=>Math.random()-.5).slice(0,3).forEach(u=>{
    const b=document.createElement('button');b.className='card';b.innerHTML='<b>'+u.t+'</b><br><small>'+u.d+'</small>';
    b.onclick=()=>{u.go();m.style.display='none';wave++;mode='play';last=performance.now();startWave()};m.appendChild(b)});
  m.style.display='flex';
}
function loop(now){
  if(!run)return;
  const dt=Math.min((now-last)/1000,.04);last=now;
  stars.forEach(s=>s.y=(s.y+dt*.06*s.s)%1);
  if(mode=='up'){pt.forEach(q=>{q.x+=q.vx*dt;q.y+=q.vy*dt;q.l-=dt});pt=pt.filter(q=>q.l>0);draw();requestAnimationFrame(loop);return}
  const k=(wave-1)%10,sp=1+tier*.25;
  if(keys.ArrowLeft)tx-=420*dt;if(keys.ArrowRight)tx+=420*dt;if(keys.ArrowUp)ty-=420*dt;if(keys.ArrowDown)ty+=420*dt;
  tx=Math.max(20,Math.min(W-20,tx));ty=Math.max(70,Math.min(H-30,ty));
  const ox=p.x,oy=p.y;p.x+=(tx-p.x)*Math.min(1,dt*14);p.y+=(ty-p.y)*Math.min(1,dt*14);p.vx=(p.x-ox)/(dt||.016);p.vy=(p.y-oy)/(dt||.016);p.cd-=dt;p.inv-=dt;
  if(p.cd<=0){p.cd=.18*Math.pow(.8,p.rate);const n=p.gun;for(let i=0;i<n;i++){const o=(i-(n-1)/2)*.13;bl.push({x:p.x+(i-(n-1)/2)*6,y:p.y-16,vx:Math.sin(o)*640,vy:-Math.cos(o)*640})}}
  bl.forEach(b=>{b.x+=b.vx*dt;b.y+=b.vy*dt});bl=bl.filter(b=>b.y>-10&&b.x>-10&&b.x<W+10);
  if(bn>0)bn-=dt;
  else if(toSpawn>0){spawn-=dt;if(spawn<=0){addEnemy();toSpawn--;spawn=Math.max(1.5,2.8-k*.12-tier*.25)}}
  else if(!en.length){if(wave%5==0)upgrade();else{wave++;startWave()}}
  en.forEach(e=>{
    e.t+=dt;
    if(e.boss){
      e.y+=(H*.2-e.y)*Math.min(1,dt*2);e.x=W/2+Math.sin(e.t*.8)*(W/2-70);
      const f=e.hp<e.max/2?1.6:1;e.cd-=dt*f;e.cd2-=dt*f;
      if(e.y>0&&e.cd<=0){e.cd=1.2;const n=(e.mini?3:5)+tier*2;for(let i=0;i<n;i++)aim(e,200,Math.PI/2+(i-(n-1)/2)*.28)}
      if(e.y>0&&e.cd2<=0){e.cd2=2.6;const a0=lead(e,300);for(let i=-1;i<=1;i++)aim(e,300,a0+i*.12)}
      return;
    }
    e.x=e.bx+Math.sin(e.t*1.4)*e.amp;e.y+=(e.s?(e.y<e.ty?100*sp:0):90*sp)*dt;
    if(e.s){e.cd-=dt;if(e.cd<=0&&e.y>0){e.cd=1.7-tier*.2;aim(e,220+tier*30)}}
  });
  eb.forEach(b=>{b.x+=b.vx*dt;b.y+=b.vy*dt});eb=eb.filter(b=>b.y>-20&&b.y<H+20&&b.x>-20&&b.x<W+20);
  for(const b of bl)for(const e of en)if(!b.d&&!e.dead&&Math.hypot(b.x-e.x,b.y-e.y)<e.r+4){
    b.d=1;e.hp-=p.dmg;boom(b.x,b.y,C.shot,2);
    if(e.hp<=0){e.dead=1;
      if(e.boss){score+=e.mini?200:500;boom(e.x,e.y,C.boss,e.mini?35:70);boom(e.x,e.y,C.shot,e.mini?20:40);eb=[];boss=null}
      else{score+=e.s?30:10;boom(e.x,e.y,C.foe,e.s?24:12)}hud()}}
  bl=bl.filter(b=>!b.d);en=en.filter(e=>!e.dead&&e.y<H+40);
  for(const e of en)if(Math.hypot(e.x-p.x,e.y-p.y)<e.r+10){if(!e.boss){e.dead=1;boom(e.x,e.y,C.foe,10)}hit()}
  en=en.filter(e=>!e.dead);
  for(const b of eb)if(Math.hypot(b.x-p.x,b.y-p.y)<13){b.y=9999;hit()}
  pt.forEach(q=>{q.x+=q.vx*dt;q.y+=q.vy*dt;q.l-=dt});pt=pt.filter(q=>q.l>0);
  draw();if(run)requestAnimationFrame(loop);
}
function poly(a,f){ctx.beginPath();ctx.moveTo(a[0],a[1]);for(let i=2;i<a.length;i+=2)ctx.lineTo(a[i],a[i+1]);ctx.closePath();ctx.fillStyle=f;ctx.fill()}
function grad(y0,y1,a,b){const g=ctx.createLinearGradient(0,y0,0,y1);g.addColorStop(0,a);g.addColorStop(1,b);return g}
function dot(x,y,r,c){ctx.fillStyle=c;ctx.beginPath();ctx.arc(x,y,r,0,7);ctx.fill()}
function drawPlayer(){
  ctx.save();ctx.translate(p.x,p.y);
  const fl=10+Math.random()*9;poly([-5,12,5,12,0,12+fl],'#ffb454');poly([-2.5,12,2.5,12,0,12+fl*.6],'#fff3b0');
  poly([-4,-4,-27,16,-27,23,-6,14],C.ship2);poly([4,-4,27,16,27,23,6,14],C.ship2);
  poly([-27,16,-23,14,-25,24],C.shot);poly([27,16,23,14,25,24],C.shot);
  poly([0,-27,7,0,6,16,-6,16,-7,0],grad(-27,16,'#e8fff6',C.ship));
  ctx.fillStyle='#1b3b6f';ctx.beginPath();ctx.ellipse(0,-6,3,7,0,0,7);ctx.fill();
  if(p.gun>2){ctx.fillStyle=C.shot;ctx.fillRect(-21,0,3,11);ctx.fillRect(18,0,3,11)}
  if(p.gun>4){ctx.fillStyle=C.shot;ctx.fillRect(-12,-2,3,11);ctx.fillRect(9,-2,3,11)}
  if(p.sh){ctx.strokeStyle='rgba(126,232,255,.85)';ctx.lineWidth=2;ctx.beginPath();ctx.arc(0,0,32,0,7);ctx.stroke()}
  ctx.restore();
}
function drawEnemy(e){
  ctx.save();ctx.translate(e.x,e.y);
  if(e.boss){
    if(e.mini)ctx.scale(.62,.62);
    const pu=.5+.5*Math.sin(e.t*6);
    poly([-72,-20,-42,-30,-30,10,-48,36,-18,22],'#3b2a6b');poly([72,-20,42,-30,30,10,48,36,18,22],'#3b2a6b');
    poly([0,50,30,20,38,-26,14,-42,-14,-42,-38,-26,-30,20],grad(-42,50,C.boss,'#3a1d72'));
    poly([0,32,12,10,0,-6,-12,10],'#1a0c33');dot(0,10,7+pu*2,'rgba(255,93,143,'+(.5+.5*pu)+')');
    ctx.fillStyle=C.shot;[-54,54].forEach(x=>ctx.fillRect(x-3,10,6,16));
  }else if(e.s){
    poly([-27,-14,-12,-4,-12,10,-27,2],'#5a1a35');poly([27,-14,12,-4,12,10,27,2],'#5a1a35');
    poly([0,23,12,4,10,-16,-10,-16,-12,4],grad(-16,23,'#ff7aa8',C.foe2));
    ctx.fillStyle='#ffd166';ctx.fillRect(-21,2,4,12);ctx.fillRect(17,2,4,12);dot(0,2,5,C.ebul);
  }else{
    poly([0,18,14,-4,19,-15,6,-8,0,-14,-6,-8,-19,-15,-14,-4],grad(-14,18,'#ff9a8b',C.foe2));
    poly([0,14,5,-2,0,-8,-5,-2],'#2b0a12');dot(0,-1,3.5,C.shot);
  }
  ctx.restore();
}
function draw(){
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle='#cfd8ff';stars.forEach(s=>{ctx.globalAlpha=.25+s.s*.4;ctx.fillRect(s.x*W,s.y*H,s.s*2,s.s*2)});ctx.globalAlpha=1;
  bl.forEach(b=>{ctx.fillStyle=C.shot;ctx.fillRect(b.x-2,b.y-9,4,14);ctx.fillStyle='#fff';ctx.fillRect(b.x-1,b.y-9,2,6)});
  eb.forEach(b=>{dot(b.x,b.y,6,'rgba(255,93,143,.35)');dot(b.x,b.y,3.5,C.ebul)});
  en.forEach(drawEnemy);
  if(p.hp>0&&(p.inv<=0||Math.floor(p.inv*12)%2))drawPlayer();
  pt.forEach(q=>{ctx.globalAlpha=Math.max(q.l*1.8,0);ctx.fillStyle=q.c;ctx.fillRect(q.x-2,q.y-2,4,4)});ctx.globalAlpha=1;
  if(boss&&boss.hp>0){ctx.fillStyle='rgba(255,255,255,.15)';ctx.fillRect(16,52,W-32,8);ctx.fillStyle=C.boss;ctx.fillRect(16,52,(W-32)*boss.hp/boss.max,8)}
  if(bn>0&&mode=='play'){ctx.globalAlpha=Math.min(1,bn);ctx.fillStyle='#fff';ctx.font='700 34px system-ui';ctx.textAlign='center';ctx.fillText(btxt,W/2,H*.4);ctx.globalAlpha=1}
}
function over(){
  run=false;if(score>best){best=score;try{localStorage.setItem('savasBest',best)}catch(e){}}
  menu('Uçağın düştü',esc(pname)+'<br>Puan: '+score+' · Dalga: '+wave+'<br>En iyi: '+best,'Tekrar savaş');
}
function move(x,y){tx=x;ty=y-70}
addEventListener('touchstart',e=>{if(run)move(e.touches[0].clientX,e.touches[0].clientY)},{passive:true});
addEventListener('touchmove',e=>{if(run)move(e.touches[0].clientX,e.touches[0].clientY)},{passive:true});
addEventListener('mousemove',e=>{if(run&&e.buttons)move(e.clientX,e.clientY+70)});
addEventListener('keydown',e=>{keys[e.key]=1;if(e.key.startsWith('Arrow'))e.preventDefault()});
addEventListener('keyup',e=>{keys[e.key]=0});
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function menu(t,s,btn){
  const m=$('msg');
  m.innerHTML='<h1>'+t+'</h1><p>'+s+'</p><input id="nm" maxlength="14" placeholder="Adını yaz" value="'+esc(pname)+'" autocomplete="off"><button id="go">'+btn+'</button>';
  m.style.display='flex';
  $('go').onclick=()=>{const v=$('nm').value.trim();if(!v){$('nm').