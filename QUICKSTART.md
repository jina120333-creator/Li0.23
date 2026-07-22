# 🚀 단상유동 케이스 - 빠른 시작 가이드

## ✅ 설치 완료 확인 사항

### 생성된 파일 확인
```bash
cd singlePhase_case/
ls -la           # 디렉토리 구조 확인
ls 0/            # 초기 조건 (p, U, k, epsilon)
ls constant/     # 상수 파일 (3개)
ls system/       # 시스템 설정 (5개 파일)
```

### 필수 파일 체크리스트
- [ ] `0/p` - 압력 필드
- [ ] `0/U` - 속도 필드
- [ ] `0/k` - 난류 에너지
- [ ] `0/epsilon` - 난류 소산율
- [ ] `constant/transportProperties` - 유체 특성
- [ ] `constant/turbulenceProperties` - 난류 모델
- [ ] `constant/g` - 중력
- [ ] `system/controlDict` - 시간 제어
- [ ] `system/fvSolution` - 솔버 설정
- [ ] `system/fvSchemes` - 스킴
- [ ] `system/blockMeshDict` - 메시

---

## 🎯 단계별 실행 절차

### 1️⃣ 메시 생성 (필수) - Pier 구조 포함

**중요**: Pier 구조를 생성하려면 blockMesh + snappyHexMesh 두 단계 필요!

```bash
cd singlePhase_case/

# 1단계: 기본 육면체 메시
blockMesh
# 출력: "Mesh Bounding Box... Mesh stats..."

# 2단계: Pier 구조 및 세밀 정제 (반드시 필요!)
snappyHexMesh -overwrite
# 출력: "Creating mesh from mesh.1..."

# 검증 (선택사항)
checkMesh
```

**상세 설명**: `MESH_GENERATION.md` 참고

### 2️⃣ 시뮬레이션 실행

#### A. 직렬 실행 (단일 프로세스)
```bash
pimpleFoam | tee log
# 또는 백그라운드
nohup pimpleFoam > log 2>&1 &
```

#### B. 병렬 실행 (권장)
```bash
# 메시 분해
decomposePar

# 병렬 실행 (8 프로세스)
mpirun -np 8 pimpleFoam -parallel | tee log

# 결과 재조합
reconstructPar
```

### 3️⃣ 결과 확인
```bash
# ParaView 시각화
paraFoam

# 또는 수동으로 결과 파일 확인
ls -la 0/
ls -la 100/   # 시간 폴더
ls -la 1000/
```

### 4️⃣ 로그 확인 (수렴 확인)
```bash
# 마지막 100줄 보기
tail -100 log

# 잔차 확인
grep "^p_rgh" log | head -20
grep "^U" log | head -20
```

---

## 📊 주요 명령어

### 메시 관련
```bash
blockMesh                    # 메시 생성
blockMesh -verbose          # 상세 정보
checkMesh                    # 메시 품질 확인
decomposePar                 # 병렬 분해
reconstructPar              # 결과 병합
```

### 시뮬레이션
```bash
pimpleFoam                   # 실행
pimpleFoam -help            # 도움말
pimpleFoam > log &          # 백그라운드 실행
```

### 후처리
```bash
paraFoam                     # 시각화 (GUI)
foamToVTK                    # VTK 변환
foamPostDict                 # 딕셔너리 확인
```

---

## ⚙️ 설정 조정 (필요시)

### 시뮬레이션 시간 단축 (테스트용)
**파일**: `system/controlDict`
```diff
- endTime         3600;      # 3600초
+ endTime         60;        # 60초로 단축
```

### 더 빠른 수렴 (계산 속도 중시)
**파일**: `system/controlDict`
```diff
- maxCo           0.5;
+ maxCo           1.0;       # 빠름 (덜 정확함)
```

### 더 정확한 결과 (안정성 중시)
**파일**: `system/fvSolution`
```diff
- nOuterCorrectors   5;
+ nOuterCorrectors   10;     # 더 느리지만 정확함
```

### 다른 난류 모델 시도
**파일**: `constant/turbulenceProperties`
```diff
- RASModel        kEpsilon;
+ RASModel        kOmegaSST;  # 또는 laminar
```

---

## 🔍 문제 해결

### 1️⃣ "경계 이름 오류" (boundary not found)
**증상**: `FatalIOError in boundary conditions`
**해결**:
```bash
# 메시의 실제 경계명 확인
checkMesh | grep "Boundary"

# 0/ 폴더의 경계명과 일치시키기
# 예: blockMesh에서 "walls" → 0/U에서 walls {} 추가
```

### 2️⃣ 계산이 발산함 (NaN 에러)
**증상**: `FATAL ERROR: Request for coefficient ... failed`
**해결**:
```bash
# 1. Courant 수 감소
sed -i 's/maxCo           0.5;/maxCo           0.3;/' system/controlDict

# 2. 완화 계수 조정 (fvSolution)
#    p: 0.3 → 0.2
#    U: 0.5 → 0.3

# 3. 초기 조건 확인
#    0/k, 0/epsilon 값이 너무 작거나 크면 문제
```

### 3️⃣ 메모리 부족
**증상**: `Error: memory allocation failed`
**해결**:
```bash
# 병렬 프로세스 수 감소
decomposePar -n 4   # 4개로 감소

# 또는 메시 크기 감소 (blockMeshDict에서)
```

### 4️⃣ 메시 생성 오류
**증상**: `blockMesh` 실행 오류
**해결**:
```bash
# blockMeshDict 문법 확인
blockMesh -verbose

# 또는 기존 케이스에서 복사 확인
diff system/blockMeshDict ../system/blockMeshDict
```

---

## 📈 비교 분석 준비

### 결과 추출
```bash
# 특정 시간의 데이터만 추출
cp -r 1000 results_1000/

# 또는 모든 시간 폴더 백업
tar -czf results_all.tar.gz [0-9]*/
```

### Python 분석 도구
```bash
# 비교 스크립트 실행
python3 compare_foams.py --summary

# 보고서 템플릿 생성
python3 compare_foams.py --report my_report.txt

# sedFoam과 비교
python3 compare_foams.py --sedfoam_path ../ --pimple_path ./singlePhase_case/
```

---

## 💡 팁과 트릭

### 1. 계산 상태 실시간 확인
```bash
tail -f log | grep -E "^(Time|ClockTime|ExecutionTime|p_rgh|U)"
```

### 2. 계산 중 ParaView 열기
```bash
# 새로운 터미널에서 (계산 중)
paraFoam
```

### 3. 계산 일시 중지 및 재개
```bash
# ControlDict에서:
# startFrom latestTime;  # 마지막 결과부터 재개

# 파일 수정 후
pimpleFoam
```

### 4. 병렬 계산 최적 프로세스 수
```bash
# CPU 코어 수 확인 (Linux)
nproc
# 또는 프로세서 수만큼 사용
mpirun -np $(nproc) pimpleFoam -parallel
```

### 5. 결과 데이터 크기 확인
```bash
# 전체 크기
du -sh .

# 시간별 크기
du -sh */ | sort -h
```

---

## 📚 참고 문서

| 파일명 | 내용 | 용도 |
|--------|------|------|
| `README.md` | 상세 설명 및 설정 가이드 | 처음 설정할 때 |
| `SETUP_SUMMARY.md` | 파일 구조 및 설정값 설명 | 파일 수정 시 |
| `COMPARISON_GUIDE.md` | 비교 분석 방법 및 Python 스크립트 | 결과 분석 시 |
| `compare_foams.py` | 비교 분석 자동화 도구 | 후처리 자동화 |

---

## 🎓 학습 경로

1. **첫 실행**
   - 메시 생성 → 단시간 시뮬 (60초) → 결과 확인

2. **설정 이해**
   - fvSolution의 solvers 이해
   - controlDict의 시간 제어 학습
   - 경계 조건 수정 연습

3. **고급 사용**
   - 난류 모델 변경
   - 메시 조정
   - 병렬 계산 최적화

4. **분석 스킬**
   - ParaView 시각화
   - 데이터 추출 및 처리
   - 결과 비교 분석

---

## 🚨 주의사항

⚠️ **절대 하지 말 것**:
- [ ] 시뮬레이션 중 0/ 폴더 수정 금지
- [ ] blockMeshDict 수정 후 메시 재생성 필수
- [ ] 경계명 임의로 변경 금지 (메시와 불일치)
- [ ] 직렬 실행 중 decomposePar 실행 금지

✅ **필수 확인**:
- [ ] 메시 생성 완료 확인
- [ ] 경계명 일치 확인
- [ ] 초기값 범위 확인
- [ ] 로그 파일에서 수렴 확인

---

## 📞 추가 도움

### 자주 묻는 질문 (FAQ)

**Q: 얼마나 오래 걸리나요?**
- A: 메시 크기, CPU 수에 따라 다름. 예상: 1~10시간

**Q: 메모리는 얼마나 필요한가요?**
- A: 병렬 계산 시 84,000 셀 기준 약 2-4GB/프로세스

**Q: pimpleFoam 대신 다른 솔버를 사용할 수 있나요?**
- A: 네. simpleFoam (정상상태), icoFoam (비압축성) 등 가능

**Q: sedFoam 9초 결과를 초기값으로 쓸 수 있나요?**
- A: 네. U.b를 U로, p_rbgh를 p로 변환 필요

**Q: 계산 시간을 줄이려면?**
- A: maxCo 증가, nOuterCorrectors 감소, 메시 축소 등

---

**마지막 업데이트**: 2024-12-19  
**상태**: ✅ 준비 완료 - 실행 가능
**다음 단계**: `blockMesh` 실행 후 `pimpleFoam` 시작
