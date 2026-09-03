#!/usr/bin/env python3
# BAGNI ant+post — muri (vano stanza) + doccia (piatto+vetro+soffione) + WC (base+cassetta) + bidet.
# Posizioni ESATTE dalla pianta DWG. Integra in arredo_geometry.json.
import cadquery as cq, json, pathlib
from cadquery import exporters
BASE=pathlib.Path('.'); PAV=1395.0
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))
def cyl(x,y,z,r,h,axis=(0,0,1)): return cq.Workplane('XY').cylinder(h,r,direct=axis,centered=(True,True,False)).translate((x,y,z))
# --- dati DWG (trailer mm) ---
BAG={
 'bagno_ant':{'room':(1000,3812,3582,4767),'wc':(3633,3881),'bidet':(3665,4407),
   'tray':(1000,1789,3582,4767),'glass_x':1780,'wall_x':3812,'wall_side':'right'},
 'bagno_post':{'room':(10538,13488,3582,4767),'wc':(10718,4477),'bidet':(10686,3980),
   'tray':(12641,13488,3582,4767),'glass_x':12660,'wall_x':10538,'wall_side':'left'},
}
def sanitario(cx,cy,wall_x,side,kind):
    # base + (WC) cassetta verso il muro
    depth=600 if kind=='wc' else 520; wide=370
    if side=='right': bx0,bx1=wall_x-depth,wall_x-40           # back al muro destro
    else: bx0,bx1=wall_x+40,wall_x+depth
    s=box(bx0,bx1,cy-wide/2,cy+wide/2,PAV,PAV+420)             # tazza
    if kind=='wc':
        if side=='right': s=s.union(box(wall_x-180,wall_x-40,cy-wide/2,cy+wide/2,PAV,PAV+900))  # cassetta
        else: s=s.union(box(wall_x+40,wall_x+180,cy-wide/2,cy+wide/2,PAV,PAV+900))
    return s
def muri(rx0,rx1,ry0,ry1,tk=90,h=2100):
    return box(rx0,rx1,ry0,ry1,PAV,PAV+h).cut(box(rx0+tk,rx1-tk,ry0+tk,ry1-tk,PAV-10,PAV+h+10))
new={}
def tess(sol):
    v,t=sol.val().tessellate(0.5); return {'v':[[round(a.x,1),round(a.y,1),round(a.z,1)] for a in v],'f':[[int(i) for i in f] for f in t]}
def add(key,sol,lab,c):
    try: new.setdefault(key,[]).append(dict(tess(sol),l=lab,c=c))
    except Exception as ex: print('err',key,lab,ex)
for key,D in BAG.items():
    rx0,rx1,ry0,ry1=D['room']
    add(key+'_muri',muri(rx0,rx1,ry0,ry1),'muro','#b9c6cc')
    # doccia
    tx0,tx1,ty0,ty1=D['tray']
    add(key+'_sanitari',box(tx0,tx1,ty0,ty1,PAV,PAV+120),'piatto','#9fb6bd')      # piatto doccia
    gx=D['glass_x']
    add(key+'_sanitari',box(gx,gx+12,ty0+40,ty1-300,PAV,PAV+1950),'vetro','#bfe0e8')  # vetro lato
    hx=(rx1-140) if D['wall_side']=='right' else (rx0+140)                          # soffione sul muro doccia
    add(key+'_sanitari',cyl((tx0+tx1)/2,ty1-200,PAV+2050,45,80,(0,0,1)),'soffione','#cccccc')
    # WC + bidet
    add(key+'_sanitari',sanitario(*D['wc'],D['wall_x'],D['wall_side'],'wc'),'wc','#eef2f4')
    add(key+'_sanitari',sanitario(*D['bidet'],D['wall_x'],D['wall_side'],'bidet'),'bidet','#e6edf0')
    # STEP per bagno
    alls=[]
    for k in (key+'_muri',key+'_sanitari'):
        for m in new.get(k,[]): pass
# export STEP combinato dei sanitari+muri
import itertools
json.dump(new,open(BASE/'bagni_v2_mesh.json','w'),separators=(',',':'))
print('bagni pezzi:',{k:len(v) for k,v in new.items()})
