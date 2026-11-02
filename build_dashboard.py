"""data/export_industry_monthly.csv → docs/index.html (원본 대시보드와 동일한 레이아웃·CSS)"""
import csv, json, sys, datetime, html, collections
from analysis import analyze, classify
from signals import generate
from build_data import S1, S2
def f3(v): return f"{v:.0f}" if abs(v)>=100 else f"{v:.1f}"
def pc(v,p='%'): return f"{abs(v):.1f}{p}" if round(v,1)==0 else f"{v:+.1f}{p}"
def cl(v): return ' class="pos"' if v>0 else (' class="neg"' if v<0 else '')
def load(path='data/export_industry_monthly.csv'):
    S=collections.defaultdict(list)
    for r in csv.DictReader(open(path,encoding='utf-8-sig')): S[r['item']].append((int(r['year']),int(r['month']),float(r['export_100M_usd']),float(r['yoy_pct'])))
    return {k:sorted(v) for k,v in S.items()}
def tip(name,a,i,order='v'):
    y,m=a['rows'][i][:2]; ma=a['ma'][i]; d=a['d'][i]
    p=[name,f"{y}.{m}"]
    ev=f"수출액 {f3(a['v'][i])}억"; yy=f"YoY {pc(a['y'][i])}"; dd=f"ΔYoY {'-' if d is None else pc(d,'%p')}"; mm=f"12M MA {'-' if ma is None else f3(ma)+'억'}"
    p+=[ev,yy,dd,mm] if order=='v' else [yy,dd,ev,mm]
    return html.escape(' | '.join(p),quote=True)
def value_chart(name,a):
    n=a['n']; X=[34+i*336/(n-1) for i in range(n)]
    c=a['v']+[m for m in a['ma'] if m is not None]; mn,mx=min(c),max(c); pad=(mx-mn)*.08; lo,hi=mn-pad,mx+pad
    Y=lambda v:110-(v-lo)/(hi-lo)*98
    pts=lambda idx,vals:' '.join(f"{X[i]:.1f},{Y(vals[i]):.1f}" for i in idx)
    s='<line x1="34" y1="110.0" x2="370" y2="110.0" class="grid"></line><line x1="34" y1="61.0" x2="370" y2="61.0" class="grid"></line><line x1="34" y1="12.0" x2="370" y2="12.0" class="grid"></line>'
    s+=f'<polyline points="{pts(range(n),a["v"])}" class="value-line"></polyline>'
    mi=[i for i in range(n) if a['ma'][i] is not None]
    if mi: s+=f'<polyline points="{pts(mi,a["ma"])}" class="ma-line"></polyline>'
    for i in sorted(set(list(range(0,n,6))+[n-1])): s+=f'<circle cx="{X[i]:.1f}" cy="{Y(a["v"][i]):.1f}" r="2.2" class="value-marker"></circle>'
    s+=f'<circle cx="{X[-1]:.1f}" cy="{Y(a["v"][-1]):.1f}" r="3.5" class="latest-dot"></circle>'
    s+=f'<text x="312.0" y="{Y(a["v"][-1])-7:.1f}" class="chart-label">최신 {f3(a["v"][-1])}억</text>'
    jh=a['v'].index(max(a['v'])); j=a['v'].index(min(a['v']))
    if jh<n-2: s+=f'<text x="{X[jh]+6:.1f}" y="{Y(a["v"][jh])-7:.1f}" class="chart-label">고점 {f3(a["v"][jh])}억</text>'
    if j<n-3: s+=f'<text x="{X[j]+6:.1f}" y="{Y(a["v"][j])-7:.1f}" class="chart-label">저점 {f3(a["v"][j])}억</text>'
    if mi: s+=f'<text x="308.0" y="{Y(a["ma"][-1])+12:.1f}" class="ma-label">MA {f3(a["ma"][-1])}억</text>'
    for i in range(n):
        t=tip(name,a,i); s+=f'<circle cx="{X[i]:.1f}" cy="{Y(a["v"][i]):.1f}" r="7" class="chart-hit" data-tooltip="{t}"><title>{t}</title></circle>'
    ax=lambda v:f"{v:.0f}"
    s+=f'<text x="2" y="16.0" class="axis-label">{ax(hi)}</text><text x="2" y="110.0" class="axis-label">{ax(lo)}</text><text x="34" y="127" class="axis-label">{a["rows"][0][0]}.{a["rows"][0][1]}</text><text x="328" y="127" class="axis-label">{a["rows"][-1][0]}.{a["rows"][-1][1]}</text>'
    return f'<svg viewBox="0 0 380 132" role="img" aria-label="수출액 추이와 12개월 이동평균">{s}</svg>'
def yoy_chart(name,a):
    n=a['n']; m_=min(max(max(abs(x) for x in a['y'])*1.12,30),250); k=49/m_; step=286/(n-1+.807); bw=step*.807
    s='<line x1="34" y1="61.0" x2="320" y2="61.0" class="zero-line"></line><line x1="34" y1="12.0" x2="320" y2="12.0" class="grid"></line><line x1="34" y1="110.0" x2="320" y2="110.0" class="grid"></line>'
    B=[]
    for i in range(n):
        v=a['y'][i]; h=min(49.0,max(1.0,abs(v)*k)); x=34+i*step; y=61-h if v>=0 else 61.0; B.append((x,y,h)); t=tip(name,a,i,'y')
        s+=f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" class="{"bar-pos" if v>=0 else "bar-neg"} chart-bar" data-tooltip="{t}"><title>{t}</title></rect>'
    cand=[n-1,a['y'].index(max(a['y'])),a['y'].index(min(a['y']))]; got=[]
    for i in cand:
        if all(abs(B[i][0]-B[j][0])>=35 for j in got): got.append(i)
    for i in sorted(got):
        x,y,h=B[i]; lab=pc(a['y'][i]); ly=y-4 if a['y'][i]>=0 else y+h+10
        lx=min(x+bw/2-len(lab)*3.2,286.0); s+=f'<text x="{lx:.1f}" y="{ly:.1f}" class="bar-label">{lab}</text>'
    s+=f'<text x="2" y="16.0" class="axis-label">{m_:+.0f}</text><text x="2" y="110.0" class="axis-label">-{m_:.0f}</text><text x="34" y="127" class="axis-label">{a["rows"][0][0]}.{a["rows"][0][1]}</text><text x="278" y="127" class="axis-label">{a["rows"][-1][0]}.{a["rows"][-1][1]}</text>'
    return f'<svg viewBox="0 0 330 132" role="img" aria-label="전년동월 대비 성장률">{s}</svg>'
def article(name,a,c):
    L=a['rows'][-1]; ma=a['ma'][-1]; mad=a['mad'][-1]
    dl=[('최신월',f"{L[0]}.{L[1]}",''),('수출액',f3(a['v'][-1])+'억',''),('YoY',pc(c['L']),cl(c['L'])),('ΔYoY',pc(c['D'],'%p'),cl(c['D'])),
        ('3개월 평균 YoY',pc(c['a3']),''),('3개월 평균 ΔYoY',pc(c['d3'],'%p'),cl(c['d3'])),('12M MA',f3(ma)+'억' if ma else '-',''),('MA 대비',pc(mad*100) if mad is not None else '-','')]
    dls=''.join(f'<div><dt>{k}</dt><dd{c_}>{v}</dd></div>' for k,v,c_ in dl)
    th=''.join(f'<th scope="col">{y}.{m}</th>' for y,m,*_ in a['rows'])
    def row(lab,vals): return f'<tr><th scope="row">{lab}</th>'+''.join(vals)+'</tr>'
    tv=row('수출액',[f'<td>{v:.1f}</td>' for v in a['v']])
    ty=row('YoY',[f'<td{cl(v)}>{pc(v)}</td>'.replace(' class="pos"',' class="pos"').replace('<td class','<td class') for v in a['y']])
    td=row('ΔYoY',[f'<td{cl(v)}>{pc(v,"%p")}</td>' if v is not None else '<td>-</td>' for v in a['d']])
    tm=row('12M MA',[f'<td>{m:.1f}</td>' if m else '<td>-</td>' for m in a['ma']])
    tx=row('MA 대비',[f'<td{cl(v)}>{pc(v*100)}</td>' if v is not None else '<td>-</td>' for v in a['mad']])
    return f'''<article class="industry-row">
      <div class="industry-meta">
        <div class="item-head">
          <h3>{name}</h3>
          <span class="badge badge-{c['cls']}">{c['label']}</span>
        </div>
        <dl>{dls}</dl>
        <p>{c['desc']}</p>
        <p class="momentum-note"><b>{c['mo'][0]}</b> · {c['mo'][1]}</p>
      </div>
      <div class="chart-cell"><div class="chart-title">수출액 및 12개월 이동평균</div>{value_chart(name,a)}</div>
      <div class="chart-cell"><div class="chart-title">YoY 성장률</div>{yoy_chart(name,a)}</div>
      <div class="data-table-wrap"><div class="table-title">월별 원자료</div>
        <table class="data-table" aria-label="{name} 월별 수출 데이터"><thead><tr><th scope="col">구분</th>{th}</tr></thead><tbody>{tv}{ty}{td}{tm}{tx}</tbody></table></div>
    </article>'''
def chips(L,key,suf): return '<div class="chip-wrap">'+''.join(f'<span class="mini-chip"><b>{n}</b> {pc(key(n),suf)}</span>' for n in L)+'</div>'
def render(S,sig=None,out='docs/index.html'):
    A={n:analyze(S[n]) for n in S1+S2}; C={n:classify(n,A[n]) for n in A}; names=list(A)
    last=max(S[n][-1][:2] for n in S); first=min(S[n][0][:2] for n in S); ym=lambda t:f"{t[0]}.{t[1]}"
    top=sorted(names,key=lambda n:-C[n]['L'])[:6]
    turn=sorted([n for n in names if C[n]['cls'] in('turn','watch')],key=lambda n:-C[n]['L'])[:7]
    weak=sorted([n for n in names if C[n]['L']<0 and C[n]['D']<0],key=lambda n:C[n]['L'])[:6]
    acc=sorted([n for n in names if C[n]['D']>=15],key=lambda n:-C[n]['D'])[:6]
    dec=sorted([n for n in names if C[n]['L']>0 and C[n]['D']<0],key=lambda n:C[n]['D'])[:6]
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y-%m-%d %H:%M')
    css=open('template/style.css',encoding='utf-8').read(); js=open('template/tooltip.js',encoding='utf-8').read()
    sig=sig or {'items':generate(A,C)}; stale=' <small>(데이터 기반 자동 생성)</small>'
    sg=''.join(f'<li><strong>{i["title"]}</strong><span>{i["text"]}</span></li>' for i in sig['items'])
    sec=lambda t,p,L,leg='':f'<section><div class="section-head"><div><h2>{t}</h2><p>{p}</p></div>{leg}</div><div class="industry-list">'+''.join(article(n,A[n],C[n]) for n in L)+'</div></section>'
    leg='<div class="legend"><span><i class="l1"></i>수출액</span><span><i class="l2"></i>12M MA</span></div>'
    H=f'''<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>한국 수출 산업 월별 트렌드 대시보드</title>
<style>
{css}</style></head>
<body>
<header><div class="header-inner"><div>
<div class="eyebrow">산업통상부 수출입동향 기반</div><h1>한국 수출 산업 월별 트렌드 대시보드</h1>
<p>기간: {ym(first)}-{ym(last)} · 최신월: {ym(last)} · 단위: 수출액은 억 달러, YoY는 전년동월 대비 · 생성: {now}</p></div></div></header>
<main>
<section class="summary-grid">
<div class="summary-box"><h2>초고성장/강세</h2>{chips(top,lambda n:C[n]['L'],'%')}</div>
<div class="summary-box"><h2>턴어라운드 후보</h2>{chips(turn,lambda n:C[n]['L'],'%')}</div>
<div class="summary-box"><h2>부진/재하락</h2>{chips(weak,lambda n:C[n]['L'],'%')}</div>
<div class="summary-box"><h2>분류 기준</h2><p>최신 YoY, 최근 3개월 평균, 6개월 기울기, 12개월 이동평균 대비 위치를 함께 보았습니다. 별도로 ΔYoY를 1차 미분처럼 추적합니다.</p></div>
</section>
<section class="derivative-panel">
<div class="derivative-box"><h2>1차 미분 읽는 법</h2><p>여기서 1차 미분은 <b>ΔYoY = 이번 달 YoY - 전월 YoY</b>입니다. YoY가 높아도 ΔYoY가 마이너스로 바뀌면 기대의 가속이 꺾이는 신호로 볼 수 있습니다.</p></div>
<div class="derivative-box"><h2>가속 확대</h2>{chips(acc,lambda n:C[n]['D'],'%p')}</div>
<div class="derivative-box"><h2>고성장 둔화/기울기 하락</h2>{chips(dec,lambda n:C[n]['D'],'%p')}</div>
</section>
<section class="signal-panel"><h2>본문에서 따로 잡아야 할 투자 신호{stale}</h2><ul>{sg}</ul></section>
{sec('20대 주력 수출품목','각 행은 왼쪽부터 분류/핵심 지표, 수출액 추이와 12개월 이동평균, YoY 성장률입니다.',S1,leg)}
{sec('유망품목 및 소비재 관찰 리스트','부록의 OLED, SSD, MCP와 유망 소비재(의약품·패션의류)를 별도 추적했습니다.',S2)}
</main>
<footer><div class="footer-brand"><b>자료 출처</b></div>
<p>산업통상부 월간 「수출입동향」 보도자료(3보) 부록의 20대 품목·유망품목·유망 소비재 표를 사용했고, 같은 달이 여러 보도자료에 있으면 최신 자료를 우선했습니다. 원천 데이터: <code>data/export_industry_monthly.csv</code></p>
<p>※ 2026년 6월 통계부터 주요 품목이 15대→20대로 개편되어(전기기기·비철금속 신규, 세부품목 조정) 2025.5 이후 값은 신규 기준, 그 이전은 개편 전 기준입니다. 전기기기·비철금속은 2025.5부터 집계됩니다.</p>
<p>레이아웃·지표 설계는 모소밤부(blog.naver.com/bambooinvesting)의 「한국 수출 산업 월별 트렌드 대시보드」를 참고했습니다.</p></footer>
</main-end>
<div class="chart-tooltip" id="chart-tooltip" role="status" aria-live="polite"></div>
<script>
{js}</script></body></html>'''.replace('</main>\n<footer>','</main>\n<footer>').replace('</main-end>\n','')
    open(out,'w',encoding='utf-8').write(H); return A,C
if __name__=='__main__':
    render(load())
