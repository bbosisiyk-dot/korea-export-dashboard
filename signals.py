"""데이터만으로 계산하는 '투자 신호' 6개 (보도자료 본문 해설은 사용하지 않음)"""
def _v(v): return f"{v:.0f}" if abs(v)>=100 else f"{v:.1f}"
def _p(v,s='%'): return f"{abs(v):.1f}{s}" if round(v,1)==0 else f"{v:+.1f}{s}"
def _it(n,A,C): return f"{n} {_v(A[n]['v'][-1])}억 달러({_p(C[n]['L'])})"
def generate(A,C):
    N=list(A); out=[]
    # 1 집계기간 내 최고 수출액 갱신
    rec=[n for n in N if A[n]['n']>=13 and A[n]['v'][-1]>=max(A[n]['v'][:-1])]
    rec.sort(key=lambda n:-C[n]['L'])
    out.append(('집계기간 최고 수출액 갱신', (f"{len(rec)}개 품목이 집계기간 중 월 수출액 최고치를 새로 썼습니다: "+', '.join(_it(n,A,C) for n in rec[:6])+('' if len(rec)<=6 else f" 외 {len(rec)-6}개")+'.') if rec else '이번 달 월 수출액 최고치를 새로 쓴 품목은 없습니다.'))
    # 2 AI 인프라 체인
    ai=[n for n in ('반도체','컴퓨터','SSD','MCP') if n in A]
    acc=[n for n in ai if C[n]['D']>=0]; dec=[n for n in ai if C[n]['D']<0]
    out.append(('AI 인프라 체인', ', '.join(_it(n,A,C) for n in ai)+f". ΔYoY 기준 가속 {len(acc)}개({', '.join(acc) or '-'}), 둔화 {len(dec)}개({', '.join(dec) or '-'}). 반도체·컴퓨터(SSD)·MCP를 함께 봐야 합니다."))
    # 3 플러스 품목 확산도
    pos=[n for n in N if C[n]['L']>0]; pprev=[n for n in N if A[n]['y'][-2]>0]
    out.append(('플러스 품목 확산도', f"{len(N)}개 중 {len(pos)}개 품목이 전년동월 대비 증가했습니다(전월 {len(pprev)}개). YoY 상위: "+', '.join(f"{n} {_p(C[n]['L'])}" for n in sorted(N,key=lambda n:-C[n]['L'])[:3])+'.'))
    # 4 가격 효과 경계
    en=[n for n in ('석유제품','석유화학') if n in A]
    out.append(('가격 효과 경계', ', '.join(f"{n} {_v(A[n]['v'][-1])}억 달러({_p(C[n]['L'])}, 3개월 평균 {_p(C[n]['a3'])})" for n in en)+'. 금액 YoY에는 단가 효과가 포함되므로 물량 회복으로 바로 해석하지 않도록 표시했습니다(물량·단가 분해는 보도자료 본문 확인).'))
    # 5 기저효과·변동성
    sw=sorted(N,key=lambda n:-abs(C[n]['D']))[:3]
    base=[]
    for n in N:
        v=A[n]['v']
        if len(v)>=14:
            dev=v[-13]/((v[-14]+v[-12])/2)-1
            if abs(dev)>=0.25: base.append((n,dev))
    t='YoY가 전월 대비 크게 움직인 품목: '+', '.join(f"{n} {_p(C[n]['L'])}(Δ{_p(C[n]['D'],'%p')})" for n in sw)+'.'
    if base: t+=' 전년 동월 수출액이 인접 월 평균에서 25% 이상 벗어난 품목(기저효과 가능): '+', '.join(f"{n}({_p(d*100,'%')})" for n,d in sorted(base,key=lambda x:-abs(x[1]))[:4])+'.'
    out.append(('기저효과·변동성 점검',t))
    # 6 마이너스 품목 점검 + 연속 플러스
    neg=sorted([n for n in N if C[n]['L']<0],key=lambda n:C[n]['L'])
    def streak(n):
        k=0
        for y in reversed(A[n]['y']):
            if y>0: k+=1
            else: break
        return k
    st=sorted(N,key=lambda n:-streak(n))[:3]
    t=(f"YoY 마이너스 품목 {len(neg)}개: "+', '.join(f"{n} {_p(C[n]['L'])}" for n in neg[:5])+'. ') if neg else 'YoY 마이너스 품목이 없습니다. '
    out.append(('마이너스 품목 점검',t+'연속 플러스 최장: '+', '.join(f"{n} {streak(n)}개월" for n in st)+'.'))
    return [dict(title=a,text=b) for a,b in out]
