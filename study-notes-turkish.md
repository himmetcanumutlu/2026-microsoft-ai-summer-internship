# Çalışma Notları

Bu notlar, **Local README & Project Documentation RAG Assistant** projesinin arkasındaki teorik kavramları özetler.

---

## RAG Nedir?
**RAG (Retrieval-Augmented Generation):** "Veri erişimiyle artırılmış üretim." Kısacası yapay zekâ uydurmaz, kitaba bakarak konuşur.

Normal bir yapay zekâ önceden öğrendiği şeyi söyler. RAG ise önce kütüphaneye bakar.

- **R – Retrieval (Arama):** Soru sorduğunuzda sistem önce kendi veritabanındaki belgeleri tarar ve ilgili bilgileri bulur.
- **A – Augmented (Ekleme):** Bulduğu doğru bilgileri sorduğunuz sorunun yanına bir not olarak iliştirir.
- **G – Generation (Üretim):** Yapay zekâ bu notları okur ve yalnızca oradaki gerçeklere dayanarak cevap verir.

**Artıları**
- Doğru bilgi
- Güncel
- Gizlilik
- Düşük maliyet (modeli yeniden eğitmeye kıyasla)
- Güvenilir kaynak
- Halüsinasyonu engeller
- Modeli sıfırdan eğitmeye gerek yok

**Eksileri**
- Hız kaybı
- Kötü veri riski
- İlk kurulum zorluğu
- Ek maliyet: sunucu ve arama maliyetleri
- Dil bariyeri: Türkçe belgelerin içeriğini tam anlamıyla anlaması için arama motoru vb. gerekebilir.

---

## Foundry Local
Yapay zekâyı bulut yerine doğrudan kendi bilgisayarında çalıştırmanı sağlayan bir Microsoft teknolojisi.

**Artıları**
- İnternet/bulut masrafı yok
- Tamamen gizli
- Bedava
- Cihazın kaynaklarını akıllıca kullanır
- Sıfır gecikme

**Eksileri**
- Cihaz gücüne bağımlılık
- Yüksek depolama alanı
- Sınırlı model zekâsı
- Pil tüketimi
- İlk kurulum zorluğu

---

## Proje: Yerel README ve Proje Dokümantasyon Robotu
Projedeki tüm kod dosyalarını (.py, .cs, README.md) taratırsınız. Sonra yapay zekâya "Bu projenin veritabanı bağlantısı nasıl yapılıyor?" ya da "Projeye yeni bir API eklemek istersem hangi sınıfı kopyalamalıyım?" gibi sorular sorarsınız.

- **Bileşenler:** File Scanner + ChromaDB + Foundry Local
- **Arayüz:** Streamlit veya Gradio

---

## File Scanner
Belirtilen dosya yoluna girer ve klasörleri recursive olarak (alt klasörleri de) gezer. Gerekenleri okur, istenmeyenleri eler. Okuduğu dosyaları küçük metin parçalarına böler ve metadata ekler.

**Artıları**
- Tam gizlilik
- Yerel çalışma
- Esnek filtreleme
- Gürültüsüz veri
- Kaynak izleme

**Eksileri**
- **Parçalama zorluğu (chunking):** Düz metinde kolay, ama kodlarda sorun olabilir. Bunun için "Header/AST based chunking" yapılmalı.
- **Encoding istisnaları:** UTF-8 dışı dosyalar sorun çıkarabilir.
- **Bellek yükü:** Dev projelerde bellek yükü artar.

---

## ChromaDB
Yapay zekâ ve RAG için açık kaynaklı bir vektör veritabanı. Kelimeleri olduğu gibi aramak yerine onları sayı dizilerine (vektörlere) dönüştürür ve anlamsal yakınlığa göre arar. Buna **semantik benzerlik** denir.

**Artıları**
- Kolay kurulum
- Gömülü çalışır
- Otomatik embedding
- Metadata filtreleme

**Eksileri**
- Ölçek sınırı
- Sürüm güncellemesi sorunları
- Varsayılan model boyutu

---

## Vektör Veritabanı: Anlamsal Yakınlık (Semantic Similarity)
Yazılışları farklı olsa bile aynı anlama gelen kelimeleri yakalayabilme yeteneği.

**Örnek: "hata logları" araması**
- **Klasik veritabanı:** Sadece "hata logları" ifadesini birebir arar. Sonuç yok. ❌
- **Semantik veritabanı:** Anlamı arar ve `error_trace.txt` ile "istisna bildirimleri" gibi sonuçları bulur. ✅
