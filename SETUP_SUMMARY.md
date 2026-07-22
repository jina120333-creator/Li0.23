# 단상유동 케이스 구성 요약

## 📌 생성된 파일 목록

### 시스템 파일 (system/)

#### 1. **controlDict** - 시뮬레이션 시간 제어
```
- application: pimpleFoam
- endTime: 3600초 (sedFoam과 동일)
- deltaT: 1e-6초 (초기 시간 스텝)
- Courant 수: maxCo = 0.5
```

#### 2. **fvSolution** - 선형 솔버 및 PIMPLE 알고리즘
```
solvers:
  - p: GAMG (압력)
  - U: PBiCGStab (속도)
  - k, epsilon: smoothSolver (난류)
  
PIMPLE:
  - nOuterCorrectors: 5
  - nNonOrthogonalCorrectors: 3
```

#### 3. **fvSchemes** - 수치 스킴
```
- ddtSchemes: Euler (1차 시간 적분)
- gradSchemes: Gauss linear
- divSchemes: Gauss linearUpwind
- laplacianSchemes: Gauss linear corrected
```

#### 4. **blockMeshDict** - 메시 생성
```
복사됨: sedFoam의 메시와 동일
셀 수: 140 x 50 x 12 = 84,000 셀
```

#### 5. **decomposeParDict** - 병렬 계산 설정
```
복사됨: sedFoam 설정과 동일
```

---

### 상수 파일 (constant/)

#### 1. **transportProperties** - 유체 특성
```
transportModel: Newtonian
nu (동점성): 1.0e-6 m²/s  (물, 20°C)
rho (밀도): 1000 kg/m³
```

#### 2. **turbulenceProperties** - 난류 모델
```
simulation: RAS (Reynolds-Averaged)
RASModel: kEpsilon (기본값)
```

#### 3. **g** - 중력 가속도
```
value: (0 0 -9.81) m/s²
```

---

### 초기 조건 파일 (0/)

#### 1. **p** - 압력 필드
```
- 내부: 0 (Pa)
- 경계: zeroGradient 또는 fixedValue
```

#### 2. **U** - 속도 필드
```
- 내부: (0 0 0) (m/s) [유동 없을 때]
- 입구: fixedValue (0 0 0)
- 벽면: noSlip
```

#### 3. **k** - 난류 운동 에너지
```
- 내부: 0.00375 m²/s²
- 입구: fixedValue
- 벽면: kqRWallFunction
```

#### 4. **epsilon** - 난류 소산율
```
- 내부: 0.0104 m²/s³
- 입구: fixedValue
- 벽면: epsilonWallFunction
```

---

## 🔄 sedFoam vs pimpleFoam 파일 비교

| 항목 | sedFoam | pimpleFoam | 비고 |
|------|---------|-----------|------|
| 솔버 | sedFoam | pimpleFoam | 이상유동 vs 단상 |
| 필드 | U.a, U.b, alpha.a, Theta | U, p, k, epsilon | 입자 제거 |
| 특수 파일 | ppProperties, kineticTheoryProperties | 없음 | 단상이므로 불필요 |
| 난류 모델 | k-epsilon (유체상) | k-epsilon | 동일 |
| 메시 | 동일 | 동일 | blockMeshDict 복사 |
| 중력 | 포함 | 포함 | 동일 |

---

## 🚀 빠른 시작 가이드

### 1단계: 메시 생성
```bash
cd singlePhase_case
blockMesh
```

### 2단계: 실행
```bash
pimpleFoam > log &
# 또는 병렬
decomposePar
mpirun -np 8 pimpleFoam -parallel > log &
```

### 3단계: 결과 확인
```bash
paraFoam
# 또는
reconstructPar  # 병렬 실행 후
```

---

## 📊 주요 설정값 설명

### Courant 수
```
Co = (U * Δt) / Δx
maxCo = 0.5  → 안정적, 정확
maxCo = 1.0  → 빠르지만 덜 정확
```

### PIMPLE 매개변수
```
nOuterCorrectors = 5:
  - 압력-속도 커플링 반복 횟수
  - 값 증가 → 정확성 증가, 시간 증가

nNonOrthogonalCorrectors = 3:
  - 비직교성 보정 횟수
  - 메시 품질이 나쁠수록 증가 필요
```

### 완화 계수 (Relaxation Factors)
```
p: 0.3     → 느린 수렴, 안정성
U: 0.5     → 중간 수렴
k, epsilon: 0.7 → 빠른 수렴
```

---

## 🔍 커스터마이제이션

### 다른 난류 모델로 변경
**constant/turbulenceProperties 수정:**
```
RASModel        kOmegaSST;  // k-omega SST
// 또는
RASModel        laminar;    // 층류
```

### 입구 속도 설정
**0/U에서 inlet 경계 수정:**
```
inlet
{
    type            fixedValue;
    value           uniform (0.5 0 0);  // x 방향 0.5 m/s
}
```

### 시뮬레이션 시간 조정
**system/controlDict에서:**
```
endTime         1800;  // 30분 단축
deltaT          5e-6;  // 시간 스텝 증가 (빠름)
maxDeltaT       5e-3;  // 최대 시간 스텝
```

---

## ⚠️ 주의사항

1. **경계명 일치**: 0/ 파일의 경계명이 메시의 경계명과 정확히 일치해야 함
2. **초기값**: k, epsilon 초기값이 너무 작으면 난류 발달 지연
3. **수치 안정성**: 복잡한 메시는 더 작은 Courant 수 필요
4. **메모리**: 병렬 계산 시 프로세스 수에 따라 메모리 사용량 증가

---

## 📈 기대되는 결과

### sedFoam vs pimpleFoam 차이
1. **침강 효과 없음**: 모래가 없으므로 중력만 작용
2. **난류 특성 단순화**: 입자-유체 상호작용 없음
3. **수렴 속도 빠름**: 더 안정적인 수치 계산
4. **물리적 장점**: 단순한 유동역학 검증 가능

---

## 💾 파일 저장 구조

```
jina120333-creator-cuddly-carnival/
├── singlePhase_case/
│   ├── 0/
│   │   ├── p
│   │   ├── U
│   │   ├── k
│   │   └── epsilon
│   ├── constant/
│   │   ├── transportProperties
│   │   ├── turbulenceProperties
│   │   └── g
│   ├── system/
│   │   ├── controlDict
│   │   ├── fvSolution
│   │   ├── fvSchemes
│   │   ├── blockMeshDict (복사)
│   │   └── decomposeParDict (복사)
│   └── README.md
├── COMPARISON_GUIDE.md
└── [기존 sedFoam 케이스 파일들...]
```

---

## 📚 추가 학습 자료

- OpenFOAM pimpleFoam 튜토리얼
- CFD 수치 해석 기초
- 난류 모델링 입문
- 메시 생성 및 품질 관리

---

**생성 날짜**: 2024-12-19
**버전**: 1.0
**상태**: ✅ 준비 완료 (실행 대기 중)
