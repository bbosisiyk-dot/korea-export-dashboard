"""원본 HTML(2024.1~2026.4) + 신규 PDF(2025.5~) 병합 → data/export_industry_monthly.csv.  같은 달은 최신 PDF 우선."""
import csv, sys, os
from bs4 import BeautifulSoup
from parse_pdf import parse_pdf
import glob
ORIG=os.environ.get('ORIG_HTML','/mnt/user-data/uploads/한국_수출_산업_월별_트렌드_대시보드.html')
S1=['반도체','컴퓨터','석유제품','석유화학','자동차','일반기계','철강제품','자동차부품','디스플레이','선박','무선통신기기','바이오헬스','섬유','이차전지','가전','전기기기','비철금속','농수산식품','화장품','생활용품']
S2=['SSD','MCP','OLED','의약품','패션의류']
RENAME={'생활유아용품':'생활용품'}   # 20대 개편 후 명칭
def load_orig():
    b=BeautifulSoup(open(ORIG,encoding='utf-8').read(),'html.parser'); D={}
    for a in b.find_all('article'):
        n=a.find('h3').get_text(); rows=a.find('tbody').find_all('tr')
        ms=[th.get_text() for th in a.find('thead').find_all('th')][1:]
        v=[float(td.get_text()) for td in rows[0].find_all('td')]
        y=[float(td.get_text().replace('%','').replace('+','')) for td in rows[1].find_all('td')]
        D[RENAME.get(n,n)]={tuple(map(int,m.split('.'))):(x,yy,'원본 대시보드') for m,x,yy in zip(ms,v,y)}
    return D
def parse_all(d='pdf'):
    return {int(f[-6:-4]):parse_pdf(f,int(f[-6:-4])) for f in sorted(glob.glob(f'{d}/2026-*.pdf'))}
def merge(D,P):
    for m in sorted(P):
        for n,d in P[m].items():
            n=RENAME.get(n,n)
            if n=='생활용품' and '생활용품' in P[m] and n in P[m] and d is not P[m]['생활용품']: continue
            for k,(a,y) in d.items(): D.setdefault(n,{})[k]=(round(a/100+1e-9,2),y,f'2026-{m:02d} 수출입동향')
    return D
if __name__=='__main__':
    D=merge(load_orig(),parse_all())
    with open('data/export_industry_monthly.csv','w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f); w.writerow(['group','item','year','month','export_100M_usd','yoy_pct','source'])
        for g,L in (('20대',S1),('유망',S2)):
            for n in L:
                for (y,m),(v,yy,src) in sorted(D[n].items()): w.writerow([g,n,y,m,v,yy,src])
    print({n:len(D[n]) for n in S1+S2})
