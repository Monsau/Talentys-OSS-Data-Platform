# 数据平台

**企业数据湖仓解决方案**

**Language**: 中文 (CN)  
**Version**: 3.2.5  
**Last Updated**: 2025-10-15

---

## 概述

专业数据平台，结合Dremio、dbt和Apache Superset，提供企业级数据转换、质量保证和商业智能。

该平台为现代数据工程提供全面解决方案，包括自动化数据管道、质量测试和交互式仪表板。

```mermaid
graph LR
    A[Data Sources] --> B[Dremio]
    B --> C[dbt]
    C --> D[Superset]
    D --> E[Business Insights]
    
    style B fill:#f5f5f5,stroke:#333,stroke-width:2px
    style C fill:#e8e8e8,stroke:#333,stroke-width:2px
    style D fill:#d8d8d8,stroke:#333,stroke-width:2px
```

---

## 主要功能

- 基于Dremio的数据湖仓架构
- 使用dbt进行自动化转换
- 使用Apache Superset进行商业智能
- 全面的数据质量测试
- 通过Arrow Flight进行实时同步

---

## 快速入门指南

### 前提条件

- Docker 20.10或更高版本
- Docker Compose 2.0或更高版本
- Python 3.11或更高版本
- 最低8 GB内存

### 安装

```bash
# Install dependencies
pip install -r requirements.txt

# Start services
make up

# Verify installation
make status

# Run quality tests
make dbt-test
```

---

## 架构

### 系统组件

| 组件 | 端口 | 描述 |
|-----------|------|-------------|
| Dremio | 9047, 31010, 32010 | 数据湖仓平台 |
| dbt | - | 数据转换工具 |
| Superset | 8088 | Business intelligence platform |
| PostgreSQL | 5432 | Transactional database |
| MinIO | 9000, 9001 | Object storage (S3-compatible) |
| Elasticsearch | 9200 | Search and analytics engine |

### 📚 架构文档

- 📘 [架构文档](architecture/) - 详细的系统设计
- 🎯 [Dremio 端口可视化指南](architecture/dremio-ports-visual.md) ⭐ **新增** - Dremio 三个端口的完整可视化指南

---

## 文档

### 入门
- [Installation Guide](getting-started/)
- [Configuration](getting-started/)
- [First Steps](getting-started/)

### 用户指南
- [Data Engineering](guides/)
- [Dashboard Creation](guides/)
- [API Integration](guides/)

### API文档
- [REST API Reference](api/)
- [Authentication](api/)
- [Code Examples](api/)

### 架构文档
- [System Design](architecture/)
- [Data Flow](architecture/)
- [Deployment Guide](architecture/)

---

## 可用语言

| Language | Code | Documentation |
|----------|------|---------------|
| English | EN | [README.md](../../../README.md) |
| Français | FR | [docs/i18n/fr/](../fr/README.md) |
| Español | ES | [docs/i18n/es/](../es/README.md) |
| Português | PT | [docs/i18n/pt/](../pt/README.md) |
| العربية | AR | [docs/i18n/ar/](../ar/README.md) |
| 中文 | CN | [docs/i18n/cn/](../cn/README.md) |
| 日本語 | JP | [docs/i18n/jp/](../jp/README.md) |
| Русский | RU | [docs/i18n/ru/](../ru/README.md) |

---

## 支持

For technical assistance:
- Documentation: [Main README](../../../README.md)
- Issue Tracking: GitHub Issues
- Community Forum: GitHub Discussions
- Email: support@example.com

---

**[返回主文档](../../../README.md)**
