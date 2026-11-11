import re,json,os
from PIL import Image
L=[]
for line in open('ocrbox.txt',encoding='utf8'):
    p=line.rstrip('\n').split('|',4)
    if len(p)<5: continue
    L.append((p[0],int(p[1]),int(p[2]),int(p[3]),p[4]))
pages=sorted(set(l[0] for l in L))
recs=json.load(open('records.json',encoding='utf8'))
# page index lines by y
bypage={pg:sorted([l for l in L if l[0]==pg],key=lambda l:l[2]) for pg in pages}
HEAD=262
# events sequence in doc order
ev=[]
for pg in pages:
    for (_,x,y,h,t) in bypage[pg]:
        if y<HEAD: continue
        ev.append((pg,x,y,h,t))
# group markers
gstart={'I':r'^GRUPO 1$','II':r'^GRUPO 11$','III':r'^GRUPO 111$','IV':r'^GRUPO IV$'}
gidx={}
for i,e in enumerate(L):
    for g,rx in gstart.items():
        if re.match(rx,e[4].strip()): gidx[g]=e
# build full event list with GRUPO markers kept (they are at y>HEAD in p1)
ev=[]
for pg in pages:
    for (_,x,y,h,t) in bypage[pg]:
        if y<HEAD: continue
        ev.append((pg,x,y,h,t))
order=['I','II','III','IV']
pos={}
for g in order:
    for i,e in enumerate(ev):
        if re.match(gstart[g],e[4].strip()): pos[g]=i;break
print(pos)
out={}
report=[]
for gi,g in enumerate(order):
    s=pos[g]; e=pos[order[gi+1]] if gi+1<len(order) else len(ev)
    seg=ev[s+1:e]
    n=len(recs[g])
    # find starts sequentially
    starts={};ans=[];i=0
    k=1
    for j,(pg,x,y,h,t) in enumerate(seg):
        if k<=n and x<260 and re.match(r'^%d\s*[\.,]\s*\S'%k,t.strip()) or (k<=n and x<260 and re.match(r'^%d\s*[\.,]?\s*$'%k,t.strip())):
            starts[k]=j;k+=1
    anss=[j for j,(pg,x,y,h,t) in enumerate(seg) if re.match(r'^\s*Respuesta',t)]
    print(g,n,'starts',len(starts),'ans',len(anss),'missing',[q for q in range(1,n+1) if q not in starts][:20])
    out[g]=(seg,starts,anss)
import pickle
pickle.dump(out,open('seg.pkl','wb'))
