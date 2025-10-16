# Dremio + dbt + OpenMetadata - Tài liệu (Tiếng Việt)

**Phiên bản**: 3.2.5  
**Cập nhật lần cuối**: 16 Tháng 10, 2025  
**Ngôn ngữ**: Tiếng Việt 🇻🇳

---

## 📚 Tổng quan

Chào mừng đến với tài liệu tiếng Việt cho nền tảng dữ liệu Dremio + dbt + OpenMetadata. Tài liệu này cung cấp hướng dẫn toàn diện về cài đặt, cấu hình và sử dụng nền tảng.

---

## 🗺️ Cấu trúc Tài liệu

### 📐 Kiến trúc

- **[Dremio Ports - Hướng dẫn Trực quan](./architecture/dremio-ports-visual.md)** ⭐ MỚI!
  - Hướng dẫn trực quan đầy đủ cho 3 cổng Dremio (9047, 31010, 32010)
  - Kiến trúc chi tiết PostgreSQL Proxy
  - So sánh hiệu suất và đánh giá
  - Trường hợp sử dụng và sơ đồ quyết định
  - Ví dụ kết nối: psql, DBeaver, Python, Java, ODBC
  - Cấu hình Docker Compose
  - 456 dòng | 8+ sơ đồ Mermaid | 5 ví dụ mã

---

## 🌍 Ngôn ngữ Có sẵn

Tài liệu này có sẵn bằng nhiều ngôn ngữ:

- 🇫🇷 **[Français](../fr/README.md)** - Tài liệu đầy đủ (22 tệp)
- 🇬🇧 **[English](../../../README.md)** - Tài liệu đầy đủ (19 tệp)
- 🇪🇸 **[Español](../es/README.md)** - Hướng dẫn trực quan
- 🇵🇹 **[Português](../pt/README.md)** - Hướng dẫn trực quan
- 🇨🇳 **[中文](../cn/README.md)** - Hướng dẫn trực quan
- 🇯🇵 **[日本語](../jp/README.md)** - Hướng dẫn trực quan
- 🇷🇺 **[Русский](../ru/README.md)** - Hướng dẫn trực quan
- 🇸🇦 **[العربية](../ar/README.md)** - Hướng dẫn trực quan
- 🇩🇪 **[Deutsch](../de/README.md)** - Hướng dẫn trực quan
- 🇰🇷 **[한국어](../ko/README.md)** - Hướng dẫn trực quan
- 🇮🇳 **[हिन्दी](../hi/README.md)** - Hướng dẫn trực quan
- 🇮🇩 **[Indonesia](../id/README.md)** - Hướng dẫn trực quan
- 🇹🇷 **[Türkçe](../tr/README.md)** - Hướng dẫn trực quan
- 🇻🇳 **[Tiếng Việt](../vi/README.md)** - Hướng dẫn trực quan ⭐ BẠN Ở ĐÂY
- 🇮🇹 **[Italiano](../it/README.md)** - Hướng dẫn trực quan
- 🇳🇱 **[Nederlands](../nl/README.md)** - Hướng dẫn trực quan
- 🇵🇱 **[Polski](../pl/README.md)** - Hướng dẫn trực quan
- 🇸🇪 **[Svenska](../se/README.md)** - Hướng dẫn trực quan

---

## 🚀 Bắt đầu Nhanh

### Yêu cầu

- Docker & Docker Compose
- Python 3.11+
- Git

### Cài đặt

```bash
# Clone repository
git clone <repository-url>
cd dremiodbt

# Khởi động các dịch vụ Docker
docker-compose up -d

# Mở Web UI
# Dremio: http://localhost:9047
# OpenMetadata: http://localhost:8585
```

Để biết hướng dẫn cài đặt chi tiết, xem [tài liệu tiếng Anh](../en/getting-started/installation.md).

---

## 📖 Tài nguyên Chính

### Dremio Ports - Tham khảo Nhanh

| Cổng | Giao thức | Sử dụng | Hiệu suất |
|------|-----------|------------|----------|
| **9047** | REST API | Web UI, Quản trị | ⭐⭐ Tiêu chuẩn |
| **31010** | PostgreSQL Wire | Công cụ BI, Di chuyển | ⭐⭐⭐ Tốt |
| **32010** | Arrow Flight | dbt, Superset, Hiệu suất Cao | ⭐⭐⭐⭐⭐ Tối đa |

**→ [Hướng dẫn trực quan đầy đủ](./architecture/dremio-ports-visual.md)**

---

## 🔗 Liên kết Ngoài

- **Tài liệu Dremio**: https://docs.dremio.com/
- **Tài liệu dbt**: https://docs.getdbt.com/
- **Tài liệu OpenMetadata**: https://docs.open-metadata.org/
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

## 🤝 Đóng góp

Đóng góp được hoan nghênh! Vui lòng xem [hướng dẫn đóng góp](../en/CONTRIBUTING.md) của chúng tôi.

---

## 📄 Giấy phép

Dự án này được cấp phép theo [Giấy phép MIT](../../../LICENSE).

---

**Phiên bản**: 3.2.5  
**Trạng thái**: ✅ Sẵn sàng Sản xuất  
**Cập nhật lần cuối**: 16 Tháng 10, 2025
