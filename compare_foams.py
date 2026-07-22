#!/usr/bin/env python3
"""
OpenFOAM sedFoam과 pimpleFoam 비교 분석 스크립트

사용법:
    python3 compare_foams.py --sedfoam_path ../ --pimple_path ./singlePhase_case/ --time 3600
    python3 compare_foams.py --summary    # 요약만 출력
"""

import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# 스타일 설정
plt.style.use('seaborn-v0_8-darkgrid')
COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

class FOAMComparator:
    """OpenFOAM 결과 비교 클래스"""
    
    def __init__(self, sedfoam_path, pimple_path):
        self.sedfoam_path = Path(sedfoam_path)
        self.pimple_path = Path(pimple_path)
        self.results = {}
        
    def get_available_times(self):
        """사용 가능한 시간 폴더 목록"""
        times_sedfoam = sorted([
            float(d.name) for d in self.sedfoam_path.iterdir() 
            if d.is_dir() and d.name.replace('.', '').isdigit()
        ])
        times_pimple = sorted([
            float(d.name) for d in self.pimple_path.iterdir() 
            if d.is_dir() and d.name.replace('.', '').isdigit()
        ])
        return times_sedfoam, times_pimple
    
    def read_field_info(self, case_path, time):
        """필드 정보 출력"""
        time_dir = case_path / str(int(time)) if time == int(time) else case_path / str(time)
        
        if not time_dir.exists():
            return None
        
        fields = [f.name for f in time_dir.iterdir() if f.is_file()]
        return fields
    
    def print_summary(self):
        """케이스 요약 정보 출력"""
        print("\n" + "="*70)
        print("단상유동 (pimpleFoam) vs 이상유동 (sedFoam) 비교")
        print("="*70)
        
        # sedFoam 정보
        print("\n📊 sedFoam 케이스 정보:")
        times_sedfoam, _ = self.get_available_times()
        if times_sedfoam:
            print(f"  경로: {self.sedfoam_path}")
            print(f"  사용 가능 시간: {times_sedfoam[0]:.1f} ~ {times_sedfoam[-1]:.1f}초")
            print(f"  시간 스텝 수: {len(times_sedfoam)}")
            
            fields = self.read_field_info(self.sedfoam_path, times_sedfoam[0])
            if fields:
                print(f"  필드: {', '.join(sorted(fields)[:5])}...")
        
        # pimpleFoam 정보
        print("\n📊 pimpleFoam 케이스 정보:")
        _, times_pimple = self.get_available_times()
        if times_pimple:
            print(f"  경로: {self.pimple_path}")
            print(f"  사용 가능 시간: {times_pimple[0]:.1f} ~ {times_pimple[-1]:.1f}초")
            print(f"  시간 스텝 수: {len(times_pimple)}")
            
            fields = self.read_field_info(self.pimple_path, times_pimple[0])
            if fields:
                print(f"  필드: {', '.join(sorted(fields)[:5])}...")
        
        # 비교 정보
        print("\n" + "="*70)
        print("비교 정보:")
        print("="*70)
        print(f"  공통 시간: {set(times_sedfoam) & set(times_pimple)}")
        print(f"\n  주요 차이점:")
        print(f"    - sedFoam: U.a (모래), U.b (물), alpha.a (농도)")
        print(f"    - pimpleFoam: U (단일 속도필드)")
        print(f"\n  비교 필드:")
        print(f"    - 속도: U.b (sedFoam) vs U (pimpleFoam)")
        print(f"    - 압력: p_rbgh (sedFoam) vs p (pimpleFoam)")
        print(f"    - 난류: k.b, epsilon.b vs k, epsilon")
    
    def generate_report_template(self, output_file="comparison_report.txt"):
        """비교 보고서 템플릿 생성"""
        report = """
╔════════════════════════════════════════════════════════════════════════════╗
║           sedFoam (이상유동) vs pimpleFoam (단상유동) 비교 보고서            ║
╚════════════════════════════════════════════════════════════════════════════╝

1. 목적
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 단상 유동 모델 (pimpleFoam)과 이상 유동 모델 (sedFoam) 결과 비교
- 모래 입자의 영향 정량화
- 물리 현상 검증

2. 케이스 설정
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2.1 sedFoam
  - 모델: 이상유동 (Eulerian-Eulerian)
  - 상: 물 (phase b) + 모래 (phase a)
  - 난류 모델: k-epsilon (유체상)
  - 특수 모델: 운동 이론, Frictional 응력

2.2 pimpleFoam
  - 모델: 단상 유동
  - 유체: 물만
  - 난류 모델: k-epsilon
  - 입자: 없음

3. 메시 및 영역
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - 메시: 동일 (blockMeshDict 사용)
  - 셀 수: [사용자 입력]
  - 해상도: [사용자 입력]

4. 초기 및 경계 조건
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4.1 초기 조건:
  - 속도: (0, 0, 0) m/s (유동 없음)
  - 압력: 0 Pa
  - 난류 k: 0.00375 m²/s²
  - 난류 ε: 0.0104 m²/s³

4.2 경계 조건:
  - 입구: [사용자 입력]
  - 출구: [사용자 입력]
  - 벽면: No-slip

5. 시뮬레이션 설정
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - 시간 범위: 0 ~ 3600초
  - 시간 스텝: 1e-6초 (적응형)
  - Courant 수: 0.5
  - 계산 시간: [사용자 입력]

6. 비교 결과
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6.1 속도 필드
  항목           sedFoam (U.b)    pimpleFoam (U)    차이
  ──────────────────────────────────────────────────────
  평균값         [계산]           [계산]            [%]
  최대값         [계산]           [계산]            [%]
  표준편차       [계산]           [계산]            [%]
  RMSE           -                -                 [계산]
  R²             -                -                 [계산]

6.2 압력 필드
  항목           sedFoam          pimpleFoam        차이
  ──────────────────────────────────────────────────────
  평균값         [계산]           [계산]            [%]
  최대값         [계산]           [계산]            [%]
  표준편차       [계산]           [계산]            [%]

6.3 난류 특성
  항목           sedFoam          pimpleFoam        차이
  ──────────────────────────────────────────────────────
  k (평균)       [계산]           [계산]            [%]
  ε (평균)       [계산]           [계산]            [%]

7. 토의
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7.1 속도장 차이
  [분석 내용 작성]

7.2 압력장 차이
  [분석 내용 작성]

7.3 난류 특성
  [분석 내용 작성]

7.4 물리적 의미
  - 모래 입자의 영향
  - 상호작용 효과
  - 난류 모디피케이션

8. 결론
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [주요 발견사항]

9. 참고 자료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - sedFoam 매뉴얼
  - OpenFOAM pimpleFoam 튜토리얼
  - 논문 참고 문헌

"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 보고서 템플릿 생성: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="OpenFOAM 단상/이상유동 비교 분석 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  python3 compare_foams.py --summary
  python3 compare_foams.py --sedfoam_path ../ --pimple_path ./singlePhase_case/
  python3 compare_foams.py --report comparison_report.txt
        """
    )
    
    parser.add_argument('--sedfoam_path', type=str, default='../', 
                        help='sedFoam 케이스 경로 (기본값: ../)')
    parser.add_argument('--pimple_path', type=str, default='./singlePhase_case/', 
                        help='pimpleFoam 케이스 경로')
    parser.add_argument('--summary', action='store_true', 
                        help='케이스 요약 정보 출력')
    parser.add_argument('--report', type=str, metavar='FILE',
                        help='비교 보고서 템플릿 생성')
    parser.add_argument('--time', type=float, metavar='SECONDS',
                        help='특정 시간 비교')
    
    args = parser.parse_args()
    
    # 비교 객체 생성
    try:
        comparator = FOAMComparator(args.sedfoam_path, args.pimple_path)
    except Exception as e:
        print(f"❌ 오류: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 요약 정보 출력
    if args.summary or len(sys.argv) == 1:
        comparator.print_summary()
    
    # 보고서 생성
    if args.report:
        comparator.generate_report_template(args.report)
    
    # 특정 시간 비교
    if args.time:
        print(f"\n⏱️  시간 {args.time}초 데이터 준비 중...")
        print("   (실제 구현: foamFileHandler 또는 PyFoam 사용)")
    
    print("\n" + "="*70)
    print("💡 팁: 데이터 추출을 위해 foamFileHandler 또는 PyFoam 설치 권장")
    print("   pip install foam")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
