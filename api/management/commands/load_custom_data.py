from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.api import Titles

class Command(BaseCommand):
    help = 'Veritabanına kendi film ve dizi verilerimizi ekle'

    def handle(self, *args, **options):
        # Türkçe film ve dizileri içeren veri seti
        films_and_series = [
            # Türkçe Filmler
            {
                'title_name': 'Organize İşler',
                'cesit': 'Film',
                'ozet': 'Türkiye\'nin en popüler komedi filmi. Suç örgütünün üyeleri işleri "organize" etmeyi öğrenirler.',
                'yil': 2005,
                'sure': 110,
                'poster_url': 'https://via.placeholder.com/500x750?text=Organize+Isler',
                'fragman_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title_name': 'Organize İşler Sahneleri',
                'cesit': 'Film',
                'ozet': 'Organize İşler\'in devam filmiyedir.',
                'yil': 2007,
                'sure': 105,
                'poster_url': 'https://via.placeholder.com/500x750?text=Organize+Isler+2',
                'fragman_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title_name': '3 Aptal',
                'cesit': 'Film',
                'ozet': 'Üç arkadaşın komik maceraları.',
                'yil': 2004,
                'sure': 98,
                'poster_url': 'https://via.placeholder.com/500x750?text=3+Aptal',
                'fragman_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title_name': 'Çilgin Dersane',
                'cesit': 'Film',
                'ozet': 'Üniversite öğrencilerinin eğlenceli hikayesi.',
                'yil': 2007,
                'sure': 120,
                'poster_url': 'https://via.placeholder.com/500x750?text=Cilgin+Dersane',
                'fragman_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title_name': 'Recep İvedik',
                'cesit': 'Film',
                'ozet': 'Adana\'dan gelen bir insanın İstanbul maceraları.',
                'yil': 2008,
                'sure': 102,
                'poster_url': 'https://via.placeholder.com/500x750?text=Recep+Ivedik',
                'fragman_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title_name': 'Ezel',
                'cesit': 'Dizi',
                'ozet': 'Bir adamın cezaevinden çıkışından sonra intikam almaya çalışması hikayesi.',
                'yil': 2009,
                'sure': 45,
                'poster_url': 'https://via.placeholder.com/500x750?text=Ezel',
                'fragman_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title_name': 'Çukur',
                'cesit': 'Dizi',
                'ozet': 'Galata\'nın suç dünyasında geçen dramatik hikaye.',
                'yil': 2015,
                'sure': 45,
                'poster_url': 'https://via.placeholder.com/500x750?text=Cukur',
                'fragman_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title_name': 'Yasak Elma',
                'cesit': 'Dizi',
                'ozet': 'Ünlü bir ailenin sırlarıyla dolu dramı.',
                'yil': 2018,
                'sure': 45,
                'poster_url': 'https://via.placeholder.com/500x750?text=Yasak+Elma',
                'fragman_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title_name': 'Fatih Harbiye',
                'cesit': 'Dizi',
                'ozet': 'Aşk ve intrika dolu bir Istanbul hikayesi.',
                'yil': 2013,
                'sure': 45,
                'poster_url': 'https://via.placeholder.com/500x750?text=Fatih+Harbiye',
                'fragman_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            # Ek filmler
            {
                'title_name': 'Deli Deli Koşu',
                'cesit': 'Film',
                'ozet': 'Komik takip ve kaçış macerası.',
                'yil': 1990,
                'sure': 95,
                'poster_url': 'https://via.placeholder.com/500x750?text=Deli+Deli+Kosu',
                'fragman_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title_name': 'Neredesin Firuze',
                'cesit': 'Film',
                'ozet': 'Bir adamın sevdiği kadını bulmaya çalışması.',
                'yil': 2004,
                'sure': 112,
                'poster_url': 'https://via.placeholder.com/500x750?text=Neredesin+Firuze',
                'fragman_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title_name': 'Büyük Adam Küçük Aşk',
                'cesit': 'Film',
                'ozet': 'Yaş farkı olan iki insanın aşk hikayesi.',
                'yil': 2001,
                'sure': 100,
                'poster_url': 'https://via.placeholder.com/500x750?text=Buyuk+Adam+Kucuk+Ask',
                'fragman_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title_name': 'Ufak Tefek Cinayetler',
                'cesit': 'Dizi',
                'ozet': 'Orta sınıf bir ailenin gizemli cinayeti çözmeye çalışması.',
                'yil': 2017,
                'sure': 45,
                'poster_url': 'https://via.placeholder.com/500x750?text=Ufak+Tefek+Cinayetler',
                'fragman_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title_name': 'Kara Para Aşk',
                'cesit': 'Dizi',
                'ozet': 'Zengin bir adamla fakir bir kızın aşk hikayesi.',
                'yil': 2014,
                'sure': 45,
                'poster_url': 'https://via.placeholder.com/500x750?text=Kara+Para+Ask',
                'fragman_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title_name': 'Medcezir',
                'cesit': 'Dizi',
                'ozet': 'Genç öğrencilerin güzel lise okulu draması.',
                'yil': 2013,
                'sure': 45,
                'poster_url': 'https://via.placeholder.com/500x750?text=Medcezir',
                'fragman_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title_name': 'Süper Baba',
                'cesit': 'Dizi',
                'ozet': 'Bir babanın çocuklarıyla yaşadığı komik olaylar.',
                'yil': 2018,
                'sure': 45,
                'poster_url': 'https://via.placeholder.com/500x750?text=Super+Baba',
                'fragman_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
        ]

        added = 0
        skipped = 0

        for item in films_and_series:
            try:
                # Duplicate kontrol - başlık zaten var mı
                if Titles.objects.filter(title_name=item['title_name']).exists():
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  "{item["title_name"]}" zaten var, atlanıyor...')
                    )
                    skipped += 1
                    continue

                # Veri oluştur
                title = Titles.objects.create(
                    title_name=item['title_name'],
                    cesit=item['cesit'],
                    ozet=item['ozet'],
                    yil=item['yil'],
                    sure=item['sure'],
                    poster_url=item['poster_url'],
                    fragman_url=item['fragman_url'],
                    tmdb_id=None  # El ile eklenen veriler TMDB ID'si boş kalır
                )

                self.stdout.write(
                    self.style.SUCCESS(f'✅ Eklendi: {item["title_name"]} ({item["cesit"]})')
                )
                added += 1

            except IntegrityError:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  "{item["title_name"]}" zaten var')
                )
                skipped += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Hata "{item["title_name"]}": {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Başarılı: {added} eklendi, ⚠️ {skipped} atlandı'
            )
        )

