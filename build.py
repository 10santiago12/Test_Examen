import re,json
t=open('manual.txt',encoding='utf8',errors='replace').read()
t=t.replace('�','?')
# decode with proper encoding instead
raw=open('manual.txt','rb').read()
try: t=raw.decode('utf8')
except: t=raw.decode('latin-1')
HDR=re.compile(r'Documento de Apoyo|^\s*Versi.n\s|^\s*P.gina\s|Vigencia|MANUAL PRUEBA|Tomado de la Resoluci|^\s*\d{1,3}\s*$|C.digo\s+D CE|^\s*P.gina\s*$')
parts=re.split(r'\n\s*GRUPO (I{1,3}|IV)\s*\n',t)
groups={}
for i in range(1,len(parts),2):
    body=parts[i+1]
    lines=[l for l in body.split('\n') if not HDR.search(l)]
    recs=[];cur=[]
    for l in lines:
        m=re.match(r'^\s*Respuesta\s*[:;]?\s*\.?\s*([A-F])',l)
        if m:
            recs.append((cur,m.group(1)));cur=[]
        else: cur.append(l)
    out=[]
    for cur,ans in recs:
        opts=[];
        for l in cur:
            s=l.strip()
            if not s: continue
            m=re.match(r'^([A-F])\s*[\.\)]\s*(.*)$',s)
            if m and (len(opts)==0 and m.group(1)=='A' or opts and ord(m.group(1))==ord(opts[-1][0])+1):
                opts.append([m.group(1),m.group(2)])
            elif opts: opts[-1][1]+=' '+s
        out.append({'options':opts,'answer':ans})
    groups[parts[i]]=out
json.dump(groups,open('records.json','w',encoding='utf8'),ensure_ascii=False,indent=0)
for g,r in groups.items():
    bad=[k+1 for k,x in enumerate(r) if len(x['options'])<2 or x['answer'] not in [o[0] for o in x['options']]]
    print(g,len(r),'bad',bad)
