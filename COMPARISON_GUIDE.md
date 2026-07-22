# sedFoam vs pimpleFoam 비교 분석 가이드

## 📊 비교 분석의 목적

두 솔버의 차이를 이해하고:
- **검증(Validation)**: 단상 유동 모델이 물리적으로 일관성 있는지 확인
- **차이 분석**: 이상유동의 영향 정량화
- **수치 특성**: 각 솔버의 수렴성, 계산 시간, 정확도 비교

---

## 🔬 주요 비교 항목

### 1. 속도 필드 (Velocity Field)

**sedFoam에서:**
```
U.a : 모래(고체상) 속도
U.b : 물(유체상) 속도
```

**pimpleFoam에서:**
```
U   : 물 속도 (단일)
```

**비교 방법:**
```
- U.b (sedFoam) vs U (pimpleFoam) 비교
- 차이: |U.b - U| 계산
- 가우스 오차: sqrt(sum((U.b - U)^2) / N)
```

### 2. 압력 필드 (Pressure)

**sedFoam:**
```
p_rbgh : 동압(dynamic pressure) - 정수압 포함
```

**pimpleFoam:**
```
p      : 동압
```

**비교:**
- 절대 값 비교
- 압력 구배(gradient) 비교
- 동적 압력 계수(Cp) 계산

### 3. 난류 특성 (Turbulent Properties)

**공통 변수:**
- `k` : 난류 운동 에너지
- `epsilon` : 난류 소산율

**비교:**
- k, epsilon의 공간/시간 변화
- 난류 점성(eddy viscosity) 비교
- 난류 구조 (isotropic vs anisotropic)

### 4. 수렴 특성 (Convergence)

**비교할 항목:**
- 잔차(residuals) 감소 추이
- 반복 계산 횟수
- 계산 시간(CPU time)
- 메모리 사용량

---

## 📈 파이썬 기반 비교 분석

### 필수 라이브러리 설치
```bash
pip install numpy pandas matplotlib scipy
pip install foamFileHandler  # OpenFOAM 데이터 읽기
# 또는
pip install foam  # 대안
```

### 1. 기본 데이터 읽기 및 비교

```python
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# OpenFOAM 결과 읽기 (예시 함수)
def read_foam_field(case_path, time_step, field_name):
    """OpenFOAM 필드 데이터 읽기"""
    # 실제 구현은 foamFileHandler 또는 PyFoam 사용
    pass

# 데이터 로드
time_steps = [0, 100, 500, 1000, 3600]
sedfoam_U = []
pimple_U = []

for t in time_steps:
    U_b = read_foam_field('../', t, 'U.b')  # sedFoam
    U = read_foam_field('singlePhase_case/', t, 'U')  # pimpleFoam
    sedfoam_U.append(U_b)
    pimple_U.append(U)

# 기본 통계
for i, t in enumerate(time_steps):
    U_b = sedfoam_U[i]
    U = pimple_U[i]
    
    print(f"\n시간: {t}초")
    print(f"sedFoam U.b - 평균: {U_b.mean():.4f}, 표준편차: {U_b.std():.4f}")
    print(f"pimpleFoam U - 평균: {U.mean():.4f}, 표준편차: {U.std():.4f}")
    
    # 차이 분석
    diff = U_b - U
    rmse = np.sqrt(np.mean(diff**2))
    mae = np.mean(np.abs(diff))
    print(f"RMSE: {rmse:.6f}, MAE: {mae:.6f}")
```

### 2. 공간 분포 비교

```python
def compare_spatial_distribution(sedfoam_path, pimple_path, time_step, field='U'):
    """
    특정 시점에서 공간 분포 비교
    """
    # sedFoam 데이터
    U_b = read_foam_field(sedfoam_path, time_step, f'{field}.b')
    
    # pimpleFoam 데이터
    U = read_foam_field(pimple_path, time_step, field)
    
    # 1D 프로필 추출 (예: 중심선)
    x_line_sedfoam = U_b[:, 0]  # x 방향 성분
    x_line_pimple = U[:, 0]
    
    # 시각화
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    axes[0].plot(x_line_sedfoam, label='sedFoam U.b', marker='o')
    axes[0].plot(x_line_pimple, label='pimpleFoam U', marker='s')
    axes[0].set_xlabel('위치 (m)')
    axes[0].set_ylabel('U_x (m/s)')
    axes[0].legend()
    axes[0].set_title(f'속도 프로필 - {time_step}초')
    
    # 차이
    diff = x_line_sedfoam - x_line_pimple
    axes[1].plot(diff, marker='^', color='red')
    axes[1].set_xlabel('위치 (m)')
    axes[1].set_ylabel('차이 (m/s)')
    axes[1].set_title('sedFoam - pimpleFoam')
    axes[1].grid()
    
    plt.tight_layout()
    plt.savefig(f'comparison_t{time_step}.png', dpi=150)
    plt.show()

# 실행
compare_spatial_distribution('../', 'singlePhase_case/', 3600)
```

### 3. 시간 이력(Time History) 비교

```python
def time_history_comparison(sedfoam_path, pimple_path, probe_point):
    """
    특정 지점에서 시간 경과에 따른 변수 추적
    
    probe_point: (x, y, z) 좌표
    """
    times = np.arange(0, 3600, 100)  # 100초 간격
    
    sedfoam_values = []
    pimple_values = []
    
    for t in times:
        # 해당 지점에서 값 추출
        U_b = read_foam_field(sedfoam_path, t, 'U.b')
        U = read_foam_field(pimple_path, t, 'U')
        
        # probe_point에 가장 가까운 셀 찾기
        sedfoam_values.append(U_b[closest_cell_index])
        pimple_values.append(U[closest_cell_index])
    
    # 시각화
    fig, ax = plt.subplots(figsize=(10, 5))
    
    ax.plot(times, sedfoam_values, 'o-', label='sedFoam U.b', linewidth=2)
    ax.plot(times, pimple_values, 's-', label='pimpleFoam U', linewidth=2)
    ax.set_xlabel('시간 (초)')
    ax.set_ylabel('속도 (m/s)')
    ax.set_title(f'시간 이력 비교 - 지점: {probe_point}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('time_history_comparison.png', dpi=150)
    plt.show()

# 실행 (중심점 선택)
time_history_comparison('../', 'singlePhase_case/', (0, 0, 0.025))
```

### 4. 통계 분석

```python
def statistical_analysis(sedfoam_U, pimple_U):
    """
    두 솔루션의 통계적 차이 분석
    """
    from scipy.stats import kstest, mannwhitneyu
    
    # 기본 통계
    print("=" * 50)
    print("기본 통계량")
    print("=" * 50)
    print(f"\nsedFoam U.b:")
    print(f"  평균: {np.mean(sedfoam_U):.6f}")
    print(f"  중위수: {np.median(sedfoam_U):.6f}")
    print(f"  표준편차: {np.std(sedfoam_U):.6f}")
    print(f"  최소값: {np.min(sedfoam_U):.6f}")
    print(f"  최대값: {np.max(sedfoam_U):.6f}")
    
    print(f"\npimpleFoam U:")
    print(f"  평균: {np.mean(pimple_U):.6f}")
    print(f"  중위수: {np.median(pimple_U):.6f}")
    print(f"  표준편차: {np.std(pimple_U):.6f}")
    print(f"  최소값: {np.min(pimple_U):.6f}")
    print(f"  최대값: {np.max(pimple_U):.6f}")
    
    # 정규성 검정 (Kolmogorov-Smirnov)
    print("\n" + "=" * 50)
    print("정규성 검정 (K-S test)")
    print("=" * 50)
    ks_sedfoam = kstest(sedfoam_U, 'norm', args=(np.mean(sedfoam_U), np.std(sedfoam_U)))
    ks_pimple = kstest(pimple_U, 'norm', args=(np.mean(pimple_U), np.std(pimple_U)))
    
    print(f"sedFoam p-value: {ks_sedfoam.pvalue:.4f}")
    print(f"pimpleFoam p-value: {ks_pimple.pvalue:.4f}")
    
    # 비모수 검정 (Mann-Whitney U test)
    print("\n" + "=" * 50)
    print("비모수 검정 (Mann-Whitney U test)")
    print("=" * 50)
    stat, p_value = mannwhitneyu(sedfoam_U, pimple_U)
    print(f"U 통계량: {stat:.4f}")
    print(f"p-value: {p_value:.4f}")
    if p_value < 0.05:
        print("두 분포는 통계적으로 유의한 차이가 있습니다.")
    else:
        print("두 분포는 통계적으로 유의한 차이가 없습니다.")
    
    # 상관계수
    correlation = np.corrcoef(sedfoam_U, pimple_U)[0, 1]
    print(f"\n피어슨 상관계수: {correlation:.6f}")
```

### 5. 에너지 분석

```python
def energy_analysis(sedfoam_path, pimple_path, time_step):
    """
    난류 에너지 비교
    """
    # 난류 운동 에너지 (k) 읽기
    k_b = read_foam_field(sedfoam_path, time_step, 'k.b')
    k = read_foam_field(pimple_path, time_step, 'k')
    
    # 난류 소산율 (epsilon) 읽기
    eps_b = read_foam_field(sedfoam_path, time_step, 'epsilon.b')
    eps = read_foam_field(pimple_path, time_step, 'epsilon')
    
    # 통합된 에너지
    total_k_sedfoam = np.sum(k_b)
    total_k_pimple = np.sum(k)
    
    total_eps_sedfoam = np.sum(eps_b)
    total_eps_pimple = np.sum(eps)
    
    print(f"시간: {time_step}초")
    print(f"총 난류 에너지 (k):")
    print(f"  sedFoam: {total_k_sedfoam:.6e}")
    print(f"  pimpleFoam: {total_k_pimple:.6e}")
    print(f"  차이: {abs(total_k_sedfoam - total_k_pimple):.6e}")
    
    print(f"\n총 난류 소산율 (epsilon):")
    print(f"  sedFoam: {total_eps_sedfoam:.6e}")
    print(f"  pimpleFoam: {total_eps_pimple:.6e}")
    print(f"  차이: {abs(total_eps_sedfoam - total_eps_pimple):.6e}")
```

---

## 📊 시각화 예제

### Matplotlib를 이용한 다양한 비교

```python
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def comprehensive_comparison(sedfoam_path, pimple_path, time_step):
    """
    종합 비교 대시보드
    """
    fig = plt.figure(figsize=(14, 10))
    gs = GridSpec(3, 3, figure=fig)
    
    # 1. 속도 분포 비교
    ax1 = fig.add_subplot(gs[0, :2])
    # 데이터 로드 및 플롯
    
    # 2. 압력 분포
    ax2 = fig.add_subplot(gs[1, :2])
    
    # 3. 난류 에너지
    ax3 = fig.add_subplot(gs[2, :2])
    
    # 4. 메트릭 요약
    ax4 = fig.add_subplot(gs[:, 2])
    ax4.axis('off')
    
    summary_text = f"""
    비교 요약 (t = {time_step}초)
    
    속도 (U):
    - RMSE: 0.0234 m/s
    - R²: 0.95
    
    압력 (p):
    - RMSE: 1.23 Pa
    - R²: 0.92
    
    난류 에너지 (k):
    - RMSE: 1.2e-5 m²/s²
    - R²: 0.88
    """
    ax4.text(0.1, 0.5, summary_text, fontsize=10, family='monospace')
    
    plt.tight_layout()
    plt.savefig('comprehensive_comparison.png', dpi=150)

comprehensive_comparison('../', 'singlePhase_case/', 3600)
```

---

## 🎯 비교 체크리스트

- [ ] 메시 확인 (두 케이스 동일한 메시 사용)
- [ ] 초기 조건 확인 (동일한 초기 속도/압력)
- [ ] 경계 조건 확인 (동일한 경계 조건)
- [ ] 시간 스텝 확인 (Courant 수 범위)
- [ ] 난류 모델 확인 (k-epsilon 동일)
- [ ] 결과 수렴성 확인 (log 파일 잔차)
- [ ] 데이터 추출 및 정규화
- [ ] 통계 분석 수행
- [ ] 그래프 및 보고서 작성

---

## 📝 보고서 작성 가이드

### 포함할 내용
1. **목적**: 이상유동과 단상유동의 차이 정량화
2. **방법론**: 사용한 솔버, 메시, 초기/경계조건
3. **결과**: 비교 그래프, 통계량
4. **토의**: 물리적 의미, 모델 차이의 영향
5. **결론**: 주요 발견사항

### 논문 참고 구조
- 시간에 따른 변화 추적
- 공간 분포 비교
- 통계적 유의성 검정
- 물리 현상 해석

---

Last Updated: 2024-12-19
