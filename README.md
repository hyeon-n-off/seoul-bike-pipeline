# 🚲 서울 공공자전거 ELT 파이프라인 | `2026.05.19 - 2026.05.21`
공공 데이터를 활용한 ELT 데이터 파이프라인 프로젝트

### 목적

간단한 데이터 파이프라인을 구현해보며, 전체적인 흐름을 이해하고 익숙해지는 경험을 해보자.

---

### E, T, L이란?

ETL / ELT 모두 다음 세 가지 단계를 포함합니다.

- **E / Extract (추출)**: 데이터 소스에서 데이터를 가져오는 것을 의미합니다.
- **T / Transform (변환)**: 데이터의 구조를 변경하는 프로세스를 의미합니다. 정제, 변형 등의 단계를 통해 데이터를 필요한 형태로 변환합니다.
- **L / Load (적재)**: 데이터를 스토리지에 저장하는 프로세스를 의미합니다.

#### ETL vs ELT

ETL은 추출(Extract) → 변환(Transform) → 적재(Load) 순으로 처리하는 방식이고,
ELT는 추출(Extract) → 적재(Load) → 변환(Transform) 순으로 처리하는 방식입니다.

ETL은 데이터 웨어하우스에 들어가기 전에 데이터를 처리하는 반면, ELT는 데이터가 적재된 후 데이터 웨어하우스 내부에서 데이터를 변환합니다.

| | ETL | ELT |
|---|---|---|
| **장점** | 민감한 데이터를 마스킹/필터링 후 적재할 수 있어 보안에 유리 | 원본 데이터를 그대로 보관하므로 로직 변경이 유연 |
| | 변환 후 적재하므로 스토리지 용량 절약 가능 | 클라우드 DW의 컴퓨팅 파워를 활용해 대용량 처리에 유리 |
| | 레거시 시스템과의 호환성이 높음 | |
| **단점** | 변환 로직이 바뀌면 파이프라인을 재실행해야 함 | 원본 데이터를 그대로 적재하므로 스토리지 비용 증가 |
| | 대용량 데이터 처리 시 속도가 느림 | 민감한 데이터가 웨어하우스에 그대로 적재되므로 보안 관리 필요 |

---

### 기술 스택

| 역할 | 기술 | 설명 |
|---|---|---|
| 데이터 웨어하우스 | Snowflake | 클라우드 기반 데이터 웨어하우스로, 대용량 데이터를 저장하고 SQL로 분석할 수 있는 플랫폼 |
| 데이터 변환 | dbt | 데이터 웨어하우스 내부에서 SQL로 데이터를 변환하는 도구. 모델 간 의존관계를 자동으로 파악해 실행 순서를 결정 |
| 워크플로우 오케스트레이션 | Airflow + Cosmos | 데이터 파이프라인의 작업들을 DAG(Directed Acyclic Graph) 형태로 정의하고, 스케줄링 및 모니터링하는 도구 |
| 시각화 | Streamlit | Python 기반 대시보드 라이브러리 |

---

### 아키텍처

```
Airflow + Cosmos (스케줄링 & 모니터링)
┌──────────────────────────────────────────────┐
│  Raw Data → Snowflake → dbt (정제 및 변환)    │
└──────────────────────────────────────────────┘
                      ↓
             Streamlit 시각화
```

---

### 데이터 설명

- **출처**: 공공데이터포털 - 서울특별시 공공자전거 이용정보(시간대별)
- **규모**: 약 180만 행
- **컬럼**: 대여일자, 대여시간, 대여소번호, 대여소명, 대여구분코드, 성별, 연령대, 이용건수, 운동량, 탄소량, 이동거리, 이용시간

---

### 프로젝트 구조 및 설명

```
seoul_bike/
├── models/
│   ├── staging/
│   │   ├── sources.yml              # 소스 정의
│   │   └── stg_bike_usage.sql       # 정제 및 표준화
│   └── marts/
│       ├── dim_stations.sql         # 대여소 마스터 테이블
│       ├── fct_hourly_usage.sql     # 시간대별 이용 패턴
│       ├── fct_user_profile.sql     # 성별/연령대별 이용 패턴
│       └── fct_station_ranking.sql  # 대여소별 이용량 순위
├── airflow/
│   └── dags/
│       └── dbt_dag.py               # Cosmos DAG 정의
├── streamlit_app.py                 # 대시보드
└── profiles.yml.example             # dbt 프로필 예시
```

#### Staging
원본 데이터를 정제하는 레이어입니다. 비즈니스 로직은 넣지 않고, 순수하게 데이터를 깔끔하게 만드는 단계입니다. (`stg_bike_usage.sql`)

- 컬럼명 표준화
- 데이터 타입 변환
- 이상값 필터링
- 값 표준화

`sources.yml` 파일은 Snowflake에 이미 적재되어 있는 원본 데이터가 어디에 있고, 어떤 규칙을 만족해야 하는지(데이터 품질 테스트) dbt에게 알려주는 명세서입니다.

#### Marts
스테이징 단계에서 정제된 데이터를 비즈니스 목적에 맞게 집계/변환하는 단계입니다. 실제 분석에 사용되는 테이블들이 여기 위치하며, Dimension Table과 Fact Table로 나뉩니다.

**Fact Table** — 실제 비즈니스에서 발생한 이벤트를 저장하는 테이블
- 매출액, 이용건수, 이동거리 등 수치 데이터 위주
- 데이터가 지속적으로 누적되어 테이블이 길어지는 구조
- 상세 정보 대신 다른 테이블을 가리키는 ID(외래키) 위주로 저장

**Dimension Table** — Fact Table의 상세 정보(who, what, where, when)를 제공하는 테이블
- 이름, 카테고리, 지역 등 텍스트 데이터 위주
- Fact Table에 비해 크기가 작고 가로로 넓은 구조
- `WHERE`, `GROUP BY` 등 필터링/그룹화에 활용

---

### 데이터 변환 과정
Raw Data (Snowflake 원본)
<img width="3552" height="248" alt="Image" src="https://github.com/user-attachments/assets/f88fd2b0-79cb-4b88-9704-fc5382306330" />

Staging(stg_bike_usage) - 정제 및 표준화
> 소문자 성별 통일, 렌탈 종류 영문화, 이용 건수 0 이하 필터링

<img width="3552" height="187" alt="Image" src="https://github.com/user-attachments/assets/8e26743c-20c5-44b3-a1b1-768a13c339b6" />

Marts
`dim_stations` - 대여소 마스터 테이블
<img width="595" height="187" alt="Image" src="https://github.com/user-attachments/assets/eeb64d11-9ad5-4837-ac27-ea14e35e32e7" />

`fct_hourly_usage` - 시간대별 이용 패턴
<img width="1483" height="186" alt="Image" src="https://github.com/user-attachments/assets/6e9481ac-dc93-4406-a87c-6cfca4cafd3f" />

`fct_user_profile` - 성별/연령대별 이용 패턴
<img width="1778" height="187" alt="Image" src="https://github.com/user-attachments/assets/5ba81100-15dd-4936-945c-086e16e01f11" />

`fct_station_ranking` - 대여소별 이용량 순위
<img width="1779" height="187" alt="Image" src="https://github.com/user-attachments/assets/146f5eed-3d9d-4469-a609-ffeadd169d7f" />

---

###### Airflow DAG 그래프
<img width="1281" height="872" alt="Image" src="https://github.com/user-attachments/assets/fea11c98-ec0b-4282-8926-c09492b618bf" />

###### Streamlit
<img width="1918" height="642" alt="Image" src="https://github.com/user-attachments/assets/75c1d6a3-efaf-40d7-8a4c-dcd5ca684027" />

<img width="1914" height="518" alt="Image" src="https://github.com/user-attachments/assets/1f463b7b-d8bd-4658-8b73-538f4cbe4e19" />

<img width="1916" height="671" alt="Image" src="https://github.com/user-attachments/assets/15e8dde8-d732-4ef3-b7dd-ce46ab786bee" />

<img width="1910" height="441" alt="Image" src="https://github.com/user-attachments/assets/c67077fd-05e3-4f70-81a3-8848570b862a" />

<img width="1915" height="634" alt="Image" src="https://github.com/user-attachments/assets/471de814-ba7d-4828-80be-3899e0790f98" />