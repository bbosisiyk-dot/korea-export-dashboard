"""산업통상부 월간 '수출입동향' PDF → 품목별 월 수출액(백만달러)·YoY(%) 추출 (pdftotext -layout 필요)"""
import re, subprocess, glob, sys
ALIAS={'철강':'철강제품'}
NUM=re.compile(r'^\(?[△\-+]?[\d,\.]+\)?$')
def num(s): return float(s.strip('()').replace(',','').replace('△','-').replace('+',''))
def is_amt(l):
    t=[x for x in l.split() if re.fullmatch(r'\d{1,3}(,\d{3})*',x)]
    return len(t)>=14
def yoy_of(l): return re.findall(r'\([^)]*\)',l)
def frag(l): return ''.join(x for x in re.sub(r'\([^)]*\)',' ',l).split() if not NUM.match(x))
def parse_pdf(path, month, year=2026):
    txt=subprocess.run(['pdftotext','-layout',path,'-'],capture_output=True,text=True).stdout
    a=txt.rfind('② 20대 품목별 수출 추이'); b=txt.find('다. 주요 지역별',a)
    L=txt[a:b].split('\n')
    cols=[(year-1,m) for m in range(month,13)]+[(year,m) for m in range(1,month+1)]
    out={}; i=0
    while i<len(L):
        if not is_amt(L[i]): i+=1; continue
        amts=[num(x) for x in L[i].split() if re.fullmatch(r'\d{1,3}(,\d{3})*',x)][-13:]
        name=frag(L[i]); j=i+1
        while j<len(L) and len(yoy_of(L[j]))<13: name+=frag(L[j]); j+=1
        y=[num(x) for x in yoy_of(L[j])][-13:]; name+=frag(L[j]); k=j+1
        while k<len(L) and L[k].strip() and not is_amt(L[k]) and not L[k].lstrip().startswith(('③','④','-')):
            f=frag(L[k]); name+=f
            if not f and len(L[k].split())>=13: break
            if not f: break
            k+=1
        name=ALIAS.get(re.sub(r'\s+','',name),re.sub(r'\s+','',name))
        out[name]={c:(a_,y_) for c,a_,y_ in zip(cols,amts,y)}
        i=j+1
    return out
