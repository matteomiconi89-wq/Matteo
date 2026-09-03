#!/usr/bin/env python3
# Genera un viewer di CONTROLLO per un singolo mobile (armadio master), con toggle per
# nascondere ante/maniglie e vedere gli interni (ripiani, cassetti, bastoni).
import json, pathlib
BASE=pathlib.Path(__file__).parent
D=json.load(open(BASE/'armadio_master_dettaglio.json'))
GEO=json.dumps(D['mesh'],separators=(',',':'))
INFO=json.dumps({k:D[k] for k in ('pezzo','W','D','H','vani','tipi')},ensure_ascii=False)
HTML=r'''<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Armadio master · controllo</title>
<style>
:root{--bg:#e9eaed;--panel:#f6f7f5;--ink:#1a1e24;--muted:#5d6672;--line:#d0d4da;--accent:#a8825a}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#0f1216;--panel:#171b21;--ink:#e7eaee;--muted:#98a2ad;--line:#2a303a;--accent:#c79a67}}
*{box-sizing:border-box}html,body{height:100%;margin:0}
body{background:var(--bg);color:var(--ink);font:14px/1.5 "IBM Plex Sans",system-ui,sans-serif;overflow:hidden}
#c{position:fixed;inset:0;display:block;cursor:grab}#c:active{cursor:grabbing}
#panel{position:fixed;top:14px;left:14px;background:var(--panel);border:1px solid var(--line);border-radius:12px;
 padding:14px 16px;max-width:290px;box-shadow:0 8px 30px rgba(0,0,0,.18)}
h1{font:600 16px/1.2 "Barlow Semi Condensed",sans-serif;margin:0 0 2px}
.dim{font:500 12px "IBM Plex Mono",monospace;color:var(--muted);margin-bottom:10px}
label{display:flex;align-items:center;gap:8px;padding:3px 0;cursor:pointer;user-select:none}
label input{accent-color:var(--accent)}
.sw{width:12px;height:12px;border-radius:3px;border:1px solid rgba(0,0,0,.2)}
.hint{margin-top:10px;font-size:12px;color:var(--muted);border-top:1px solid var(--line);padding-top:8px}
#views{position:fixed;bottom:14px;left:14px;display:flex;gap:6px}
#views button{background:var(--panel);border:1px solid var(--line);color:var(--ink);border-radius:8px;padding:6px 10px;cursor:pointer;font:500 12px "IBM Plex Sans"}
</style>
<canvas id="c"></canvas>
<div id="panel"><h1 id="ttl"></h1><div class="dim" id="dim"></div><div id="toggles"></div>
<div class="hint" id="hint"></div></div>
<div id="views">
 <button data-v="3q">3/4</button><button data-v="fr">Fronte</button><button data-v="tp">Alto</button><button data-v="op">Ante OFF</button>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const MESH=/*__GEO__*/, INFO=/*__INFO__*/;
const LAB={carcassa:'Struttura',zoccolo:'Zoccolo',montante:'Montanti',ripiano:'Ripiani',cassetto:'Cassetti',anta:'Ante',maniglia:'Maniglie',bastone:'Bastoni appenderia'};
document.getElementById('ttl').textContent=INFO.pezzo;
document.getElementById('dim').textContent=`${INFO.W} × ${INFO.D} × ${INFO.H} mm  ·  ${INFO.vani} vani`;
document.getElementById('hint').textContent='Ipotesi da confermare: n° e passo ripiani, quali vani hanno i cassetti (ora vani 3–4), altezza appenderia, altezza maniglie. Dimmi e correggo.';
const scene=new THREE.Scene();
const cvs=document.getElementById('c');
const renderer=new THREE.WebGLRenderer({canvas:cvs,antialias:true});
const dark=matchMedia('(prefers-color-scheme:dark)').matches;
scene.background=new THREE.Color(dark?0x0f1216:0xe9eaed);
const cam=new THREE.PerspectiveCamera(38,innerWidth/innerHeight,10,60000);
scene.add(new THREE.AmbientLight(0xffffff,.72));
const d1=new THREE.DirectionalLight(0xffffff,.85);d1.position.set(1,-2,3);scene.add(d1);
const d2=new THREE.DirectionalLight(0xffffff,.35);d2.position.set(-2,1,1);scene.add(d2);
// centro del mobile
let cx=0,cy=0,cz=0,n=0;
MESH.forEach(m=>m.v.forEach(v=>{cx+=v[0];cy+=v[1];cz+=v[2];n++}));
cx/=n;cy/=n;cz/=n;
const groups={};
MESH.forEach(m=>{
 const g=new THREE.BufferGeometry();
 const pos=[];m.f.forEach(f=>f.forEach(i=>{const v=m.v[i];pos.push(v[0]-cx,v[1]-cy,v[2]-cz)}));
 g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.computeVertexNormals();
 const mat=new THREE.MeshLambertMaterial({color:new THREE.Color(m.c),side:THREE.DoubleSide});
 const mesh=new THREE.Mesh(g,mat);
 (groups[m.l]=groups[m.l]||new THREE.Group()).add(mesh);
});
Object.values(groups).forEach(g=>scene.add(g));
// wireframe edges per leggibilità
MESH.forEach(m=>{});
// toggles
const order=['carcassa','montante','ripiano','cassetto','bastone','anta','maniglia','zoccolo'];
const tg=document.getElementById('toggles');
order.filter(k=>groups[k]).forEach(k=>{
 const first=MESH.find(m=>m.l===k);
 const l=document.createElement('label');
 l.innerHTML=`<input type=checkbox checked><span class=sw style="background:${first.c}"></span>${LAB[k]||k}`;
 l.querySelector('input').onchange=e=>groups[k].visible=e.target.checked;
 tg.appendChild(l);
});
// orbit (Z-up)
let az=-0.9,el=0.5,rad=5200,tgt=new THREE.Vector3(0,0,120);
function place(){cam.position.set(tgt.x+rad*Math.cos(el)*Math.cos(az),tgt.y+rad*Math.cos(el)*Math.sin(az),tgt.z+rad*Math.sin(el));cam.up.set(0,0,1);cam.lookAt(tgt)}
let drag=false,px,py;
cvs.onpointerdown=e=>{drag=true;px=e.clientX;py=e.clientY;cvs.setPointerCapture(e.pointerId)};
cvs.onpointermove=e=>{if(!drag)return;az-=(e.clientX-px)*.008;el=Math.max(-1.4,Math.min(1.4,el+(e.clientY-py)*.008));px=e.clientX;py=e.clientY;place()};
cvs.onpointerup=()=>drag=false;
cvs.onwheel=e=>{e.preventDefault();rad=Math.max(1400,Math.min(20000,rad*(1+Math.sign(e.deltaY)*.1)));place()};
document.querySelectorAll('#views button').forEach(b=>b.onclick=()=>{
 const v=b.dataset.v;
 if(v=='3q'){az=-0.9;el=0.5}if(v=='fr'){az=Math.PI/2;el=0.05}if(v=='tp'){el=1.35}
 if(v=='op'){groups.anta.visible=!groups.anta.visible;groups.maniglia.visible=groups.anta.visible;
   tg.querySelectorAll('input')[order.filter(k=>groups[k]).indexOf('anta')].checked=groups.anta.visible;}
 place();
});
addEventListener('resize',()=>{renderer.setSize(innerWidth,innerHeight);cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix()});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(innerWidth,innerHeight);cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix();
place();(function loop(){requestAnimationFrame(loop);renderer.render(scene,cam)})();
</script>'''
HTML=HTML.replace('/*__GEO__*/',GEO).replace('/*__INFO__*/',INFO)
out=BASE/'armadio_review.html'; out.write_text(HTML)
import os; print('scritto',out.name,os.path.getsize(out)//1024,'KB')
