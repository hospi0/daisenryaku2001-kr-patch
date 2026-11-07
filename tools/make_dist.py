# -*- coding: utf-8 -*-
r"""어드밴스드 대전략 2001 배포 묶음 — dist/Daisenryaku2001_KR_<VER>/ : 트랙 3 xdelta + xdelta.exe + readme.txt(CP949) + 한글패치_적용.bat
  (건버드 2 tools/make_dist.py 를 옮김, 2026-11-07) 바뀌는 트랙: 트랙 3 만. 트랙 1·2·cue 는 원본 그대로.
  검증: 원본 트랙 3 → xdelta 적용 → md5 = 빌드(work/disc) 트랙 3 md5.
  python tools/make_dist.py   (먼저 python tools/build.py --write)
"""
import hashlib, os, shutil, subprocess, sys, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)

VER = 'v0.9'
XDELTA = r'C:\claude\utils\xdelta.exe'
ROM = 'Advanced Daisenryaku 2001 (Japan)'
SRC = os.path.join(r'C:\claude\roms\dc', ROM)
OUT = os.path.join(ROOT, 'work', 'disc')
NAME = 'Daisenryaku2001_KR_' + VER
TITLE = '어드밴스드 대전략 2001 (드림캐스트 일본판) 한글 패치 ' + VER


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest().upper()


README = """3개의 트랙으로 이루어진 {rom} 의
트랙 3번에 패치하시면 됩니다.

원본md5 : {o}
패치md5 : {d}

입니다.


{title}
{line}

[ 적용 방법 ]

  1) 원본 트랙 3 파일을 이 폴더에 복사
       "{bin}"
  2) 한글패치_적용.bat 실행 → 이름 끝에 [KR] 이 붙은 파일이 만들어집니다
  3) 만든 파일 이름을 원본 트랙 3 이름으로 바꿔 넣고, 트랙 1·2 와 cue 는 원본 그대로 쓰세요

  직접 적용:
    xdelta.exe -d -B 536870912 -s "원본 트랙 3" "{patch}" "결과 파일"
  (Delta Patcher 같은 xdelta3 GUI 도구로 적용해도 됩니다. 원본이 다르면 xdelta 가 적용을 거부합니다.)


[ 바뀌는 것 ]

  - 메뉴, 도움말, 참모 조언, 각종 메시지
  - 유닛·병기 이름(원어 표기는 그대로)
  - 시나리오의 제목, 브리핑, 결과문, 지명, 부대 이름
  - 역사 뉴스 약 930건
  - 유닛 정보·무기·상태 화면의 그림 라벨, 시작 문구
  - 시나리오 제목 카드 29장: 원본 위에 작은 한글 뜻풀이
  - 동영상 7편의 해설 자막
  - 전투 화면 유닛 이름(원래 본체 BIOS 글꼴을 쓰는 곳이라 코드를 고쳤습니다)


[ 알려진 점 ]

  - 동영상의 연표와 큰 제목 글자, 스태프 롤은 원본 그대로입니다.
  - 인터넷 메뉴는 번역하지 않았습니다.
  - 칸이 좁은 곳은 띄어쓰기를 줄이거나 낱말을 줄였습니다.
"""

BAT = r"""@echo off
chcp 949 >nul
set "XD=%~dp0xdelta.exe"
if not exist "%~dp0{bin}" (
  echo   [오류] 원본 트랙 3 파일을 이 폴더에 넣어 주세요 - readme 참고.
  pause & exit /b 1
)
"%XD%" -d -f -B 536870912 -s "%~dp0{bin}" "%~dp0{patch}" "%~dp0{kbin}"
if errorlevel 1 (
  echo   [오류] 패치 실패 - 원본이 다를 수 있습니다 - readme 의 원본md5 확인.
  pause & exit /b 1
)
echo   완료: "{kbin}"
pause
"""


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    d = os.path.join(ROOT, 'dist', NAME)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    b = '%s (Track 3).bin' % ROM
    src, out = os.path.join(SRC, b), os.path.join(OUT, b)
    patch = NAME + '_Track3.xdelta'; pp = os.path.join(d, patch)
    subprocess.run([XDELTA, '-e', '-9', '-B', '536870912', '-f', '-s', src, out, pp], check=True)
    chk = os.path.join(d, '_check.bin')
    subprocess.run([XDELTA, '-d', '-f', '-B', '536870912', '-s', src, pp, chk], check=True)
    o, want, got = md5(src), md5(out), md5(chk)
    os.remove(chk)
    assert got == want, ('패치 적용 결과가 빌드와 다름', got, want)
    print('트랙 3 원본md5 %s → 패치md5 %s · %s %d B' % (o, want, patch, os.path.getsize(pp)))
    shutil.copy2(XDELTA, os.path.join(d, 'xdelta.exe'))
    kbin = '%s (Track 3) [KR].bin' % ROM
    readme = README.format(title=TITLE, line='=' * 60, rom=ROM, o=o, d=want, bin=b, patch=patch)
    open(os.path.join(d, 'readme.txt'), 'wb').write(readme.replace('\n', '\r\n').encode('cp949'))
    open(os.path.join(d, '한글패치_적용.bat'), 'wb').write(BAT.format(bin=b, patch=patch, kbin=kbin).replace('\n', '\r\n').encode('cp949'))
    z = os.path.join(ROOT, 'dist', NAME + '.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(os.listdir(d)):
            zf.write(os.path.join(d, f), NAME + '/' + f)
    print('완료', d)
    for f in sorted(os.listdir(d)):
        print('  %-56s %12d' % (f, os.path.getsize(os.path.join(d, f))))
    print('  zip %s %d B · md5 %s' % (os.path.basename(z), os.path.getsize(z), md5(z)))


if __name__ == '__main__':
    main()
