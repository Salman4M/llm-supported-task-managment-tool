# LLM Dəstəkli Tapşırıq İdarəetmə Sistemi - Biznes Sənədləri

## 1. Layihənin Məqsədi

**LLM Dəstəkli Tapşırıq İdarəetmə Sistemi** - komandaların iş proseslərini strukturlaşdırmaq, tapşırıqların icrasını izləmək və süni intellekt vasitəsilə avtomatik hesabatlar yaratmaq üçün hazırlanmış müasir biznes həllidir.

## 2. İstifadəçi Rolları və Səlahiyyətlər

### 2.1 Layihə Sahibi (Project Owner)
- **Rolu**: Sistemdə ilk qeydiyyatdan keçən şəxs avtomatik olaraq Layihə Sahibi statusu alır
- **Səlahiyyətlər**:
  - İstifadəçilər yaratmaq və idarə etmək
  - Komandalar yaratmaq və istifadəçiləri komandalara təyin etmək
  - Layihələr yaratmaq və komandalara təhvil vermək
  - Təsdiqlənmiş hesabatları LLM vasitəsilə analiz etdirmək və ümumi məlumat almaq
  - Bütün layihələrin vəziyyətini izləmək

### 2.2 Komanda Lideri (Team Lead)
- **Rolu**: Komanda üzvlərinin işlərini idarə edən və nəzarət edən şəxs
- **Səlahiyyətlər**:
  - Komanda üzvlərinin yazdığı hesabatları təsdiqləmək və ya rədd etmək
  - Yalnız təsdiqlənmiş hesabatlar Layihə Sahibinə çatır
  - Komandanın tapşırıqlarını izləmək

### 2.3 Komanda Üzvü (Team Member)
- **Rolu**: Tapşırıqları icra edən əsas işçilər
- **Səlahiyyətlər**:
  - Özünə təyin edilmiş tapşırıqları görmək və icra etmək
  - İş haqqında hesabatlar yazmaq
  - Tapşırıqların statusunu yeniləmək

## 3. Sistem Arxitekturası

### 3.1 İyerarxik Struktur

```
Layihə Sahibi
    └── Komandalar
        └── Komanda Üzvləri
            └── Layihələr
                └── Tapşırıqlar (Tasks)
                    └── Alt Tapşırıqlar (Subtasks)
```

### 3.2 Status İyerarxiyası

Sistemdə hər səviyyənin statusu aşağıdakı prinsiplə işləyir:

- **Alt Tapşırıqlar**: İcra olunan əsas işlər
- **Tapşırıqlar**: Statusu alt tapşırıqların vəziyyətinə əsasən avtomatik hesablanır
- **Layihələr**: Statusu tapşırıqların ümumi vəziyyətinə görə avtomatik yenilənir

**Status Növləri**:
- To Do (Gözləyir)
- In Progress (Davam edir)
- Review (Nəzərdən keçirilir)
- Done (Tamamlandı)

### 3.3 Hesabatların Axını

```
Komanda Üzvü → Hesabat yazır
    ↓
Komanda Lideri → Hesabatı təsdiqləyir (verify)
    ↓
Təsdiqlənmiş Hesabatlar → Layihə Sahibinə çatır
    ↓
LLM Təhlili → Ümumi hesabat və məlumatlar
```

## 4. Əsas Funksionallıq

### 4.1 İstifadəçi İdarəetməsi
- Yeni istifadəçilərin qeydiyyatı
- İstifadəçilərin rollara bölünməsi
- Komandalara üzvlərin təyin edilməsi
- İstifadəçi profillərinin idarə edilməsi

### 4.2 Komanda İdarəetməsi
- Komandaların yaradılması
- Komanda üzvlərinin təyin edilməsi
- Komanda üzvlərinin müxtəlif komandalarda iştirakı
- Komandaların layihələrlə əlaqələndirilməsi

### 4.3 Layihə İdarəetməsi
- Layihələrin yaradılması
- Layihələrin komandalara təhvil verilməsi
- Layihə məlumatlarının (ad, təsvir, deadline) idarə edilməsi
- Layihə statuslarının avtomatik hesablanması
- Layihələrin aktiv/passiv vəziyyətinin idarə edilməsi

### 4.4 Tapşırıq İdarəetməsi
- Tapşırıqların yaradılması və alt tapşırıqlara bölünməsi
- Tapşırıqların istifadəçilərə təyin edilməsi
- Tapşırıq statuslarının yenilənməsi
- Tapşırıq və alt tapşırıq statuslarının bir-birinə təsiri
- Deadline təyin edilməsi və izlənməsi

### 4.5 Hesabat Sistemi

#### İstifadəçi Hesabatları
- Komanda üzvləri öz işləri haqqında hesabatlar yazır
- Hesabatlar konkret tapşırıqlarla əlaqələndirilir
- İlkin vəziyyətdə hesabatlar təsdiqlənməmiş olur

#### Təsdiqləmə Prosesi
- Komanda Lideri hesabatları nəzərdən keçirir
- Təsdiqləmədən sonra hesabatlar Layihə Sahibinə çatır
- Yalnız təsdiqlənmiş hesabatlar sonrakı işləməyə daxil olur

#### LLM Təhlili
- Layihə Sahibi tələb etdikdə, sistem təsdiqlənmiş bütün hesabatları toplayır
- LLM bütün hesabatları və layihə məlumatlarını analiz edir
- Ümumi vəziyyət hesabatı, irəliləyiş faizi və əsas məlumatlar yaradılır
- Layihə Sahibi üçün anlaşıqlı və faydalı məlumat təqdim olunur

## 5. Biznes Dəyəri

### 5.1 Səmərəliliyin Artırılması
- Avtomatik status yeniləmələri vaxta qənaət edir
- İyerarxik struktura görə layihələrin vəziyyəti aydın görünür
- Komanda üzvləri öz işlərinə diqqət yetirə bilirlər

### 5.2 Qərar Vermənin Sürətləndirilməsi
- LLM təhlili vasitəsilə böyük miqdarda məlumatı tez analiz etmək
- Layihə Sahibinə dərhal ümumi vəziyyət haqqında məlumat vermək
- Komanda Liderlərinin təsdiqləmə prosesi sayəsində keyfiyyətli məlumatın təmin edilməsi

### 5.3 Şəffaflıq və Nəzarət
- Hər səviyyədə iş proseslərinin izlənməsi
- Hesabatların təsdiqləmə mexanizmi sayəsində keyfiyyətli məlumat
- Bütün statusların real vaxt rejimində yenilənməsi

### 5.4 Miqyaslaşdırılabilirlik
- Çoxlu komanda və layihənin idarə edilməsi
- İstifadəçilərin və komandaların asanlıqla əlavə edilməsi
- Böyük layihələrin alt tapşırıqlara bölünərək idarə edilməsi

## 6. İş Prosesi

### 6.1 İlkin Quraşdırma
1. Layihə Sahibi sistemə qeydiyyatdan keçir
2. İstifadəçilər yaradılır və rollar təyin edilir
3. Komandalar yaradılır və üzvlər təyin edilir
4. Layihələr yaradılır və komandalara təhvil verilir

### 6.2 Gündəlik İş Prosesi
1. Komanda Üzvləri tapşırıqları icra edir
2. Tapşırıq statusları yenilənir
3. Komanda Üzvləri iş haqqında hesabatlar yazır
4. Komanda Liderləri hesabatları təsdiqləyir
5. Təsdiqlənmiş hesabatlar Layihə Sahibinə çatır

### 6.3 Analitika və Hesabatlar
1. Layihə Sahibi tələb edir
2. Sistem bütün təsdiqlənmiş hesabatları toplayır
3. LLM hesabatları və layihə məlumatlarını analiz edir
4. Ümumi hesabat və irəliləyiş məlumatları yaradılır
5. Layihə Sahibi qərar verir

## 7. Texnoloji Xüsusiyyətlər (Qısa)

- Modern web platforması
- Real-vaxt status yeniləmələri
- İyerarxik məlumat strukturu
- Süni intellekt inteqrasiyası
- Təhlükəsiz istifadəçi autentifikasiyası
- Miqyaslaşdırılabilir arxitektura

## 8. Gələcək İnkişaf İstiqamətləri

- Real-vaxt bildirişlər sistemi
- Gelişmiş analitika və qrafiklər
- Mobil tətbiq dəstəyi
- Əlavə inteqrasiyalar
- Daha inkişaf etmiş LLM funksionallığı

---

**Qeyd**: Bu sənəd biznes baxımından sistemin funksionallığını və dəyərini izah etmək üçün hazırlanmışdır. Texniki detallar və tətbiq detalları ayrıca texniki sənədlərdə təqdim olunur.

