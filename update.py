"""매월 실행: pdf/YYYY-MM.pdf 를 파싱해 data/export_industry_monthly.csv 를 갱신하고 docs/index.html 을 다시 생성.
같은 달 수치는 최신 보도자료가 우선. PDF 파싱이 비정상이면 비정상 종료(워크플로 실패로 표시)."""
import csv, glob, re, sys, json
from parse_pdf import parse_pdf
from build_dashboard import render, load
CSV='data/export_industry_monthly.csv'; ALIAS={'생활유아용품':'생활용품'}
def main():
    rows=list(csv.DictReader(open(CSV,encoding='utf-8-sig'))); grp={r['item']:r['group'] for r in rows}
    D={(r['item'],int(r['year']),int(r['month'])):(float(r['export_100M_usd']),float(r['yoy_pct']),r['source']) for r in rows}
    done={r['source'] for r in rows}
    for f in sorted(glob.glob('pdf/*.pdf')):
        y,m=map(int,re.search(r'(\d{4})-(\d{2})\.pdf$',f).groups()); tag=f'{y}-{m:02d} 수출입동향'
        P=parse_pdf(f,m,y); P={ALIAS.get(k,k):v for k,v in P.items()}
        miss=[n for n in grp if n not in P]; extra=[n for n in P if n not in grp]
        if miss or any(len(v)!=13 for v in P.values()): sys.exit(f'{f}: 파싱 실패/품목 누락 {miss}')
        if extra: print('경고: 신규 품목(무시됨)',extra,file=sys.stderr)
        for n in grp:
            for (yy,mm),(a,yo) in P[n].items(): D[(n,yy,mm)]=(round(a/100+1e-9,2),yo,tag)
    with open(CSV,'w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f); w.writerow(['group','item','year','month','export_100M_usd','yoy_pct','source'])
        order=list(dict.fromkeys(r['item'] for r in rows))
        for n in order:
            for (i,y,m),(v,yo,s) in sorted((k,v) for k,v in D.items() if k[0]==n): w.writerow([grp[n],n,y,m,v,yo,s])
    render(load(),json.load(open('data/signals.json',encoding='utf-8')))
    print('완료: 최신월',max((y,m) for (_,y,m) in D))
if __name__=='__main__': main()
