# SIC/XE Assembler by Ezgi GÜL (b210109004)

Bu proje, SIC/XE Assembler'ını içerir. PyQt5 kullanarak GUI (Grafik Kullanıcı Arayüzü) ile kullanıcıların bir assembler dosyası seçip çalıştırmalarını sağlar. 

## İçindekiler

- [Özellikler](#özellikler)
- [Gereksinimler](#gereksinimler)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Dosya Yapısı](#dosya-yapısı)
- [Kod Açıklamaları](#kod-açıklamaları)
- [Algoritma](#algoritma)

## Özellikler

- PyQt5 tabanlı GUI
- SIC/XE assembler dosyalarını seçme ve çalıştırma
- Çalıştırma sonuçlarını GUI üzerinde görüntüleme
- Hata mesajlarını görüntüleme

## Gereksinimler

Bu projeyi çalıştırmak için aşağıdaki yazılımlara ihtiyacınız var:

- Python 3.x
- PyQt5
- PyInstaller (exe oluşturmak için)

## Kurulum

1. Bu projeyi bilgisayarınıza indirin.


2. Gerekli Python paketlerini yükleyin.
    
    pip install pyqt5 pyinstaller
    

## Kullanım

    Dist dosyasının içindeki exe dosyasını çalıştırın. İnput dosyası olarak inputs dosyası içerisindeki input.txt dosyasını girdi olarak verebilirsiniz. Eğer exe halini çalıştıramıyorsanız aşağıdaki adımlaru uygulayın:
    
    a. **Assembler'ı Çalıştırmak:**
        python main.py

    b. **Executable Oluşturmak:**

        Spec dosyasını kullanarak executable oluşturabilirsiniz:

        pyinstaller main.spec

    c. **Executable Dosyasını Çalıştırmak:**
        ./dist/main/main

## Dosya Yapısı

- main.py: PyQt5 tabanlı GUI uygulaması
- assembler.py: Assembler işlevlerini gerçekleştiren dosya
- opcode.txt: Opcode bilgilerini içeren dosya
- main.spec: PyInstaller için spec dosyası
- README.md: Proje hakkında bilgi içeren dosya

## Kod Açıklamaları

### main.py :  
PyQt5 tabanlı bir GUI sağlar. Bu arayüzü kullanarak assembler dosyalarını seçebilir ve çalıştırabilirsiniz.

- SICXEAssemblerApp Sınıfı: Ana uygulama sınıfıdır.
- initUI(): Kullanıcı arayüzünü başlatır.
- open_file_dialog(): Dosya seçme dialogunu açar.
- run_assembler(): Assembler'ı çalıştırır.
- handle_stdout(): Standart çıktıyı işler ve GUI'de gösterir.
- handle_stderr(): Hata çıktısını işler ve GUI'de gösterir.
- assembler_finished(): Assembler işlemi tamamlandığında çağrılır, sonuçları GUI'de gösterir.
### assembler.py:
- assembler.py dosyası, SIC/XE assembly dilini işleyip nesne kodu oluşturan işlevleri içerir.

Pass 1 İşlevleri:

    readOptab(): Opcode tablosunu dosyadan okur.
    searchSymtab(): Sembol tablosunda arama yapar.
    insertSymtab(): Sembol tablosuna yeni semboller ekler.
    writeSymtab(): Sembol tablosunu dosyaya yazar.
    writeIntermediate(): Ara dosyaya satır yazar.
    isOpcode(): Opcode'un geçerli olup olmadığını kontrol eder.
    insertLiteral(): Literalleri ekler.
    writeLiterals(): Literalleri dosyaya yazar.
    processLine(): Girdi satırını işler ve uygun işlemleri yapar.
    processInputFile(): Girdi dosyasını okur ve işler.
    pass1(): Pass 1 işlemini gerçekleştirir.

Pass 2 İşlevleri:

    readOptabPass2(): Opcode tablosunu Pass 2 için okur.
    readSymtabPass2(): Sembol tablosunu Pass 2 için okur.
    readIntermediate(): Ara dosyayı okur.
    split_line(): Satırı böler ve bileşenlerine ayırır.
    pass2(): Pass 2 işlemini gerçekleştirir ve nesne kodu oluşturur.
    writeObjectProgram(): Nesne programını dosyaya yazar.

## Algoritma:
### Pass 1
    1. Opcode tablosunu oku.
    2. Girdi dosyasını satır satır işle:
        Label, opcode ve operandları ayır.
        Opcode "START" ise başlangıç adresini ayarla.
        Opcode "END" ise literalleri yaz.
        Opcode "ORG", "EQU", "LTORG", "USE" komutlarını işle.
        Label varsa sembol tablosuna ekle.
        Opcode varsa ve operand literal ise literali ekle.
        Adres sayacını (LOCCTR) güncelle.
    3. Sembol tablosunu dosyaya yaz.
    4. Program uzunluğunu hesapla.

### Pass 2
    1. Opcode tablosunu oku.
    2. Sembol tablosunu oku.
    3. Ara dosyayı oku ve satır satır işle:
        Adres, label, opcode ve operandları ayır.
        "START" ve "END" komutlarını işle.
        Nesne kodunu oluştur ve uygun formatta metin kayıtlarına ekle.
    4. Nesne programını dosyaya yaz.
    # assembler
