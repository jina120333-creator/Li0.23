# Li, Yang & Yang (2020) 교각 세굴 실험과의 시간 정렬 비교 절차

대상 논문: *Influence of Scour Development on Turbulent Flow Field in Front of a Bridge Pier*, Water 2020, 12, 2370.
실험 조건: D = 4 cm, h = 5 cm, U0 = 0.233 m/s, u\* = 0.016 m/s, d50 = 0.6 mm, clear-water (Θ0 = 0.029 < Θcr = 0.033).

## 1. 시간 변환 — 논문의 시간축은 초가 아니라 무차원 시간 t\*

```
t* = sqrt(g(s-1)·d50³)/D² · t = 0.03696 · t     →   t* 1 = 27.06 s
```

| t\* | 실제 시간 | 비고 |
|-----|-----------|------|
| 2   | 54 s      | 논문 PIV 첫 측정 시점 |
| 11  | 298 s     | PIV 두 번째 시점 (~5분) |
| 133 | 60 min    | |
| 931 | 420 min   | 실험 종료 |

## 2. 비교 기준값 (논문 Fig. 5 디지타이징, 오차 ±0.02 S/D)

| t_exp [s] | t\* | side 세굴심 | front 세굴심 |
|-----------|-----|------------|--------------|
| 54  | 2  | ~20 mm (S/D 0.50) | ~12 mm (첫 기록점, t\*=2~6 사이) |
| 298 | 11 | ~24 mm (S/D 0.60) | ~13–18 mm |
| 595 | 22 | ~28 mm | ~20 mm |

전체 디지타이징 데이터는 `scripts/extract_scour.py`의 `PAPER_SIDE` / `PAPER_FRONT` 배열에 있습니다.
주의: 논문의 지수 피팅식(Eq. 2)은 c2 < 1이라 t→0에서 세굴률이 무한대가 되는 형태이므로
첫 실측점 이전 구간으로 외삽해서 비교하면 안 됩니다. 실측점과 직접 비교하세요.

## 3. 시간 정렬 방법 — 2단계 실행 (Allrun이 자동 수행)

실험의 t = 0은 "평평한 하상 위에 목표 유량이 확립된 순간"입니다. 시뮬레이션에서
내부 유동장은 정지 상태에서 시작하므로, 유동 발달(스핀업) 구간을 세굴 시계에서
분리해야 실험과 시간이 맞습니다.

```
Stage 0 (t_sim = 0–3 s)    : 하상 미세조정(settling).  mus/mu2 = 10/10.5,
                             maxDeltaT = 2e-4.  하상은 setExprFields가
                             Johnson-Jackson 평형 압밀 프로파일
                             (α: 표면 0.570 → 바닥 0.6125)로 초기화하므로
                             자중 붕괴 없이 잔여 불균형(수십 Pa)만 완화.
Stage 1 (t_sim = 3–60 s)   : 하상 동결 스핀업.  maxDeltaT = 5e-4.
                             하상은 강체처럼 고정되고 유동/난류장만 발달.
Stage 2 (t_sim = 60–360 s) : mus/mu2 = 0.63/1.13 복원, maxDeltaT = 2e-4,
                             세굴 진행.   ★ 실험 시계:  t_exp = t_sim − 60
```

★ 압밀 안정성의 핵심은 `PPressureModel MuI` (granularRheologyProperties):
팽창성 입자압 pa = (Bφ·α/(αMaxG−α))²·ρa·d²·|D|² 가 α → alphaMaxG(0.625)에서
발산하며 과잉 압밀을 막아 줍니다. `none`으로 두면 α가 Johnson-Jackson
pff의 특이점(alphaMax = 0.635)까지 그대로 압밀되어 pff ~ 1e10 Pa에 셀이
고착되고, 그 셀에서 나오는 ±10 m/s 속도 제트가 dt를 짓눌러 계산이
사실상 멈춥니다 (초기 발산의 근본 원인). alphaMaxG < alphaMax 를 반드시
유지하세요. mus/mu2/I0/Bphi/relaxPa 값은 sedFoam 3DScour 튜토리얼
(Nagel et al. 2020, 원형 실린더 세굴, 검증됨) 값입니다.
여기에 더해 setExprFieldsDict가 하상 α를 JJ 평형 압밀 프로파일로 직접
초기화해 붕괴 과정 자체를 제거합니다 (튜토리얼의 1D 컬럼 프리커서
→ funkySetFields 매핑을 해석적 프로파일로 대체한 것). 그래도 불안정하면
1D 프리커서 방식이 최후의 정석입니다.

- `endTime`, `mus·mu2`, `maxCo·maxAlphaCo·maxDeltaT`는 각각
  `system/endTimeControl`, `constant/musControl`, `system/timeStepControl`
  include 파일로 분리되어 있고 Allrun 스크립트가 단계 전환 시 다시 씁니다.
- ★ 동결 시 mu2도 함께 키워야 합니다 (mu2 > mus 유지). mu(I)는 I→0에서 mus,
  I→∞에서 mu2로 가는 보간이므로, mus=10에 mu2=0.97을 그대로 두면 전단이
  커질수록 마찰이 10→0.97로 "약해지는" velocity-weakening 유변학이 되어
  수학적으로 불량설정(ill-posed) — 스핀업 발산의 주원인 중 하나였습니다.
- 스핀업 단축을 위해 `setExprFields`(system/setExprFieldsDict)로 내부장을
  inlet과 동일한 로그 프로파일(U.b, omega.b)로 초기화합니다.
- 스핀업 수렴 판정: `python3 scripts/check_approach_flow.py`
  → x = −0.4 m (10D 상류)에서 깊이평균 U ≈ 0.233 m/s, 로그법칙 피팅 u\* ≈ 0.016 m/s가
  정체되면 수렴. **u\*가 0.016에 못 미치면 clear-water 특성상 세굴이 크게
  과소예측되므로, 세굴 단계 결과를 보기 전에 반드시 이 값부터 확인하세요.**
  60 s로 부족하면 Allrun의 `SPINUP_END`를 늘리면 됩니다 (SCOUR_END = SPINUP_END + 300 유지).

### 실행

```bash
sbatch Allrun        # SLURM 배치 (192 코어, mpiexec.hydra + sedFoam)
./Allclean           # 초기화 (0_org와 stage-control 기본값은 보존)
```

Allrun은 mesh → setFields → setExprFields → decomposePar 후,
mus/endTime include 파일을 바꿔 스핀업(log.spinup)과 세굴(log.scour)을
연속 실행합니다. 각 단계 로그: log.block, log.snappy, log.setFields,
log.setExprFields, log.decompose, log.spinup, log.scour.
스핀업 길이를 바꾸려면 Allrun 상단의 SPINUP_END를 수정하고
SCOUR_END = SPINUP_END + 300으로 맞춘 뒤, 후처리 시
`extract_scour.py --t0 <SPINUP_END>`를 같은 값으로 실행하세요.

## 4. 세굴심 추출과 비교

- controlDict의 `bedLevels` functionObject가 교각 표면에서 2.5 mm 떨어진
  전면(front)·양측면(sideL/sideR) 연직선에서 alpha.a 프로파일을 1초마다 기록합니다
  (실험도 교각 표면의 눈금으로 읽었으므로 같은 위치 기준).
- 실행 후:

```bash
python3 scripts/extract_scour.py --t0 60
```

  → `scour_timeseries.csv` (t_sim, t_exp, t\*, S_front, S_side, S/D)와
  논문 실측점을 겹친 `scour_vs_paper.png` 생성.
  하상면 정의는 alpha.a = 0.5 등고면 기준이며 `--alpha-c`로 변경 가능
  (예: alphaMinFriction 기준이면 `--alpha-c 0.57`).
- 단일 시점(54 s)보다 **S(t) 곡선 형태**로 비교할 것. 실험 쪽도 펌프 기동
  절차로 t = 0에 수십 초의 불확실성이 있으므로, 곡선이 맞는데 시간축이
  ±30 s 어긋나는 정도는 허용 범위로 보는 것이 합리적입니다.

## 5. 이번에 함께 변경된 설정 (세굴 과소예측 완화)

| 파일 | 변경 | 이유 |
|------|------|------|
| `system/fvSchemes` | `div(phi.a,U.a)`, `div(phi.b,U.b)`: 1차 upwind → `linearUpwind` | 1차 upwind는 측면 가속·말굽와류를 수치확산으로 약화시켜 하상 전단응력(→세굴률)을 과소평가. clear-water(Θ0/Θcr≈0.88)에서 특히 민감 |
| `constant/turbulenceProperties.b` | `twophasekEpsilon` → `twophasekOmega` (Wilcox 2006) | sedFoam에 kOmegaSST는 없음. k-ω가 k-ε보다 역압력구배·말굽와류 예측에 유리. 빌드에 없으면 주석의 twophasekEpsilon으로 복귀 |
| `0_org/omega.b` (신규) | inlet은 평형 로그층 프로파일 ω = u\*/(√Cμ·κ·z), 벽은 omegaWallFunction | k-ω 전환에 필요 |
| `system/snappyHexMeshDict` | scourBedFineBox z 하한 −0.020 → −0.035 | t\*=11 실측 측면 세굴 ~24 mm가 fine 영역 밖으로 뚫고 나가는 것 방지 |
| `system/setFieldsDict` | 초기 alpha.a 0.58 → 0.60 | 0.58은 alphaMinFriction(0.57) 직상이라 런 중 침하·다짐이 발생해 세굴심 판독 오염 |
| `constant/twophaseRASProperties` | SUS 0 → 1 | 난류 부유 항 복원 (sedFoam 세굴 케이스 표준) |
| `system/controlDict` | endTime 360 (include화), writeInterval 0.1 → 2 s, 모니터링 functionObjects 추가 | 세굴 시계 300 s 확보 + 디스크 절약 (시계열은 1 s 간격 sets가 담당) |

추가 여력이 있으면: `snappyHexMeshDict`의 scourBedFineBox refinement level 2 → 3
(수평 2.5 mm → 1.25 mm). 셀 수가 ~8배 늘지만 측면 전단 증폭 해상에 가장 효과적입니다.

## 6. 남는 한계 (미리 알아둘 것)

- RAS(k-ω 포함)는 말굽와류의 비정상 다이내믹스(bimodal oscillation)를 시간평균으로만
  다루므로 front 세굴률은 여전히 과소예측될 수 있습니다. 문헌에서도 RAS 기반
  세굴 모델은 초기 세굴률을 실험보다 낮게 예측하는 경향이 보고됩니다.
- 실험의 초기 세굴(54 s에 측면 20 mm)은 매우 빠른 편이라, 곡선의 후반부(t\*=11
  전후)가 맞는지부터 확인하고 초기 구간은 경향성 위주로 평가하는 것을 권합니다.
