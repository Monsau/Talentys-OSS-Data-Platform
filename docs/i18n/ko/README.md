# Dremio + dbt + OpenMetadata - 문서 (한국어)

**버전**: 3.2.5  
**최종 업데이트**: 2025년 10월 16일  
**언어**: 한국어 🇰🇷

---

## 📚 개요

Dremio + dbt + OpenMetadata 데이터 플랫폼 한국어 문서에 오신 것을 환영합니다. 이 문서는 플랫폼의 설정, 구성 및 사용에 대한 포괄적인 가이드를 제공합니다.

---

## 🗺️ 문서 구조

### 📐 아키텍처

- **[Dremio 포트 - 시각적 가이드](./architecture/dremio-ports-visual.md)** ⭐ 새로운!
  - 3개의 Dremio 포트(9047, 31010, 32010)에 대한 완전한 시각적 가이드
  - PostgreSQL 프록시 상세 아키텍처
  - 성능 비교 및 벤치마크
  - 사용 사례 및 의사 결정 트리
  - 연결 예제: psql, DBeaver, Python, Java, ODBC
  - Docker Compose 구성
  - 456 줄 | 8+ Mermaid 다이어그램 | 5개 코드 예제

---

## 🌍 사용 가능한 언어

이 문서는 여러 언어로 제공됩니다:

- 🇫🇷 **[Français](../fr/README.md)** - 전체 문서 (22개 파일)
- 🇬🇧 **[English](../../../README.md)** - 전체 문서 (19개 파일)
- 🇪🇸 **[Español](../es/README.md)** - 시각적 가이드
- 🇵🇹 **[Português](../pt/README.md)** - 시각적 가이드
- 🇨🇳 **[中文](../cn/README.md)** - 시각적 가이드
- 🇯🇵 **[日本語](../jp/README.md)** - 시각적 가이드
- 🇷🇺 **[Русский](../ru/README.md)** - 시각적 가이드
- 🇸🇦 **[العربية](../ar/README.md)** - 시각적 가이드
- 🇩🇪 **[Deutsch](../de/README.md)** - 시각적 가이드
- 🇰🇷 **[한국어](../ko/README.md)** - 시각적 가이드 ⭐ 현재 위치
- 🇮🇳 **[हिन्दी](../hi/README.md)** - 시각적 가이드
- 🇮🇩 **[Indonesia](../id/README.md)** - 시각적 가이드
- 🇹🇷 **[Türkçe](../tr/README.md)** - 시각적 가이드
- 🇻🇳 **[Tiếng Việt](../vi/README.md)** - 시각적 가이드
- 🇮🇹 **[Italiano](../it/README.md)** - 시각적 가이드
- 🇳🇱 **[Nederlands](../nl/README.md)** - 시각적 가이드
- 🇵🇱 **[Polski](../pl/README.md)** - 시각적 가이드
- 🇸🇪 **[Svenska](../se/README.md)** - 시각적 가이드

---

## 🚀 빠른 시작

### 사전 요구사항

- Docker & Docker Compose
- Python 3.11+
- Git

### 설치

```bash
# 저장소 복제
git clone <repository-url>
cd dremiodbt

# Docker 서비스 시작
docker-compose up -d

# 웹 UI 열기
# Dremio: http://localhost:9047
# OpenMetadata: http://localhost:8585
```

자세한 설치 지침은 [영문 문서](../en/getting-started/installation.md)를 참조하세요.

---

## 📖 주요 리소스

### Dremio 포트 - 빠른 참조

| 포트 | 프로토콜 | 사용 | 성능 |
|------|-----------|------------|----------|
| **9047** | REST API | 웹 UI, 관리 | ⭐⭐ 표준 |
| **31010** | PostgreSQL Wire | BI 도구, 마이그레이션 | ⭐⭐⭐ 양호 |
| **32010** | Arrow Flight | dbt, Superset, 고성능 | ⭐⭐⭐⭐⭐ 최대 |

**→ [전체 시각적 가이드](./architecture/dremio-ports-visual.md)**

---

## 🔗 외부 링크

- **Dremio 문서**: https://docs.dremio.com/
- **dbt 문서**: https://docs.getdbt.com/
- **OpenMetadata 문서**: https://docs.open-metadata.org/
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

## 🤝 기여

기여를 환영합니다! [기여 가이드라인](../en/CONTRIBUTING.md)을 참조하세요.

---

## 📄 라이선스

이 프로젝트는 [MIT 라이선스](../../../LICENSE)에 따라 라이선스가 부여됩니다.

---

**버전**: 3.2.5  
**상태**: ✅ 프로덕션 준비 완료  
**최종 업데이트**: 2025년 10월 16일
