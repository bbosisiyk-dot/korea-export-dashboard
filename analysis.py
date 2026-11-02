"""지표 계산 + 분류 규칙 (원본 대시보드 23개 품목 라벨을 재현하도록 역산한 규칙)"""
import numpy as np
T=dict(HOT=100, ACCEL=15, HIGHG=20, STRONG3M=10, DECEL=-15, SLOPE=-0.9, TURN_WIN=3)   # 임계값
LUMPY={'선박'}
def analyze(rows):
    """rows: [(y,m,value,yoy)] 시간순 → dict"""
    v=[r[2] for r in rows]; y=[r[3] for r in rows]; n=len(v)
    d=[None]+[round(y[i]-y[i-1],1) for i in range(1,n)]
    ma=[None]*11+[float(np.mean(v[i-11:i+1])) for i in range(11,n)]
    mad=[None if m is None else v[i]/m-1 for i,m in enumerate(ma)]
    return dict(rows=rows,v=v,y=y,d=d,ma=ma,mad=mad,n=n)
def classify(name,a):
    y,d,v=a['y'],a['d'],a['v']; L=y[-1]; D=d[-1]; a3=float(np.mean(y[-3:])); d3=float(np.mean([x for x in d[-3:] if x is not None]))
    slope=float(np.polyfit(range(6),y[-6:],1)[0]); prev=y[-2]
    neg_recent=any(x<0 for x in y[-1-T['TURN_WIN']:-1])
    if L>=T['HOT'] and a3>=T['HOT']: k=('hot','초고성장','최근 3개월 YoY 평균이 매우 높고 최신월도 압도적입니다.')
    elif name in LUMPY and L>0 and a3>=T['STRONG3M']: k=('lumpy','수주형 강세','인도 시점 변동성이 크지만 최근 수출액과 YoY가 모두 강합니다.')
    elif L<0:
        if prev>0: k=('caution','재하락 주의','직전월 플러스 이후 다시 마이너스로 내려왔습니다.')
        elif slope>=T['SLOPE']: k=('watch','회복 관찰','아직 마이너스지만 최근 기울기는 개선 쪽입니다.')
        else: k=('weak','부진 지속','최근 성장률이 마이너스에 머물러 있습니다.')
    elif neg_recent: k=('turn','플러스 전환','최근 마이너스 구간을 지나 양의 성장률로 돌아섰습니다.')
    elif D<=T['DECEL']: k=('caution','둔화 주의','성장은 유지되지만 직전월 대비 속도가 둔화했습니다.')
    elif a3>=T['STRONG3M']: k=('strong','고성장 지속','양의 성장률이 이어지고 최근 평균도 두 자릿수입니다.')
    else: k=('watch','완만한 플러스','양의 성장률이 이어지지만 최근 평균은 한 자릿수입니다.')
    if D>=T['ACCEL']: mo=('가속 확대','YoY의 1차 미분이 큰 폭의 플러스입니다.')
    elif D>=0: mo=('가속 유지','YoY가 전월보다 더 높아졌습니다.')
    elif L>=T['HIGHG']: mo=('고성장 둔화','절대 성장률은 높지만 YoY의 1차 미분이 마이너스로 꺾였습니다.')
    else: mo=('기울기 둔화','YoY가 전월보다 낮아졌습니다.')
    return dict(cls=k[0],label=k[1],desc=k[2],mo=mo,L=L,D=D,a3=a3,d3=d3,slope=slope)
