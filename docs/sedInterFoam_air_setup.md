# sedInterFoam 전환: 공기층 및 경계조건 설정 노트

기존 sedFoam(rigid-lid) 케이스를 sedInterFoam(모래 + 물 + 공기, VOF)으로 전환하기 위한
격자/경계조건 설계 근거를 정리한다.

## 1. 공기층 높이: 0.03 m (z = 0.05 → 0.08)

| 항목 | 값 |
|---|---|
| 수심 h | 0.05 m |
| 유입 유속 U₀ (로그법칙, u* = 0.01617) | ≈ 0.23 m/s |
| Froude 수 Fr = U₀/√(gh) | ≈ 0.33 (상류류) |
| 교각 전면 정체 수위 상승 U₀²/2g | ≈ 2.8 mm |

- 이 케이스는 Fr ≈ 0.33의 상류류이므로 자유수면 변동은 교각 전면 상승 + 후류 함몰을
  합쳐도 **수 mm 수준**이다.
- 공기층 0.03 m는 예상 수면 변동의 약 10배 여유이며, 수심의 0.6배로
  interFoam 계열 개수로 케이스에서 통용되는 0.5h–1.0h 범위에 든다.
- 공기층을 더 높이면 (예: 0.05 m) 셀 수만 늘고 결과에 거의 영향이 없다.
  쇄파나 큰 run-up이 없는 세굴 문제에서는 0.03 m로 충분하다.

## 2. z 방향 격자 설계

| 블록 | z 범위 | 셀 수 | grading | 비고 |
|---|---|---|---|---|
| 모래 | -0.06 ~ 0.00 | 12 | 0.2 | 하상면(z=0)에서 dz ≈ 2 mm |
| 물 | 0.00 ~ 0.05 | 16 | ((0.5 0.5 4) (0.5 0.5 0.25)) | 양 끝단 미세화: 바닥 dz ≈ 1.4 mm, 수면 dz ≈ 1.4 mm |
| 공기 | 0.05 ~ 0.08 | 8 | 4 | 계면에서 dz ≈ 1.7 mm, 상단으로 갈수록 성김 |

핵심: **기존 물 블록의 grading 5 (수면 쪽이 가장 성김)는 VOF에 부적합**하다.
VOF 계면(z = 0.05)이 가장 굵은 셀에 놓이면 계면이 뭉개진다. 새 격자는
계면 상하로 dz ≈ 1.4–1.7 mm의 준균일 셀 밴드를 두어 계면을 선명하게 잡는다.

snappyHexMeshDict 변경 사항:
- 교각 실린더 point2: z = 0.051 → **0.081** (수면 관통 교각이 새 도메인 상단을 넘도록)
- nearPierFineBox 상단: z = 0.050 → **0.060** (교각 주위 bow wave / run-up 해상)

## 3. 경계조건 권장 설정 (sedInterFoam)

패치 구성: `inletSediment`, `inletWater`, `inletAir`, `outletSediment`,
`outletWater`, `outletAir`, `sideWalls`(wall), `bottom`(wall), `top`(patch, 대기).

압력 기준은 **top(대기)의 totalPressure p0 = 0**이 잡아준다. 따라서 기존
sedFoam 설정처럼 outlet에 p_rbgh fixedValue 0을 주면 **안 된다**
(VOF에서는 물 영역의 p_rbgh ≈ ρ_w·g·h_still ≈ 490 Pa ≠ 0이므로 수면을 강제로 왜곡한다).

### top (대기 개방면)

```
U.b         pressureInletOutletVelocity; value uniform (0 0 0);
p_rbgh      totalPressure; p0 uniform 0;
alpha.water inletOutlet; inletValue uniform 0;
alpha.a     zeroGradient;
U.a         fixedValue uniform (0 0 0);
k.b         inletOutlet; inletValue uniform <작은값>;
epsilon.b   inletOutlet; inletValue uniform <작은값>;
Theta, pa   zeroGradient;
```

### inletAir (x = -0.8, z = 0.05~0.08)

공기 유입을 따로 강제할 필요가 없으므로 top과 동일하게 "준대기(open)"로 처리하는
것이 가장 안정적이다:

```
U.b         pressureInletOutletVelocity; value uniform (0 0 0);
p_rbgh      totalPressure; p0 uniform 0;
alpha.water inletOutlet; inletValue uniform 0;
alpha.a     fixedValue uniform 0;
```

### inletWater (x = -0.8, z = 0~0.05)

```
U.b         codedFixedValue (기존 로그법칙 유지, z=0~0.05만 적용되므로 수정 불필요)
p_rbgh      fixedFluxPressure; value uniform 0;
alpha.water fixedValue uniform 1;
alpha.a     fixedValue uniform 0;   // (기존과 동일)
k.b, eps.b  기존 값 유지
```

### inletSediment (x = -0.8, z = -0.06~0)

```
U.a, U.b    fixedValue uniform (0 0 0);   // 기존 유지
p_rbgh      fixedFluxPressure; value uniform 0;
alpha.water fixedValue uniform 1;         // 공극수는 물
alpha.a     zeroGradient;                 // 기존 유지
```

### outletWater / outletSediment (x = 0.6)

```
U.b         inletOutlet; inletValue uniform (0 0 0);  // 역류 방지형 zeroGradient
U.a         기존 유지 (outletWater: zeroGradient, outletSediment: fixedValue 0)
p_rbgh      zeroGradient;        // fixedValue 0 금지! (위 설명 참조)
alpha.water zeroGradient;
alpha.a     zeroGradient;
```

### outletAir (x = 0.6, z = 0.05~0.08)

```
U.b         pressureInletOutletVelocity; value uniform (0 0 0);
p_rbgh      totalPressure; p0 uniform 0;
alpha.water inletOutlet; inletValue uniform 0;
alpha.a     fixedValue uniform 0;
```

### sideWalls / bottom

기존 설정 유지 (U noSlip, p_rbgh fixedFluxPressure, alpha zeroGradient).
`alpha.water`는 zeroGradient 추가.

## 4. 초기조건 (setFieldsDict)

`alpha.water` 필드를 추가하고 다음을 설정:

```
defaultFieldValues
(
    volScalarFieldValue alpha.a     0
    volScalarFieldValue alpha.water 0     // 기본: 공기
);

regions
(
    boxToCell   // 모래층
    {
        box (-0.81 -0.1251 -0.061) (0.61 0.1251 0.0);
        fieldValues ( volScalarFieldValue alpha.a 0.58
                      volScalarFieldValue alpha.water 1 );
    }
    boxToCell   // 물층
    {
        box (-0.81 -0.1251 0.0) (0.61 0.1251 0.05);
        fieldValues ( volScalarFieldValue alpha.water 1 );
    }
);
```

## 5. 주의사항

- **outlet 수위 드리프트**: 위 outlet 설정(zeroGradient 계열)은 수위를 고정하지
  않으므로, 장시간(300 s) 계산에서 도메인 내 수위가 서서히 표류할 수 있다.
  수위 유지가 필요하면 outletWater의 U.b에 `outletPhaseMeanVelocity`
  (Umean = 유입 평균유속, alpha = alpha.water)를 적용하는 것을 검토.
- **maxAlphaCo**: VOF 계면 Courant 수 제한이 실제로 작동하게 되므로
  (rigid-lid에서는 무의미했음) controlDict의 `maxAlphaCo 0.5`는 그대로 두되,
  초기 과도기에는 0.3 정도로 낮추는 것이 안전.
- 배경격자 셀 수: 140×25×36 = 126,000 (기존 84,000 대비 +50%, snappy 이전 기준).
