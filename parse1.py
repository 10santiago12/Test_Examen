import re
t=open('manual.txt',encoding='utf8',errors='replace').read()
# split groups
parts=re.split(r'\n\s*GRUPO (I{1,3}|IV)\s*\n',t)
print(len(parts))
for i in range(1,len(parts),2):
    print(parts[i], len(re.findall(r'^\s*Respuesta\s*:',parts[i+1],flags=re.M)))
o=open('ocr.txt',encoding='utf8').read()
po=re.split(r'\n(?=GRUPO (?:1|11|111|IV)\b)',o)
for g in po[1:]:
    nums=[int(m.group(1)) for m in re.finditer(r'^(\d{1,3})[\.,] ',g,flags=re.M)]
    print(g[:9],len(nums),nums[:3],nums[-3:], len(re.findall(r'^Respuesta',g,flags=re.M)))
