import json
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from backend.api.models import Titles, Tur, BaslikTurleri, Aktorler
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'JSON dosyasından film ve dizi verilerini veritabanına yükler.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Veri yükleme işlemi başlatılıyor...'))

        file_path = 'data.json'

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"HATA: '{file_path}' dosyası bulunamadı."))
            return

        for item in data:
            try:
                # 1. Title (Başlık) Objesi Oluşturma
                title_slug = slugify(f"{item['title']}-{item['year']}")

                title_obj, created = Titles.objects.get_or_create(
                    slug=title_slug,
                    defaults={
                        'title_name': item['title'],
                        'cesit': item['tip'],
                        'yil': item['year'],
                        'ozet': item['overview'],
                        #'sure': item['suresi_int',0],
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"'{title_obj.title_name}' başarıyla oluşturuldu."))

                # 2. Türleri Bağlama
                for genre_name in item.get('genres', []):

                    genre_obj, _ = Tur.objects.get_or_create(
                        baslik=genre_name,
                    )
                    BaslikTurleri.objects.get_or_create(title=title_obj, tur=genre_obj)
                for actor_name in item.get('actors', []):
                    actor_obj, _ = Aktorler.objects.get_or_create(
                        isim=actor_name,
                        slug=slugify(actor_name)
                    )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"'{item['title']}' yüklenirken hata oluştu: {e}"))

        self.stdout.write(self.style.SUCCESS('Tüm veriler başarıyla yüklendi!'))
