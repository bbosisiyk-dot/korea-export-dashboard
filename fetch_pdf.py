"""산업통상부 보도자료에서 '수출입 동향' 최신 PDF를 pdf/YYYY-MM.pdf 로 내려받는다(베스트 에포트).
※ 사이트 구조가 바뀌면 실패할 수 있으며, 그 경우 PDF를 pdf/ 폴더에 직접 넣고 커밋하면 동일하게 갱신된다."""
import re, os, sys, requests
from urllib.parse import urljoin
LIST=os.environ.get('MOTIR_LIST','https://www.motir.go.kr/kor/article/ATCL03465409b')
H={'User-Agent':'Mozilla/5.0'}
def main():
    html=requests.get(LIST,headers=H,timeout=30).text
    links=re.findall(r'<a[^>]+href="([^"]+/view[^"]*)"[^>]*>(.*?)</a>',html,flags=re.S)
    got=0
    for href,title in links:
        t=re.sub(r'<[^>]+>|\s+',' ',title)
        m=re.search(r'(\d{4})년\s*(\d{1,2})월\s*수출입\s*동향',t)
        if not m: continue
        out=f'pdf/{m.group(1)}-{int(m.group(2)):02d}.pdf'
        if os.path.exists(out): continue
        page=requests.get(urljoin(LIST,href),headers=H,timeout=30).text
        for h,name in re.findall(r'<a[^>]+href="([^"]*/attach/down/[^"]+)"[^>]*>(.*?)</a>',page,flags=re.S):
            if '수출입동향' in re.sub(r'<[^>]+>|\s+','',name) and '.pdf' in name.lower():
                open(out,'wb').write(requests.get(urljoin(LIST,h),headers=H,timeout=60).content); print('다운로드',out); got+=1; break
    print('신규',got)
if __name__=='__main__': main()
