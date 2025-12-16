# LLM Dəstəkli Tapşırıq İdarəetmə Sistemi - Biznes Təqdimatı

## Sistem Nədir?

Müasir tapşırıq idarəetmə sistemi - komandaların işlərini strukturlaşdırmaq, irəliləyişi izləmək və süni intellekt vasitəsilə avtomatik hesabatlar yaratmaq üçün.

## Əsas Xüsusiyyətlər

### 1. İyerarxik Struktur
- **Layihələr** → **Tapşırıqlar** → **Alt Tapşırıqlar**
- Hər səviyyənin statusu avtomatik hesablanır
- Alt tapşırıqlardan layihəyə qədər avtomatik yeniləmə

### 2. Rollar və Səlahiyyətlər

**Layihə Sahibi** (ilk qeydiyyatdan keçən):
- İstifadəçilər və komandalar yaradır
- Layihələr yaradır və komandalara təhvil verir
- LLM vasitəsilə ümumi hesabatlar alır

**Komanda Lideri**:
- Üzvlərin hesabatlarını təsdiqləyir
- Keyfiyyət nəzarətini həyata keçirir

**Komanda Üzvü**:
- Tapşırıqları icra edir
- İş haqqında hesabatlar yazır

### 3. Avtomatik Status Yeniləmələri
- Alt tapşırıq statusu → Tapşırıq statusunu təyin edir
- Tapşırıq statusları → Layihə statusunu təyin edir
- Real-vaxt izləmə və yeniləmə

### 4. LLM Təhlili
- Təsdiqlənmiş bütün hesabatları toplayır
- Layihə məlumatlarını analiz edir
- Layihə Sahibinə ümumi vəziyyət hesabatı verir
- İrəliləyiş faizi və əsas məlumatlar

### 5. Təsdiqləmə Mexanizmi
```
İstifadəçi Hesabatı → Komanda Lideri Təsdiqləyir → Layihə Sahibinə Çatır → LLM Analizi
```

## Biznes Dəyəri

✅ **Səmərəlilik**: Avtomatik proseslər vaxta qənaət edir  
✅ **Qərar Vermə**: LLM sayəsində böyük məlumatı tez analiz etmək  
✅ **Şəffaflıq**: Hər səviyyədə iş proseslərinin aydın görünməsi  
✅ **Keyfiyyət**: Təsdiqləmə mexanizmi sayəsində etibarlı məlumat  
✅ **Miqyaslaşdırılabilirlik**: Çoxlu komanda və layihənin idarə edilməsi

## İş Prosesi

1. **Qurulum**: Layihə Sahibi sistemə daxil olur → İstifadəçilər və komandalar yaradılır
2. **İşləmə**: Üzvlər tapşırıqları icra edir → Hesabatlar yazılır → Liderlər təsdiqləyir
3. **Analitika**: LLM bütün məlumatı analiz edir → Ümumi hesabat verir

---

**Məqsəd**: Komandaların işlərini effektiv idarə etmək, irəliləyişi izləmək və düzgün qərar vermək üçün lazım olan məlumatı avtomatik şəkildə təqdim etmək.

