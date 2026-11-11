import re,json,os
from PIL import Image,ImageChops
L=[]
for line in open('ocrbox.txt',encoding='utf8'):
    p=line.rstrip('\n').split('|',4)
    if len(p)<5: continue
    L.append((p[0],int(p[1]),int(p[2]),int(p[3]),p[4].strip()))
recs=json.load(open('records.json',encoding='utf8'))
HEAD,BOT=262,1535
def valid(e):
    pg,x,y,h,t=e
    if y<HEAD: return False
    if y>1500 and x>1000: return False
    if re.match(r'^\d{1,3}$',t) and y>1500: return False
    return True
ev=[e for e in L if valid(e)]
ev.sort(key=lambda e:(e[0],e[2]))
gm={'I':r'^GRUPO 1$','II':r'^GRUPO 11$','III':r'^GRUPO 111$','IV':r'^GRUPO IV$'}
order=['I','II','III','IV']
pos={g:next(i for i,e in enumerate(ev) if re.match(gm[g],e[4])) for g in order}
os.makedirs('web/img',exist_ok=True)
def pimg(pg):
    return Image.open(f'pages/{pg}.png').convert('RGB')
cache={}
def getimg(pg):
    if pg not in cache: cache[pg]=pimg(pg)
    return cache[pg]
def crop_range(a,b):
    """a=(pg,y) start, b=(pg,y) end (exclusive)"""
    pgs=sorted(set(e[0] for e in L))
    ia,ib=pgs.index(a[0]),pgs.index(b[0])
    parts=[]
    for i in range(ia,ib+1):
        y0=a[1] if i==ia else HEAD
        y1=b[1] if i==ib else BOT
        if y1-y0<8: continue
        im=getimg(pgs[i]).crop((90,y0,1200,y1))
        parts.append(im)
    if not parts: return None
    W=max(p.width for p in parts);H=sum(p.height for p in parts)
    c=Image.new('RGB',(W,H),'white');yy=0
    for p in parts: c.paste(p,(0,yy));yy+=p.height
    bg=Image.new('RGB',c.size,'white')
    bb=ImageChops.difference(c,bg).convert('L').point(lambda v:255 if v>40 else 0).getbbox()
    if bb: c=c.crop((max(0,bb[0]-6),max(0,bb[1]-6),min(c.width,bb[2]+6),min(c.height,bb[3]+6)))
    return c
data=[];issues=[]
for gi,g in enumerate(order):
    s=pos[g]; e=pos[order[gi+1]] if gi+1<4 else len(ev)
    seg=ev[s+1:e]
    n=len(recs[g])
    anss=[j for j,x in enumerate(seg) if re.match(r'^Respuesta',x[4])]
    letters=[]
    for j in anss:
        m=re.search(r'Respuesta\s*[:;]?\s*\.?\s*([A-F])',seg[j][4]); letters.append(m.group(1) if m else '?')
    print(g,'n',n,'ans',len(anss))
    # alignment check
    exp=[r['answer'] for r in recs[g]]
    for k in range(min(len(exp),len(letters))):
        if exp[k]!=letters[k] and letters[k]!='?':
            print('  mismatch at',k+1,exp[k],letters[k])
    prev=-1
    for k in range(min(n,len(anss))):
        j=anss[k]
        region=seg[prev+1:j]
        prev=j
        if not region: issues.append((g,k+1,'empty'));continue
        first=region[0]
        rec=recs[g][k]
        qid=f'{g}{k+1:03d}'
        item={'id':qid,'group':g,'n':k+1,'answer':rec['answer']}
        c=crop_range((first[0],first[2]-6),(seg[j][0],seg[j][2]-4))
        item['letters']=[o[0] for o in rec['options']] if len(rec['options'])>=2 else ['A','B','C','D']
        if c is None: issues.append((g,k+1,'nocrop'));continue
        c.save(f'web/img/{qid}.png',optimize=True)
        data.append(item)
json.dump(data,open('questions.json','w',encoding='utf8'),ensure_ascii=False)
print(len(data),issues[:20])

if os.environ.get('DBG'):
    for g,idx in (('III',range(82,89)),('IV',range(40,45))):
        s=pos[g]; e=pos[order[order.index(g)+1]] if g!='IV' else len(ev)
        seg=ev[s+1:e]
        anss=[j for j,x in enumerate(seg) if re.match(r'^Respuesta',x[4])]
        for k in idx: print(g,k+1,seg[anss[k]])
