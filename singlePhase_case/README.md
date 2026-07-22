# 단상유동 케이스 (Single-Phase Flow Case) 설정 가이드

## 📋 개요

이 디렉토리는 sedFoam 이상유동(two-phase flow) 시뮬레이션과 비교할 수 있는 **단상유동(single-phase) 케이스**입니다.

### 주요 특징
- **솔버**: pimpleFoam (비정상 비압축성 유동)
- **유동**: 물(water) 단일 상만 고려
- **난류 모델**: k-epsilon (기본값, k-omega SST로 변경 가능)
- **시간**: sedFoam과 동일하게 0~3600초 (조정 가능)

---

## 📁 디렉토리 구조

```
singlePhase_case/
├── 0/                      # 초기 및 경계 조건
│   ├── p                  # 압력 필드
│   ├── U                  # 속도 필드
│   ├── k                  # 난류 운동 에너지
│   └── epsilon            # 난류 소산율
├── constant/              # 상수 특성
│   ├── transportProperties # 유체 특성 (밀도, 점성도)
│   ├── turbulenceProperties # 난류 모델 설정
│   └── g                  # 중력 가속도
└── system/                # 수치 해석 설정
    ├── controlDict        # 시간 제어
    ├── fvSchemes          # 수치 스킴
    ├── fvSolution         # 선형 솔버
    ├── blockMeshDict      # 메시 생성 (sedFoam에서 복사)
    └── decomposeParDict   # 병렬 분해 설정
```

---

## 🔧 실행 단계

### 1단계: 메시 생성
```bash
cd singlePhase_case/
blockMesh
```

### 2단계: 초기 조건 설정 (필요시)
sedFoam의 9초 후 결과를 초기 조건으로 사용하려면:
```bash
# sedFoam의 마지막 결과 폴더(예: 9) 복사
cp -r ../0 ./0_backup
cp -r ../9/* ./0/
```

### 3단계: 단상유동 시뮬레이션 실행

**직렬 실행:**
```bash
pimpleFoam
```

**병렬 실행 (예: 8 프로세스):**
```bash
decomposePar
mpirun -np 8 pimpleFoam -parallel
reconstructPar
```

### 4단계: 결과 확인
```bash
# ParaView에서 시각화
paraFoam
```

---

## 📊 sedFoam과의 비교

| 항목 | sedFoam | pimpleFoam (단상) |
|------|---------|------------------|
| 모델링 | 이상유동 (물+모래) | 단상 (물만) |
| 상 개수 | 2 (액체 + 고체) | 1 (액체) |
| 주요 변수 | U.a, U.b, alpha.a | U, p, k, epsilon |
| 난류 모델 | k-epsilon (유체상) | k-epsilon |
| 중력 영향 | 모래 침강 | 정수압 + 난류 |
| 응용 | 토사 이동 | 기본 유동역학 |

### 주요 예상 차이점
1. **침강 없음**: pimpleFoam은 입자가 없으므로 침강 현상 없음
2. **난류 특성**: 모래-물 상호작용이 없어서 다른 난류 특성
3. **점성 영향**: 물의 점성만 작용
4. **수치적 안정성**: pimpleFoam이 더 안정적 (간단한 모델)

---

## ⚙️ 설정 조정

### 난류 모델 변경
`constant/turbulenceProperties`에서:
```
RASModel        kEpsilon;  // k-epsilon
// 또는
RASModel        kOmegaSST; // k-omega SST
// 또는
RASModel        laminar;   // 층류
```

### 시뮬레이션 시간 변경
`system/controlDict`에서:
```
endTime         3600;  // 원하는 시간 (초)
deltaT          1e-6;  // 시간 스텝
```

### 쿠랑트 수 (Courant Number) 조정
```
maxCo           0.5;   // 0.3~1.0 범위
maxDeltaT       3e-3;  // 최대 시간 스텝
```

### 경계 조건 설정
기본적으로 모든 벽면은 `noSlip` 조건입니다.
필요시 `0/U`, `0/p` 등에서 경계 이름 조정 필요.

---

## 📈 결과 비교 및 분석

### 추출해야 할 데이터
1. **속도 프로필**: U 분포 시간 변화
2. **압력 필드**: p 분포
3. **난류 특성**: k, epsilon 값
4. **통계량**: 평균값, RMS, 표준편차

### Python 스크립트 예시
```python
import pandas as pd
from foamFileHandler import read_field_data

# 결과 읽기
u_pimple = read_field_data('singlePhase_case/postProcessing', 'U')
u_sedfoam = read_field_data('../postProcessing', 'U.b')

# 비교
comparison = pd.DataFrame({
    'pimpleFoam': u_pimple,
    'sedFoam': u_sedfoam
})
```

### ParaView 비교 가능 항목
- **Slice**: xy 평면에서 속도/압력 비교
- **Contour**: 난류 에너지 분포
- **Vector**: 속도장 벡터

---

## ⚠️ 주의사항

1. **메시 생성**: blockMeshDict는 기존 sedFoam과 동일하므로, 초기 경계층 설정이 sedFoam과 다를 수 있음
2. **경계 조건**: 메시의 경계명(inlet, outlet, etc.)을 0/ 폴더 파일과 일치시켜야 함
3. **초기 값**: k, epsilon의 초기값을 메시 크기와 유동 특성에 맞게 조정 권장
4. **수렴성**: pimpleFoam은 보통 sedFoam보다 수렴이 빠르지만, 초기값에 따라 달라짐

---

## 🔍 문제 해결

### 메시 생성 오류
```bash
# blockMeshDict 문법 확인
blockMesh -verbose
```

### 시뮬레이션 발산
- `maxCo` 값 감소 (0.3~0.4)
- `nOuterCorrectors` 증가 (5→7)
- `nNonOrthogonalCorrectors` 증가 (3→5)

### 메모리 부족
- 프로세스 수 감소
- `maxDeltaT` 증가 (더 큰 시간 스텝)
- 메시 셀 수 감소

---

## 📚 참고 자료

- OpenFOAM 공식 문서: https://www.openfoam.com/documentation
- sedFoam 논문 및 튜토리얼
- pimpleFoam 예제: `$FOAM_TUTORIALS/incompressible/pimpleFoam`

---

## 💡 팁

1. **처음 실행 시**: `writeInterval`을 크게 설정하여 디스크 공간 절약
2. **수렴 확인**: `log` 파일에서 residuals 추적
3. **비교 분석**: 최종 시점뿐 아니라 시간 경과에 따른 변화 추적
4. **재시작**: `startFrom latestTime`으로 계속 실행 가능

---

## 📧 문의

추가 정보나 문제 발생 시 문의 바랍니다.

Last Updated: 2024-12-19
