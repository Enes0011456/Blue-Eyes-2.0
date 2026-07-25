import os,time,sys,time,json,re,random,threading
from google import genai
from google.genai import client,types

# Renk kodları (terminal)
LIGHT_BLUE = '\033[38;2;2;82;223m'  
BLUE = "\033[91m" 
ENDC = "\033[0m" 
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
# Syntax highlighting renkleri (terminal)
SYN_KEYWORD  = "\033[95m"   # Magenta - keyword
SYN_STRING   = "\033[92m"   # Green   - string
SYN_COMMENT  = "\033[90m"   # Gray    - comment
SYN_NUMBER   = "\033[93m"   # Yellow  - number
SYN_BUILTIN  = "\033[96m"   # Cyan    - built-in
# Ayarlar dosyası 
SETTINGS_FILE = "blue_eyes_settings.json"
# Varsayılan ayarlar
DEFAULT_SETTINGS = {
    "api_key": "",
    "karakter_adi": "BLUE EYES",
    "karakter_ayari": "",
    "tema": "dark",          # dark / light  (GUI için)
    "typing_delay": 0.005,
    "offline_mod": False,
    "model": "gemini-2.0-flash",    # veya "gemini-1.5-flash"
    #"model": "gemini-2.5-flash",
    "dil": "tr"
}
# Akıllı soru önerileri YENİ - Konuya göre öneri listesi
SORU_ONERILERI = {
    "kod": [
        "Bu kodu nasıl optimize edebilirim?",
        "Bu kodda hata var mı?",
        "Bunu daha Pythonic yazabilir misin?",
        "Unit test nasıl yazarım?",
    ],
    "genel": [
        "Bunu daha detaylı açıklar mısın?",
        "Bir örnek verir misin?",
        "Alternatif yöntemler neler?",
        "Avantajları ve dezavantajları neler?",
        "Bunu nasıl öğrenebilirim?",
    ],
    "hata": [
        "Bu hatanın sebebi ne?",
        "Nasıl düzeltebilirim?",
        "Benzer hatalardan nasıl kaçınırım?",
    ]
}
# Offline AI basit yanıtları YENİ - API keysiz çalışma için yerel yanıt sistemi
OFFLINE_YANIT = {
    "merhaba": "Merhaba! Ben BLUE EYES. Şu an offline modda çalışıyorum, API key olmadan sınırlı yanıt verebiliyorum.",
    "nasılsın": "İyiyim, teşekkürler! Offline modda çalışıyorum ama yine de buradayım.",
    "ne yapabilirsin": "Online modda: kod yazma, analiz, soru cevaplama yapabilirim. Şu an offline moddasın, /ayarlar ile API key ekle.",
    "yardım": "Komutlar için /help yaz. API key eklemek için /ayarlar veya /apikey kullan.",
    "default": [
        "Offline moddayım. Tam özellikler için /ayarlar ile API key ekle.",
        "API key olmadan detaylı yanıt veremiyorum. /apikey ile ekle.",
        "Bu soruya online modda daha iyi yanıt verebilirim. /ayarlar ile API key gir.",
    ]
}
# AYAR YÖNETİMİ KISMI
def ayarlari_yukle():
    """JSON dosyasından ayarları yükler."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Eksik anahtarları varsayılan sekilde doldur 
                for key, val in DEFAULT_SETTINGS.items():
                    if key not in data:
                        data[key] = val
                return data
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()
def ayarlari_kaydet(ayarlar):
    """Ayarları JSON dosyasına kaydeder."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(ayarlar, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"{RED}Ayarlar kaydedilemedi: {e}{ENDC}")
        return False
# TERMINAL YARDIMCI FONKSİYONLAR
def print_with_typing_animation(text, delay=0.005):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()
def print_with_typing_animation(text, delay=0.005):
    """Metni yazıcı etkisiyle terminale yazdırır."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # Yeni satır 
def display_ascii_art():
    # ansı renk kodları 
    BLUE = '\033[94m' # Parlak Mavi Renk
    ENDC = '\033[0m'  # Rengi Sıfırla 
####------------------------------------------------------------------------
# Not: \ karakterleri terminalde düzgün görünsün diye \\ şeklinde çiftlendi o yüzden
    ascii_art = f"""
{BLUE}
             / \\                           / \\           
            /   \\                         /   \\          
   ________/     \\_______________________/     \\________
  |  ░█▀▀█ ░█─── ░█──░█ ░█▀▀▀    ░█▀▀▀ ░█──░█ ░█▀▀▀ ░█▀▀▀█  |
  |  ░█▀▀▄ ░█─── ░█──░█ ░█▀▀▀    ░█▀▀▀ ─░█▀░─ ░█▀▀▀ ─▀▀▀▄▄  |
  |  ░█▄▄█ ░█▄▄█ ░█▄▄▄█ ░█▄▄▄    ░█▄▄▄ ──░█── ░█▄▄▄ ░█▄▄▄█  |
   ‾‾‾‾‾‾‾‾\\     /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\\     /‾‾‾‾‾‾‾‾
            \\   /                       \\   /           
             \\ /                         \\ /
{ENDC}
"""
    # animasyon fonksiyonunu çagırıyor
    print_with_typing_animation(ascii_art, 0.001)
# YENİ Syntax Highlighting Fonksiyonu
def syntax_highlight_terminal(code):
    """
    Terminal için basit Python syntax highlighting
    [YENİ] - Tamamen yeni fonksiyon
    """
    KEYWORDS = r'\b(def|class|import|from|return|if|elif|else|for|while|try|except|finally|with|as|pass|break|continue|and|or|not|in|is|True|False|None|lambda|yield|global|nonlocal|del|raise|assert)\b'
    BUILTINS = r'\b(print|len|range|type|int|str|float|list|dict|set|tuple|input|open|enumerate|zip|map|filter|sorted|reversed|any|all|max|min|sum|abs|round|isinstance|hasattr|getattr|setattr)\b'
    result = code
    # Önce stringleri işaretle (çakışmayı önlemek için)
    result = re.sub(r'(""".*?"""|\'\'\'.*?\'\'\'|".*?"|\'.*?\')',
                    lambda m: SYN_STRING + m.group(0) + ENDC, result, flags=re.DOTALL)
    # Yorumlar
    result = re.sub(r'(#[^\n]*)', SYN_COMMENT + r'\1' + ENDC, result)
    # Sayılar
    result = re.sub(r'\b(\d+\.?\d*)\b', SYN_NUMBER + r'\1' + ENDC, result)
    # Keywords
    result = re.sub(KEYWORDS, SYN_KEYWORD + r'\1' + ENDC, result)
    # Builtins
    result = re.sub(BUILTINS, SYN_BUILTIN + r'\1' + ENDC, result)
    return result
###------------------------------------------------
def yanitta_kod_isle(text):
    """
    AI yanıtındaki kod bloklarını syntax highlighting ile işler
    YENİ - Tamamen yeni fonksiyon
    """
    def replace_code_block(m):
        lang = m.group(1).strip().lower() if m.group(1) else ""
        code = m.group(2)
        border = "─" * 50
        header = f"{CYAN}┌{border}┐\n│ {'python' if lang == 'python' else lang or 'kod':^48} │\n└{border}┘{ENDC}"
        if lang in ("python", "py", ""):
            highlighted = syntax_highlight_terminal(code)
        else:
            highlighted = code
        return f"\n{header}\n{highlighted}\n{CYAN}{'─' * 52}{ENDC}\n"
    # ```lang\ncode``` bloklarını işle
    result = re.sub(r'```(\w*)\n?(.*?)```', replace_code_block, text, flags=re.DOTALL)
    return result
###------------------------------------------------
# YENİ Akıllı soru önerileri 
def onerileri_goster(son_yanit):
    """
    Son yanıta göre ilgili soru önerileri gösterir.
    [YENİ] - Tamamen yeni fonksiyon
    """
    if any(k in son_yanit.lower() for k in ["def ", "class ", "import ", "```python", "fonksiyon", "kod"]):
        kategori = "kod"
    elif any(k in son_yanit.lower() for k in ["hata", "error", "exception", "traceback"]):
        kategori = "hata"
    else:
        kategori = "genel"
    oneriler = random.sample(SORU_ONERILERI[kategori], min(3, len(SORU_ONERILERI[kategori])))

    print(f"\n{DIM}{CYAN} Önerilen sorular :{ENDC}")
    for i, soru in enumerate(oneriler, 1):
        print(f"{DIM}   {i}. {soru}{ENDC}")
###------------------------------------------------
# YENİ Offline AI Kısmı 
def offline_yanit_uret(user_input):
    """
    API key olmadan basit yerel yanıtlar üretir
    YENİ - Tamamen yeni fonksiyon
    """
    user_lower = user_input.lower().strip()
    for anahtar, yanit in OFFLINE_YANIT.items():
        if anahtar != "default" and anahtar in user_lower:
            return yanit
    return random.choice(OFFLINE_YANIT["default"])
###------------------------------------------------
###------------------------------------------------
# YENİ KOMUTLAR
def komut_help():
    """
    /help, /komutlar komutunu işler.
    [YENİ] - Tamamen yeni fonksiyon
    """
    yardim = f"""

{BLUE}╔══════════════════════════════════════════════════╗
║           BLUE EYES - KOMUT REHBERİ              ║
╚══════════════════════════════════════════════════╝{ENDC}
{BOLD}{CYAN}── Temel Komutlar ────────────────────────────────{ENDC}
  /help, /komutlar     → Bu yardım menüsünü gösterir
  /hakkında, /about    → Program hakkında bilgi
  /ayarlar, /settings  → Ayarlar menüsüne girer
  /apikey              → API key hızlı değiştirme
  /durum, /status      → Bağlantı ve mod durumu
  çıkış, exit, q       → Programdan çıkar
{BOLD}{CYAN}── Metin Modu ────────────────────────────────────{ENDC}
  /uzun, ///, /m       → Çok satırlı metin modu
                          (END yazıp Enter ile bitir)
{BOLD}{CYAN}── Konuşma ───────────────────────────────────────{ENDC}
  /yeni                → Yeni konuşma başlat
  /oneriler            → Soru önerilerini göster
{BOLD}{CYAN}── Mod ───────────────────────────────────────────{ENDC}
  /offline             → Offline moda geç
  /online              → Online moda geç (API gerekli)
{DIM}İpucu: Konuşma sırasında istediğin zaman /ayarlar yazabilirsin!{ENDC}
"""
    print(yardim)
###------------------------------------------------###
###Beni arıyorsan benim kimligim burda sana kolay gelsin asağıdaki 
#sifreyi çöz bul beni :) !!!  (Ama anahtarların olmadan Yapıcaksın :)) ! ) (Bakalım Anahtar Olmadan neler yapabilirsin bence en fazla milyarlarca bruteforce ile anahtarı bulamyı deneyip kırmayı deniceksin ama basarısız olcaksınız haberiniz olsun :) !!! )
###------------------------------------------------###
def komut_hakkinda():
    """
    /hakkında komutunu işler.
    [YENİ] - Tamamen yeni fonksiyon
    """
    hakkinda = f"""
{BLUE}╔══════════════════════════════════════════════════╗
║               BLUE EYES  v2.0                    ║
╚══════════════════════════════════════════════════╝{ENDC}
  {BOLD}Geliştirici:{ENDC}  (Bunu Çöz Bulursun :) !!! ) ###XOR:BCJeWVgTRXclbykXKVoTWDwOEQkSHRsvLBIHkf1vMjYKMg1AVwhfHxQYVxsmEyUIO437SA9HBzUTHwsbAAZPEIyHXYrXNKuOMKmIAxRSLDSy+RtaCTc/HCtXc0NJZHRUWk8GFzUQSQlmbRpvKw0NFho3DC8yXnNkA1cCbwOhxHI2IhYKIwV6bA1aB1NSDxMvFgUt9d9nR0ZueG0vCQ4vFws3scUTsd45pNk7pNEZbw03LIP/PWIKMSQFOXMCUExXDnBQZn8TJ1oBDgs4RmcYIlxrD1YsVBYAdykkNCNXKKL0Fz8iNSILKVUTXT1HGEIQFi8MO1G0gURKRh01QzAYIRUaGEjx4BXyxhuFiDuPzChGDlYgk4Y/CzomPR4qcUBvQ21ycmNgBVUmORAFajMdTGEiKXVgEj86FgdZZS1BIEME74BuLhQENzwHQzpdCjEwHQ==
  {BOLD}Motor:{ENDC}        ???
  {BOLD}Versiyon:{ENDC}     2.0  
  {BOLD}Dil:{ENDC}          Python 

  {CYAN}Özellikler:{ENDC}
        Terminal & GUI mod
        Syntax highlighting
        Akıllı soru önerileri  
        API key yöneticisi
        Offline AI modu
        Dark/Light tema (GUI)
        Çok satırlı metin girişi
        Anlık ayar değişimi

{DIM}  Ayarlar {SETTINGS_FILE} dosyasına kaydedilir.{ENDC}
"""
    print(hakkinda)
def komut_durum(ayarlar, client_aktif):
    """
    /durum komutunu işler.
    [YENİ] - Tamamen yeni fonksiyon
    """
    api_durum = f"{GREEN} Bağlı{ENDC}" if (client_aktif and not ayarlar["offline_mod"]) else f"{RED} Bağlı Değil{ENDC}"
    mod = f"{YELLOW} Offline{ENDC}" if ayarlar["offline_mod"] else f"{GREEN} Online{ENDC}"
    api_goster = ("*" * (len(ayarlar["api_key"]) - 4) + ayarlar["api_key"][-4:]) if len(ayarlar["api_key"]) > 4 else "(boş)"
    print(f"""
{CYAN}Sistem Durumu     {ENDC}
  API Bağlantısı : {api_durum}
  Çalışma Modu   : {mod}
  Model          : {ayarlar['model']}
  API Key        : {api_goster}
  Ayar Dosyası   : {SETTINGS_FILE}
{CYAN}                  {ENDC}""")
###------------------------------------------------
#  YENİ AYARLAR MENÜSÜ (Terminal)
def terminal_ayarlar_menusu(ayarlar):
    """
    Konuşma sırasında veya başlangıçta çağrılabilen ayar menüsü.
    [YENİ] - Tamamen yeni fonksiyon
    Hem /ayarlar komutuyla hem de yeni konuşma öncesi erişilebilir.
    """
    while True:
        print(f"""
{BLUE}╔══════════════════════════════════════════════════╗
║                AYARLAR MENÜSÜ                   ║
╚══════════════════════════════════════════════════╝{ENDC}
  {BOLD}1.{ENDC} API Key Değiştir
  {BOLD}2.{ENDC} Karakter Adı Değiştir
  {BOLD}3.{ENDC} Karakter Kişiliği Ayarla
  {BOLD}4.{ENDC} Yazma Hızı Ayarla
  {BOLD}5.{ENDC} Offline Mod: {'[AÇIK]' if ayarlar['offline_mod'] else '[KAPALI]'}
  {BOLD}6.{ENDC} Model Seç
  {BOLD}7.{ENDC} Tüm Ayarları Göster
  {BOLD}0.{ENDC} Geri Dön
{DIM}Seçiminiz: {ENDC}""", end="")
        secim = input().strip()
        if secim == "0":
            print_with_typing_animation(f"{GREEN}Ayarlar kaydedildi. Konuşmaya dönülüyor...{ENDC}", 0.01)
            break
        elif secim == "1":
            # [YENİ] API Key yönetimi - hem ayarlardan hem /apikey komutuyla erişilebilir
            print(f"\n{CYAN}Mevcut API Key:{ENDC} ", end="")
            if ayarlar["api_key"]:
                gizli = "*" * (len(ayarlar["api_key"]) - 4) + ayarlar["api_key"][-4:]
                print(gizli)
            else:
                print("(boş)")
            print(f"{YELLOW}Yeni API Key girin (boş bırakırsanız değişmez):{ENDC} ", end="")
            yeni_key = input().strip()
            if yeni_key:
                ayarlar["api_key"] = yeni_key
                ayarlari_kaydet(ayarlar)
                print(f"{GREEN} API Key güncellendi! Yeni konuşmada aktif olur.{ENDC}")
                print(f"{YELLOW}  Yeni API key'in aktif olması için programı yeniden başlat.{ENDC}")
            else:
                print(f"{DIM}Değiştirilmedi.{ENDC}")
        elif secim == "2":
            print(f"\n{CYAN}Mevcut isim:{ENDC} {ayarlar['karakter_adi']}")
            print(f"{YELLOW}Yeni isim:{ENDC} ", end="")
            yeni_isim = input().strip()
            if yeni_isim:
                ayarlar["karakter_adi"] = yeni_isim
                ayarlari_kaydet(ayarlar)
                print(f"{GREEN} İsim '{yeni_isim}' olarak güncellendi!{ENDC}")
        elif secim == "3":
            print(f"\n{CYAN}Mevcut kişilik:{ENDC}")
            print(ayarlar["karakter_ayari"] or "(boş - varsayılan Gemini davranışı)")
            print(f"\n{YELLOW}Yeni kişilik açıklaması (boş = değiştirme):{ENDC}")
            print(f"{DIM}Örnek: 'Sen bir siber güvenlik uzmanısın, esprili ve teknik konuşursun.'{ENDC}")
            yeni_kisilik = input().strip()
            if yeni_kisilik:
                ayarlar["karakter_ayari"] = yeni_kisilik
                ayarlari_kaydet(ayarlar)
                print(f"{GREEN} Kişilik güncellendi! Yeni konuşmada aktif olur.{ENDC}")
        elif secim == "4":
            print(f"\n{CYAN}Mevcut yazma hızı:{ENDC} {ayarlar['typing_delay']} saniye/karakter")
            print(f"{YELLOW}Yeni hız (0.001=çok hızlı, 0.05=yavaş):{ENDC} ", end="")
            try:
                yeni_hiz = float(input().strip())
                if 0 < yeni_hiz < 1:
                    ayarlar["typing_delay"] = yeni_hiz
                    ayarlari_kaydet(ayarlar)
                    print(f"{GREEN} Yazma hızı güncellendi!{ENDC}")
                else:
                    print(f"{RED}Geçersiz değer (0-1 arası olmalı){ENDC}")
            except ValueError:
                print(f"{RED}Geçersiz sayı{ENDC}")
        elif secim == "5":
            ayarlar["offline_mod"] = not ayarlar["offline_mod"]
            durum = "AÇILDI" if ayarlar["offline_mod"] else "KAPATILDI"
            renk = YELLOW if ayarlar["offline_mod"] else GREEN
            print(f"{renk} Offline mod {durum}!{ENDC}")
            ayarlari_kaydet(ayarlar)
        elif secim == "6":
            modeller = [
                "gemini-2.5-flash",
                "gemini-2.5-pro",
                "gemini-2.0-flash",
                "gemini-1.5-flash",
            ]
            print(f"\n{CYAN}Mevcut model:{ENDC} {ayarlar['model']}")
            print(f"\n{YELLOW}Model seçin:{ENDC}")
            for i, m in enumerate(modeller, 1):
                isaretli = " ← aktif" if m == ayarlar["model"] else ""
                print(f"  {i}. {m}{DIM}{isaretli}{ENDC}")
            print("  Seçim (1-4): ", end="")
            try:
                secim2 = int(input().strip())
                if 1 <= secim2 <= len(modeller):
                    ayarlar["model"] = modeller[secim2 - 1]
                    ayarlari_kaydet(ayarlar)
                    print(f"{GREEN} Model '{ayarlar['model']}' seçildi!{ENDC}")
            except ValueError:
                print(f"{RED}Geçersiz seçim{ENDC}")
        elif secim == "7":
            print(f"\n{CYAN}── Tüm Ayarlar ───────────────────────────────{ENDC}")
            for k, v in ayarlar.items():
                if k == "api_key" and v:
                    v = "*" * (len(v) - 4) + v[-4:]
                print(f"  {k:20} : {v}")
            print(f"{CYAN}──────────────────────────────────────────────{ENDC}")
        else:
            print(f"{RED}Geçersiz seçim{ENDC}")
    return ayarlar
###------------------------------------------------
#  GEMİNİ İSTEMCİ OLUŞTURMA
def gemini_baglantisi_kur(ayarlar):
    """
    Gemini client ve chat oturumu oluşturur.
    [DEĞİŞTİRİLDİ] - Artık ayarlar dict'inden API key alıyor,
                      sabit değişken yerine.
    """
    try:
        from google import genai
        from google.genai import types
        if not ayarlar["api_key"]:
            return None, None, "API key boş"
        client = genai.Client(api_key=ayarlar["api_key"])

        chat = client.chats.create(
            model=ayarlar["model"],
            config=types.GenerateContentConfig(
                system_instruction=ayarlar["karakter_ayari"] or None
            )
        )
        return client, chat, None
    except ImportError:
        return None, None, "google-genai kütüphanesi yüklü değil (pip install google-genai)"
    except Exception as e:
        return None, None, str(e)
#  API YANIT FONKSİYONU
def get_response(chat, user_input, ayarlar):
    """
    Kullanıcı girdisine yanıt üretir.
    [DEĞİŞTİRİLDİ] - Offline mod desteği eklendi,
                      chat None olabilir artık.
    """
    if ayarlar["offline_mod"] or chat is None:
        # [YENİ] Offline mod
        return offline_yanit_uret(user_input)
    try:
        response = chat.send_message(user_input)
        if response and hasattr(response, 'text'):
            return response.text or "Üzgünüm, geçerli bir yanıt alınamadı."
        return "Üzgünüm, geçerli bir yanıt alınamadı."
    except Exception as e:
        return f"API hatası: {e}"
#  ÇOK SATIRLI GİRİŞ
def get_multiline_input():
    print_with_typing_animation(" Uzun metin modu aktif! Metninizi yazın:", 0.01)
    print_with_typing_animation(" Bitirmek için yeni satırda 'END' yazıp Enter.", 0.01)
    print("-" * 50)
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        except EOFError:
            break
    full_text = "\n".join(lines)
    if full_text.strip():
        print_with_typing_animation(f"\n{len(lines)} satır, {len(full_text)} karakter alındı.", 0.01)
    return full_text
#  [YENİ] API KEY HIZLI DEĞİŞTİRME KOMUTU
def apikey_hizli_degistir(ayarlar):
    """
    /apikey komutu - hızlı API key değiştirme.
    [YENİ] - Tamamen yeni fonksiyon.
    Hem /apikey komutuyla hem ayarlar menüsü 1. seçeneğiyle erişilebilir.
    """
    print(f"\n{CYAN}╔═ API KEY YÖNETİCİSİ ═══════════════════════╗{ENDC}")
    if ayarlar["api_key"]:
        gizli = "*" * (len(ayarlar["api_key"]) - 4) + ayarlar["api_key"][-4:]
        print(f"{CYAN}║{ENDC} Mevcut: {gizli}")
    else:
        print(f"{CYAN}║{ENDC} Mevcut: {RED}(boş){ENDC}")
    print(f"{CYAN}╚════════════════════════════════════════════╝{ENDC}")
    print(f"\n{YELLOW}Yeni API Key (boş = iptal):{ENDC} ", end="")
    yeni = input().strip()
    if yeni:
        ayarlar["api_key"] = yeni
        ayarlari_kaydet(ayarlar)
        print(f"{GREEN} API Key kaydedildi! Programı yeniden başlat.{ENDC}")
    else:
        print(f"{DIM}İptal edildi.{ENDC}")
    return ayarlar
###------------------------------------------------
#  TERMİNAL ANA DÖNGÜSÜ
def terminal_modu():
    """
    Terminal modunda ana sohbet döngüsü.
    [DEĞİŞTİRİLDİ] - Komutlar, ayarlar, offline mod, syntax highlight eklendi.
                      Eski sabit değişkenler yerine ayarlar dict kullanılıyor.
    """
    ayarlar = ayarlari_yukle()
    display_ascii_art()
    KARAKTER_ADI = ayarlar["karakter_adi"]
    print_with_typing_animation(f"--- {KARAKTER_ADI} 'a Hoş Geldin! ---", 0.01)
    # Bağlantı kur
    client, chat, hata = gemini_baglantisi_kur(ayarlar)
    if hata and not ayarlar["offline_mod"]:
        print(f"\n{YELLOW}  API bağlantısı kurulamadı: {hata}{ENDC}")
        print(f"{YELLOW}   Offline modda devam ediliyor. /apikey ile API key ekleyin.{ENDC}\n")
        ayarlar["offline_mod"] = True
    elif not ayarlar["offline_mod"]:
        print(f"{GREEN} Gemini bağlantısı başarılı!{ENDC}")

    if ayarlar["offline_mod"]:
        print(f"{YELLOW} Offline mod aktif - sınırlı yanıtlar{ENDC}")
    print_with_typing_animation(f"\n{DIM}Komutlar için /help | Ayarlar için /ayarlar | Çıkış için 'çıkış'{ENDC}", 0.005)
    print_with_typing_animation("-" * 50, 0.003)
    son_yanit = ""
    # Yeni konuşma öncesi ayarlara girme seçeneği
    print(f"\n{DIM}Konuşmaya başlamadan önce ayarlara girmek ister misin? (e/h): {ENDC}", end="")
    on_ayar = input().strip().lower()
    if on_ayar == "e":
        ayarlar = terminal_ayarlar_menusu(ayarlar)
        # Ayarlar değiştiyse yeniden bağlan
        client, chat, hata = gemini_baglantisi_kur(ayarlar)
    while True:
        user_input = input(f"\n{BOLD}Sen : {ENDC}").strip()
        # Çıkış
        if user_input.lower() in ["çıkış", "exit", "quit", "q"]:
            print_with_typing_animation(f"\n{BLUE}{KARAKTER_ADI}: Gene beklerim, bay bay! 👋{ENDC}", 0.01)
            break
        # YENİ Komutlar
        elif user_input.lower() in ["/help", "/komutlar", "/?", "/yardım"]:
            komut_help()
            continue
        elif user_input.lower() in ["/hakkında", "/hakkinda", "/about", "/info"]:
            komut_hakkinda()
            continue
        elif user_input.lower() in ["/ayarlar", "/settings", "/config"]:
            # YENİ Konuşma SIRASINDA ayarlara girme
            ayarlar = terminal_ayarlar_menusu(ayarlar)
            KARAKTER_ADI = ayarlar["karakter_adi"]
            continue
        elif user_input.lower() in ["/apikey", "/api", "/key"]:
            # Hızlı API key değiştirme komutu
            ayarlar = apikey_hizli_degistir(ayarlar)
            continue
        elif user_input.lower() in ["/durum", "/status", "/stat"]:
            komut_durum(ayarlar, chat is not None)
            continue
        elif user_input.lower() in ["/offline"]:
            # Offline moda geçiş
            ayarlar["offline_mod"] = True
            ayarlari_kaydet(ayarlar)
            print(f"{YELLOW} Offline mod aktif!{ENDC}")
            continue
        elif user_input.lower() in ["/online"]:
            #  Online moda geçiş
            ayarlar["offline_mod"] = False
            ayarlari_kaydet(ayarlar)
            if chat is None:
                client, chat, hata = gemini_baglantisi_kur(ayarlar)
                if hata:
                    print(f"{RED} Bağlantı kurulamadı: {hata}{ENDC}")
                    ayarlar["offline_mod"] = True
                else:
                    print(f"{GREEN} Online moda geçildi!{ENDC}")
            else:
                print(f"{GREEN} Online moda geçildi!{ENDC}")
            continue
        elif user_input.lower() in ["/oneriler", "/öneriler"]:
            # Manuel öneri gösterme
            onerileri_goster(son_yanit)
            continue
        elif user_input.lower() in ["/yeni"]:
            print(f"{CYAN}Yeni konuşma başlatılıyor...{ENDC}")
            client, chat, hata = gemini_baglantisi_kur(ayarlar)
            son_yanit = ""
            print(f"{GREEN} Yeni konuşma başladı!{ENDC}")
            continue
        # Uzun metin modu 
        elif user_input.lower() in ["/uzun", "/long", "///", '"""', "/multiline", "/m", "//", "/l"]:
            user_input = get_multiline_input()
            if not user_input.strip():
                print_with_typing_animation(f"{YELLOW}Boş metin, iptal.{ENDC}", 0.01)
                continue
            print_with_typing_animation(f"{DIM}Gönderiliyor... ({len(user_input)} karakter){ENDC}", 0.01)
        # Boş mesaj
        elif not user_input:
            print(f"{DIM}Boş mesaj gönderilemez.{ENDC}")
            continue
        # Yanıt al
        yanit = get_response(chat, user_input, ayarlar)
        son_yanit = yanit
        if yanit is None:
            yanit = "Şu anda yanıt veremiyorum, tekrar dene."
        # Syntax highlighting uygula
        yanit_gosterim = yanitta_kod_isle(yanit)
        print(f"\n{BLUE}{KARAKTER_ADI}: {ENDC}", end="")
        print_with_typing_animation(yanit_gosterim, ayarlar["typing_delay"])
        # Her 3 yanıtta bir öneri göster
        if random.random() < 0.3:
            onerileri_goster(yanit)
#  GUI MODU (Tkinter)
def gui_modu():
    """
    GUI modunda Tkinter arayüzü.
    [YENİ] - Tamamen yeni fonksiyon.
    Dark/Light tema, syntax highlighting, ayarlar penceresi içerir.
    GUI modda ayar değişimi sadece ayarlar penceresinden yapılır.
    """
    try:
        import tkinter as tk
        from tkinter import scrolledtext, messagebox, simpledialog
    except ImportError:
        print(f"{RED}Tkinter bulunamadı. Terminal modu kullanılıyor.{ENDC}")
        terminal_modu()
        return
    ayarlar = ayarlari_yukle()
    # Tema renkleri (GUİ için olan kısım) #Dark/Light tema sistemi
    TEMALAR = {
        "dark": {
            "bg":        "#0d1117",
            "bg2":       "#161b22",
            "fg":        "#e6edf3",
            "fg2":       "#8b949e",
            "accent":    "#58a6ff",
            "accent2":   "#3fb950",
            "user_bg":   "#1f2937",
            "bot_bg":    "#0d1117",
            "border":    "#30363d",
            "input_bg":  "#21262d",
            "btn_bg":    "#238636",
            "btn_fg":    "#ffffff",
            "code_bg":   "#161b22",
        },
        "light": {
            "bg":        "#ffffff",
            "bg2":       "#f6f8fa",
            "fg":        "#24292f",
            "fg2":       "#57606a",
            "accent":    "#0969da",
            "accent2":   "#1a7f37",
            "user_bg":   "#ddf4ff",
            "bot_bg":    "#f6f8fa",
            "border":    "#d0d7de",
            "input_bg":  "#f6f8fa",
            "btn_bg":    "#2da44e",
            "btn_fg":    "#ffffff",
            "code_bg":   "#f6f8fa",
        }
    }
    tema = TEMALAR[ayarlar.get("tema", "dark")]
    # Gemini bağlantısı
    client_ref = [None]
    chat_ref   = [None]
    def baglanti_kur():
        c, ch, hata = gemini_baglantisi_kur(ayarlar)
        client_ref[0] = c
        chat_ref[0]   = ch
        return hata
    baglanti_kur()
    # Ana pencere 
    root = tk.Tk()
    root.title(f"BLUE EYES v2.0 - {ayarlar['karakter_adi']}")
    root.geometry("900x650")
    root.configure(bg=tema["bg"])
    root.minsize(600, 400)
    # Font 
    FONT_CHAT  = ("Consolas", 11)
    FONT_INPUT = ("Consolas", 11)
    FONT_TITLE = ("Consolas", 14, "bold")
    FONT_BTN   = ("Consolas", 10)

###------------------------------------------------
    # Tema uygulama fonksiyonu 
    def temayı_uygula(yeni_tema_adi):
        nonlocal tema
        ayarlar["tema"] = yeni_tema_adi
        tema = TEMALAR[yeni_tema_adi]
        ayarlari_kaydet(ayarlar)
        root.configure(bg=tema["bg"])
        baslik_frame.configure(bg=tema["bg2"])
        baslik_lbl.configure(bg=tema["bg2"], fg=tema["accent"])
        durum_lbl.configure(bg=tema["bg2"], fg=tema["fg2"])
        sohbet_text.configure(bg=tema["bg"], fg=tema["fg"])
        alt_frame.configure(bg=tema["bg2"])
        giris_text.configure(bg=tema["input_bg"], fg=tema["fg"],
                              insertbackground=tema["fg"])
        gonder_btn.configure(bg=tema["btn_bg"], fg=tema["btn_fg"])
        ayarlar_btn.configure(bg=tema["bg2"], fg=tema["accent"])
        tema_btn.configure(bg=tema["bg2"], fg=tema["fg2"])
    # Arayüz bileşenleri # Başlık çubuğu
    baslik_frame = tk.Frame(root, bg=tema["bg2"], pady=8)
    baslik_frame.pack(fill=tk.X)
    baslik_lbl = tk.Label(baslik_frame, text=f"◈ {ayarlar['karakter_adi']}",
                           font=FONT_TITLE, bg=tema["bg2"], fg=tema["accent"])
    baslik_lbl.pack(side=tk.LEFT, padx=15)
    durum_lbl = tk.Label(baslik_frame, text="● Bağlanıyor...",
                          font=FONT_BTN, bg=tema["bg2"], fg=tema["fg2"])
    durum_lbl.pack(side=tk.LEFT, padx=5)
    # Tema toggle butonu (GUI'ye özel olan kısım - terminalde yok)
    def tema_degistir():
        yeni = "light" if ayarlar["tema"] == "dark" else "dark"
        temayı_uygula(yeni)
        tema_btn.configure(text=" Light" if yeni == "dark" else " Dark")
    tema_btn = tk.Button(baslik_frame,
                          text=" Light" if ayarlar["tema"] == "dark" else " Dark",
                          font=FONT_BTN, bg=tema["bg2"], fg=tema["fg2"],
                          relief=tk.FLAT, cursor="hand2",
                          command=tema_degistir)
    tema_btn.pack(side=tk.RIGHT, padx=5)
    # Ayarlar butonu - GUI'de sadece buradan API key yönetimi
    def gui_ayarlar_ac():
        ayar_win = tk.Toplevel(root)
        ayar_win.title("Ayarlar")
        ayar_win.geometry("480x520")
        ayar_win.configure(bg=tema["bg"])
        ayar_win.grab_set()
        tk.Label(ayar_win, text="  AYARLAR", font=FONT_TITLE,
                 bg=tema["bg"], fg=tema["accent"]).pack(pady=15)
        # API Key
        tk.Label(ayar_win, text="API Key:", font=FONT_BTN,
                 bg=tema["bg"], fg=tema["fg"]).pack(anchor=tk.W, padx=20)
        api_var = tk.StringVar(value=ayarlar["api_key"])
        api_entry = tk.Entry(ayar_win, textvariable=api_var,
                              font=FONT_INPUT, bg=tema["input_bg"],
                              fg=tema["fg"], show="*", width=50,
                              insertbackground=tema["fg"])
        api_entry.pack(padx=20, pady=5, fill=tk.X)
        # Göster/Gizle
        goster_var = tk.BooleanVar(value=False)
        def goster_gizle():
            api_entry.configure(show="" if goster_var.get() else "*")
        tk.Checkbutton(ayar_win, text="API Key'i göster",
                       variable=goster_var, command=goster_gizle,
                       bg=tema["bg"], fg=tema["fg2"],
                       selectcolor=tema["bg2"]).pack(anchor=tk.W, padx=20)
        # Karakter adı
        tk.Label(ayar_win, text="Karakter Adı:", font=FONT_BTN,
                 bg=tema["bg"], fg=tema["fg"]).pack(anchor=tk.W, padx=20, pady=(10, 0))
        isim_var = tk.StringVar(value=ayarlar["karakter_adi"])
        tk.Entry(ayar_win, textvariable=isim_var, font=FONT_INPUT,
                 bg=tema["input_bg"], fg=tema["fg"],
                 insertbackground=tema["fg"], width=30).pack(padx=20, pady=5, fill=tk.X)
        # Kişilik
        tk.Label(ayar_win, text="Karakter Kişiliği:", font=FONT_BTN,
                 bg=tema["bg"], fg=tema["fg"]).pack(anchor=tk.W, padx=20, pady=(10, 0))
        kisilik_text = tk.Text(ayar_win, font=FONT_INPUT,
                                bg=tema["input_bg"], fg=tema["fg"],
                                height=4, width=50,
                                insertbackground=tema["fg"])
        kisilik_text.insert("1.0", ayarlar["karakter_ayari"])
        kisilik_text.pack(padx=20, pady=5, fill=tk.X)
        # Offline mod
        offline_var = tk.BooleanVar(value=ayarlar["offline_mod"])
        tk.Checkbutton(ayar_win, text=" Offline Mod",
                       variable=offline_var,
                       bg=tema["bg"], fg=tema["fg2"],
                       selectcolor=tema["bg2"]).pack(anchor=tk.W, padx=20, pady=5)
        def kaydet():
            ayarlar["api_key"]       = api_var.get().strip()
            ayarlar["karakter_adi"]  = isim_var.get().strip() or "BLUE EYES"
            ayarlar["karakter_ayari"]= kisilik_text.get("1.0", tk.END).strip()
            ayarlar["offline_mod"]   = offline_var.get()
            ayarlari_kaydet(ayarlar)
            baslik_lbl.configure(text=f"◈ {ayarlar['karakter_adi']}")
            # Bağlantıyı yenile
            hata = baglanti_kur()
            durum_guncelle(hata)
            messagebox.showinfo("Kaydedildi", "Ayarlar kaydedildi!\nYeni API key aktif edildi.", parent=ayar_win)
            ayar_win.destroy()
        tk.Button(ayar_win, text="  Kaydet",
                  font=FONT_BTN, bg=tema["btn_bg"], fg=tema["btn_fg"],
                  relief=tk.FLAT, cursor="hand2", pady=6,
                  command=kaydet).pack(pady=15, ipadx=20)
    ayarlar_btn = tk.Button(baslik_frame, text="⚙ Ayarlar",
                             font=FONT_BTN, bg=tema["bg2"], fg=tema["accent"],
                             relief=tk.FLAT, cursor="hand2",
                             command=gui_ayarlar_ac)
    ayarlar_btn.pack(side=tk.RIGHT, padx=5)
    # Sohbet alanı
    sohbet_text = scrolledtext.ScrolledText(
        root, font=FONT_CHAT,
        bg=tema["bg"], fg=tema["fg"],
        relief=tk.FLAT, padx=15, pady=10,
        wrap=tk.WORD, state=tk.DISABLED,
        spacing3=5
    )
    sohbet_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 0))
    # Text tag'leri
    sohbet_text.tag_configure("kullanici",  foreground=tema["accent"],  font=("Consolas", 11, "bold"))
    sohbet_text.tag_configure("bot",        foreground=tema["accent2"], font=("Consolas", 11, "bold"))
    sohbet_text.tag_configure("mesaj",      foreground=tema["fg"])
    sohbet_text.tag_configure("kod",        foreground="#f0a500",       font=("Consolas", 10),
                               background=tema["code_bg"])
    sohbet_text.tag_configure("oneri",      foreground=tema["fg2"],     font=("Consolas", 10, "italic"))
    sohbet_text.tag_configure("sistem",     foreground=tema["fg2"],     font=("Consolas", 10))
    def mesaj_ekle(etiket, icerik, tag="mesaj"):
        sohbet_text.configure(state=tk.NORMAL)
        if etiket:
            sohbet_text.insert(tk.END, f"\n{etiket}\n",
                               "kullanici" if "Sen" in etiket else "bot")
        sohbet_text.insert(tk.END, icerik + "\n", tag)
        sohbet_text.configure(state=tk.DISABLED)
        sohbet_text.see(tk.END)
    def durum_guncelle(hata=None):
        if ayarlar["offline_mod"]:
            durum_lbl.configure(text=" Offline", fg="#f0a500")
        elif hata:
            durum_lbl.configure(text=f" {hata[:30]}", fg="red")
        else:
            durum_lbl.configure(text="● Bağlı", fg=tema["accent2"])
    durum_guncelle(None if chat_ref[0] else "API key gerekli")
    # Hoş geldin mesajı
    mesaj_ekle(None, f"◈ {ayarlar['karakter_adi']}'a hoş geldin!\n"
                      "Ayarlar için ⚙ butonunu, tema için Light / Dark butonunu kullan.\n",
               "sistem")
    # Alt giriş çubuğu
    alt_frame = tk.Frame(root, bg=tema["bg2"], pady=8)
    alt_frame.pack(fill=tk.X, side=tk.BOTTOM)
    giris_text = tk.Text(alt_frame, font=FONT_INPUT,
                          bg=tema["input_bg"], fg=tema["fg"],
                          height=3, relief=tk.FLAT,
                          insertbackground=tema["fg"],
                          padx=10, pady=5)
    giris_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5))
    def mesaj_gonder(event=None):
        user_input = giris_text.get("1.0", tk.END).strip()
        if not user_input:
            return "break"
        giris_text.delete("1.0", tk.END)
        mesaj_ekle("  Sen:", user_input)
        # Kod bloklarını GUI'de de işle
        yanit = get_response(chat_ref[0], user_input, ayarlar)
        # Kod bloklarını ayır
        parcalar = re.split(r'(```[\w]*\n?.*?```)', yanit, flags=re.DOTALL)
        mesaj_ekle(f"  {ayarlar['karakter_adi']}:", "", "bot")
        for parca in parcalar:
            if parca.startswith("```"):
                # Kod bloğu
                kod = re.sub(r'```\w*\n?', '', parca).strip()
                sohbet_text.configure(state=tk.NORMAL)
                sohbet_text.insert(tk.END, f"\n{kod}\n", "kod")
                sohbet_text.configure(state=tk.DISABLED)
            else:
                if parca.strip():
                    sohbet_text.configure(state=tk.NORMAL)
                    sohbet_text.insert(tk.END, parca, "mesaj")
                    sohbet_text.configure(state=tk.DISABLED)
        sohbet_text.configure(state=tk.NORMAL)
        sohbet_text.insert(tk.END, "\n")
        sohbet_text.configure(state=tk.DISABLED)
        sohbet_text.see(tk.END)
        # GUI'de öneri göster
        if random.random() < 0.35:
            oneriler = random.sample(SORU_ONERILERI["genel"], 2)
            oneri_txt = " " + "  |  ".join(oneriler)
            mesaj_ekle(None, oneri_txt, "oneri")
        return "break"
    giris_text.bind("<Return>", mesaj_gonder)
    giris_text.bind("<Shift-Return>", lambda e: None)  # Shift+Enter yeni satır
    gonder_btn = tk.Button(alt_frame, text="➤ Gönder",
                            font=FONT_BTN, bg=tema["btn_bg"], fg=tema["btn_fg"],
                            relief=tk.FLAT, cursor="hand2", padx=12,
                            command=mesaj_gonder)
    gonder_btn.pack(side=tk.RIGHT, padx=(0, 10))
    tk.Label(alt_frame, text="Enter = gönder  |  Shift+Enter = yeni satır",
             font=("Consolas", 9), bg=tema["bg2"], fg=tema["fg2"]).pack(side=tk.BOTTOM, pady=2)
    root.mainloop()
#  MOD SEÇİMİ (Başlangıç)
def mod_secimi():
    """
    Program başlangıcında terminal veya GUI seçimi - Tamamen yeni fonksiyon.
    """
#--------------------------------------------------
###Yeni Banner

    print(f"""
{LIGHT_BLUE} ▄▄▄▄    ██▓     █    ██ ▓█████    ▓█████▓██   ██▓▓█████   ██████    
▓█████▄ ▓██▒     ██  ▓██▒▓█   ▀    ▓█   ▀ ▒██  ██▒▓█   ▀ ▒██    ▒    
▒██▒ ▄██▒██░    ▓██  ▒██░▒███      ▒███    ▒██ ██░▒███   ░ ▓██▄      
▒██░█▀  ▒██░    ▓▓█  ░██░▒▓█  ▄    ▒▓█  ▄  ░ ▐██▓░▒▓█  ▄   ▒   ██▒   
░▓█  ▀█▓░██████▒▒▒█████▓ ░▒████▒   ░▒████▒ ░ ██▒▓░░▒████▒▒██████▒▒   
░▒▓███▀▒░ ▒░▓  ░░▒▓▒ ▒ ▒ ░░ ▒░ ░   ░░ ▒░ ░  ██▒▒▒ ░░ ▒░ ░▒ ▒▓▒ ▒ ░   
▒░▒   ░ ░ ░ ▒  ░░░▒░ ░ ░  ░ ░  ░    ░ ░  ░▓██ ░▒░  ░ ░  ░░ ░▒  ░ ░   
 ░    ░   ░ ░    ░░░ ░ ░    ░         ░   ▒ ▒ ░░     ░   ░  ░  ░     
 ░          ░  ░   ░        ░  ░      ░  ░░ ░        ░  ░      ░     
      ░                                   ░ ░                      {ENDC}

  {BOLD}1.{ENDC}   Terminal Modu  {DIM}(CLI, syntax highlighting, tam komutlar){ENDC}
  {BOLD}2.{ENDC}    GUI Modu       {DIM}(Tkinter penceresi, dark/light tema){ENDC}
{DIM}Seçiminiz (1/2, varsayılan 1): {ENDC}""", end="")
    secim = input().strip()
    if secim == "2":
        print(f"{CYAN}GUI modu başlatılıyor...{ENDC}")
        gui_modu()
    else:
        terminal_modu()
#  BAŞLANGIÇ
if __name__ == "__main__":
    # Komut satırı argümanı ile direkt mod seçimi
    # python blue_eyes.py --gui    → direkt GUI
    # python blue_eyes.py --term   → direkt terminal
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--gui", "-g", "gui"]:
            gui_modu()
        elif arg in ["--term", "-t", "term", "--terminal"]:
            terminal_modu()
        else:
            mod_secimi()
    else:
        mod_secimi()
######################################################################################################
#!!!!
#Yeni karakter ayarı yapısı: 
#Karakter ayarına kendi karakter yapınızı 
#koyarak istediniz sekilde jailbreak (deneyebilmen için) yapabilmek
#için size özel o küçük alan kodun içine gömülen özel o alan evet senin için bunu okuyan kişi !!!!
#(Evet bunu düsündünü biliyorum bunu cidden yapabilir mi olur diye 
#düsünüyorsun birşey sana engel oluyor ondan kurtul mutlu olcaksın :) Aynı sen ve ben gibi :] ) !!!! 
#!!!!
KARAKTER_AYARI = ("""
""")
######################################################################################################
###sahip oldugu adı
KARAKTER_ADI = "BLUE EYES"
try:
    chat = client.chats.create(
        model="gemini-2.0-flash", 
        config=types.GenerateContentConfig(
            system_instruction=KARAKTER_AYARI # Burada tırnak olmamalı, değişken adı olmalı
        )
    )
except NameError:
    print("Hata: 'client' nesnesi oluşturulmamış. API anahtarınızı kontrol edin  ")
except Exception as e:
    print(f"Hata: Sohbet oturumu başlatılamadı   Detay: {e}")

def get_response(user_input):
    """Kullanıcı girdisine göre API'den cevap alır."""
    try:
        response = chat.send_message(user_input)
        if response and hasattr(response, 'text'):
            return response.text or "Üzgünüm, geçerli bir yanıt alınamadı."
        else:
            return "Üzgünüm, geçerli bir yanıt alınamadı."
    except Exception as e:
        return f"Üzgünüm, API'den bir hata oluştu: {e}"    
def get_multiline_input():
    """
    Çok satırlı metin girişi alır. 
    Kullanıcı END yazana kadar devam eder.
    Karakter sınırı yoktur!
    """
    print_with_typing_animation(" Uzun metin modu aktif! Metninizi yazın : ", 0.01)
    print_with_typing_animation(" Bitirmek için yeni satırda sadece 'END' yazıp Enter'a basın.", 0.01)
    print_with_typing_animation(" İstediğiniz kadar uzun yazabilirsiniz, sınır yok ! ", 0.01)
    print_with_typing_animation("-" * 50, 0.005)    
    lines = []
    line_count = 0    
    while True:
        try:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
            line_count += 1
        except EOFError:
            # Ctrl+D veya Ctrl+Z ile çıkış
            break    
    full_text = "\n".join(lines)    
    if full_text.strip():
        print_with_typing_animation(f"\n Toplam {line_count} satır, {len(full_text)} karakter alındı.", 0.01)    
    return full_text
def main():
    """Terminal arayüzünü çalıştırır."""
    display_ascii_art()
    print_with_typing_animation(f"--- {KARAKTER_ADI} 'a Hoş Geldin! ---", 0.01)
    ###karakter yapısı kısmı
    print_with_typing_animation("", 0.01)
    print_with_typing_animation("UZUN METİN MODU: '/uzun' veya '///' yazın (SINIR YOK ! )", 0.01)
    print_with_typing_animation("Normal mesaj için: Direkt yazıp Enter'a basın ", 0.01)
    print_with_typing_animation("Çıkmak için: 'çıkış' yazın ", 0.01)
    print_with_typing_animation("-" * 50, 0.005)
    while True:
        user_input = input("\nSen : ")
        if user_input.lower() in ["çıkış", "exit", "quit", "q"]:
            print_with_typing_animation(f"{KARAKTER_ADI}: Gene beklerim bay bay!", 0.01)
            break
        # Uzun metin modu kontrolü - Birden fazla trigger eklendi
        if user_input.lower() in ["/uzun", "/long", "///", "\"\"\"", "/multiline", "/m", "//", "/l"]:
            user_input = get_multiline_input()
            if not user_input.strip():
                print_with_typing_animation("Boş metin gönderilmedi. Tekrar deneyin ", 0.01)
                continue
            print_with_typing_animation(f"\nGönderiliyor..... ({len(user_input)} karakter)", 0.01)      
        # Boş mesaj kontrolü
        if not user_input.strip():
            print_with_typing_animation("Boş mesaj gönderilemez ", 0.01)
            continue
        assistant_answer = get_response(user_input)
        if assistant_answer is None:
            assistant_answer = "Şu anda yanıt veremiyorum. Lütfen tekrar dene."      
        print(f"\n{BLUE}{KARAKTER_ADI}: {ENDC}", end="")
        print_with_typing_animation(assistant_answer, 0.008)
if __name__ == "__main__":
    main()
