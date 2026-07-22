# 📋 메시 생성 가이드 (Mesh Generation Guide)

## 중요! Pier 구조 생성을 위한 완전한 메시 생성 절차

단상유동 케이스에서 **pier(기둥) 구조**를 포함한 완전한 메시를 생성하려면 다음 두 단계가 필요합니다.

---

## 🔧 메시 생성 프로세스

### 1단계: blockMesh - 기본 육면체 메시 생성

```bash
cd singlePhase_case/
blockMesh
```

**결과:**
- 기본 배경 메시 생성
- 약 84,000개 셀 생성

---

### 2단계: snappyHexMesh - Pier 구조 및 국소 정제

```bash
snappyHexMesh -overwrite
```

**주요 작업:**
1. **Castellated Mesh**: Pier 기하학 표현 (원형 실린더)
   - Pier 반경: 0.02 m (직경 0.04 m)
   - Pier 높이: -0.061 ~ 0.051 m
   
2. **Snap**: 메시 표면을 Pier 기하학에 정렬
   
3. **Add Layers**: 벽면 경계층 메시 추가

**refinement 영역:**
- **nearPierFineBox**: Pier 주변 세밀 정제 (레벨 2)
  - Horseshoe vortex 및 near-bed 흐름 포착
  
- **scourBedFineBox**: 침식 예상 영역 세밀 정제
  - 침식 홀 발달 추적용

**결과:**
- Pier 구조 포함 최종 메시
- 총 셀 수: ~200,000 ~ 300,000 (정제 정도에 따라)

---

## ⚡ 빠른 메시 생성 (한 번에)

```bash
cd singlePhase_case/

# 블록 메시 생성
blockMesh

# snappyHexMesh 실행 (기존 메시 덮어쓰기)
snappyHexMesh -overwrite

# 검증 (선택사항)
checkMesh

# 메시 정보 확인
checkMesh -allGeometry
```

---

## 🔍 메시 품질 확인

```bash
# 메시 통계 정보
checkMesh

# 출력 확인 항목:
# - Non-orthogonal faces
# - Boundary layer quality
# - Cell aspect ratio
```

**정상 범위:**
- Non-orthogonal faces: < 5%
- Skewness: < 0.8
- Aspect ratio: < 1000 (벽면 근처는 높음)

---

## 🛠️ snappyHexMeshDict 설정값 설명

### 기하학 정의 (geometry)

```
pier:
  type searchableCylinder
  point1 (0 0 -0.061)    # 실린더 하단 (domain 아래)
  point2 (0 0  0.051)    # 실린더 상단 (domain 위)
  radius 0.02            # 반경 = 0.02 m (직경 0.04 m)
```

### 정제 영역 (refinementRegions)

```
nearPierFineBox:
  min (-0.06 -0.05 -0.015)   # Pier 주변 상자 범위
  max ( 0.06  0.05  0.050)
  refinement level: 2         # 메시 크기 1/4로 정제

scourBedFineBox:
  min (-0.10 -0.060 -0.025)   # 침식 영역 범위
  max ( 0.14  0.060  0.020)
  refinement level: 2         # 메시 크기 1/4로 정제
```

### 중요 파라미터

```
nCellsBetweenLevels: 5
  → 정제 레벨 간 최소 셀 개수 (안정성)

resolveFeatureAngle: 30
  → 특성 모서리 감지 각도

locationInMesh (-0.395 0.00 0.025)
  → 유동 계산 영역의 한 점 (pier 외부!!)
```

---

## 📊 Pier 매개변수 커스터마이징

### Pier 크기 변경 (예: D = 0.06 m)

**파일**: `system/snappyHexMeshDict`
```diff
  pier
  {
      type searchableCylinder;
-     radius 0.02;     // D = 0.04 m
+     radius 0.03;     // D = 0.06 m
  }
```

### Pier 위치 변경 (예: x = 0.1m로 이동)

```diff
  nearPierFineBox
  {
      type searchableBox;
-     min (-0.06 -0.05 -0.015);
+     min ( 0.04 -0.05 -0.015);  // 중심이 0.1으로 이동
-     max ( 0.06  0.05  0.050);
+     max ( 0.16  0.05  0.050);
  }
  
  locationInMesh (-0.395 0.00 0.025)
  → locationInMesh (-0.395 0.00 0.025)  // 여전히 pier 외부여야 함!
```

### 정제 레벨 증가 (더 세밀한 메시)

```diff
  pier
  {
      type searchableCylinder;
-     level (1 2);    # 현재 (크기 1/2, 1/4)
+     level (2 3);    # 더 세밀 (크기 1/4, 1/8)
  }
```

**주의**: 레벨 증가 → 셀 수 4배 증가 → 계산 시간 급증

---

## 🚨 자주 만나는 문제

### 1️⃣ "locationInMesh 점이 pier 내부에 있음" 오류

**원인**: `locationInMesh`가 pier 실린더 내부에 있음

**해결**:
```
# 현재 설정:
locationInMesh (-0.395 0.00 0.025)
              ↑ x = -0.395 (pier의 좌측, pier 중심은 x=0)
              
# Pier 반경이 0.02m이므로 안전함. OK!
```

### 2️⃣ snappyHexMesh 실행 후 메시가 없음

**원인**: `-overwrite` 옵션 빠뜨림

**해결**:
```bash
snappyHexMesh -overwrite
```

### 3️⃣ 메시 생성 너무 느림

**원인**: 정제 레벨이 너무 높거나 셀 수 많음

**해결**:
```diff
  refinementSurfaces
  {
      pier
      {
-         level (2 3);
+         level (1 2);    # 레벨 낮춤
      }
  }
```

### 4️⃣ 메시 품질 나쁨 (Non-orthogonal 많음)

**원인**: addLayers가 너무 많은 레이어 생성

**해결**:
```diff
- addLayers       true;
+ addLayers       false;   # 벽면 레이어 비활성화 (빠름, 덜 정확함)
```

---

## 📈 메시 크기 추정

| 설정 | 예상 셀 수 | 계산 시간 (1 CPU) | 디스크 |
|------|-----------|------------------|--------|
| blockMesh만 | ~84,000 | 수 시간 | ~50 MB |
| + snappyHex (level 1) | ~150,000 | 10~20시간 | ~100 MB |
| + snappyHex (level 2) | ~300,000 | 30~50시간 | ~200 MB |
| + addLayers ON | +50% | +30% | +30% |

---

## ✅ 메시 생성 체크리스트

- [ ] `blockMesh` 실행 성공
- [ ] `snappyHexMesh -overwrite` 실행 성공
- [ ] `checkMesh` 오류 없음
- [ ] `poly/` 폴더에 파일 생성됨
  - `boundary`
  - `faces`
  - `neighbour`
  - `owner`
  - `points`
- [ ] ParaView에서 pier 구조 시각 확인

---

## 🎯 권장 메시 생성 절차

### 테스트용 (빠름)
```bash
# 1. blockMesh만 사용
blockMesh

# 2. 간단한 snappyHex (레벨 1)
# snappyHexMeshDict에서:
#   level (1 2);
#   addLayers false;
snappyHexMesh -overwrite
```

### 최종 정확 시뮬레이션용
```bash
blockMesh

# snappyHexMeshDict에서:
#   level (2 3);
#   addLayers true;
snappyHexMesh -overwrite
```

---

## 📚 참고

- **blockMeshDict**: 배경 메시 (육면체) 생성
- **snappyHexMeshDict**: pier 구조 및 세밀 정제
- 두 파일 모두 필수: pier 구조 생성을 위해

---

**마지막 업데이트**: 2024-12-19
**상태**: ✅ 필수 가이드
