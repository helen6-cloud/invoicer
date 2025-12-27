from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator


class Titles(models.Model):
    CESIT_CHOICES = [('film', 'Film'), ('dizi', 'Dizi'),('anime', 'Anime')]
    cesit = models.CharField(max_length=10, choices=CESIT_CHOICES)
    title_name = models.CharField(max_length=255, verbose_name="Başlık Adı")
    yil = models.IntegerField()
    sezon_sayisi = models.IntegerField(default=1, null=True, blank=True)
    bolum_sayisi = models.IntegerField(default=0, null=True, blank=True)
    sure = models.IntegerField(null=True, blank=True, help_text="Film süresi (dakika)")
    ozet = models.TextField(blank=True)
    turler = models.ManyToManyField('Tur', through='BaslikTurleri', related_name='titles')
    yonetmen = models.CharField(max_length=255, blank=True, null=True)
    aktorler = models.TextField(blank=True, null=True)
    imdb_rating = models.CharField(max_length=10, blank=True, null=True)
    metascore = models.CharField(max_length=10, null=True, blank=True)
    rotten_tomatoes = models.CharField(max_length=10, null=True, blank=True)
    GRUP_CHOICES = [
        ('genel', 'Genel (Global)'),
        ('turk', 'Türk Yapımı'),
        ('anime', 'Anime'),
        ('kore', 'Kore Dizisi (K-Drama)'),
    ]
    grup = models.CharField(
        max_length=20,
        choices=GRUP_CHOICES,
        default='genel',
        verbose_name="İçerik Grubu"
    )

    def __str__(self):
        return self.title_name
    fragman_url = models.URLField(max_length=500, blank=True, null=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=255)
    poster_url = models.URLField(
    max_length=500, blank=True, null=True, help_text="Poster resim URL'i")
    poster_image = models.ImageField(
        upload_to='posters/',
        null=True,
        blank=True,
        help_text="Poster resmi (dosya olarak)"
    )

    @property
    def sure_saat_cinsinden(self):
        if self.cesit == 'film' and self.sure:
            saat = self.sure // 60
            dakika = self.sure % 60
            return f"{saat}s {dakika}dk"
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title_name)
        super().save(*args, **kwargs)

    def get_poster(self):

        if self.poster_image:
            return self.poster_image.url
        return None

    def __str__(self):
        return self.title_name

    class Meta:
        verbose_name_plural = "Başlıklar (Filmler/Diziler)"


class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    gender = models.CharField(max_length=10, null=True, blank=True)
    profil_adi = models.CharField(max_length=200)
    olus_tarihi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profili"

class Tur(models.Model):
    baslik = models.CharField(max_length=105, unique=True)

    def __str__(self):
        return self.baslik
    class Meta:
        verbose_name = "Tür"
        verbose_name_plural = "Türler"



class BaslikTurleri(models.Model):
    title = models.ForeignKey(Titles, on_delete=models.CASCADE)
    tur = models.ForeignKey('Tur', on_delete=models.CASCADE)
    class Meta:
        unique_together = ('title', 'tur')

    def __str__(self):
        return f"{self.title.title_name} - {self.tur.baslik}"


class Aktorler(models.Model):
    aktor_adi = models.CharField(max_length=200)
    dogum_tarihi = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.aktor_adi


class BaslikAktorler(models.Model):
    title = models.ForeignKey(Titles, on_delete=models.CASCADE)
    aktor = models.ForeignKey(Aktorler, on_delete=models.CASCADE)
    rol_adi = models.CharField(max_length=199)
    
    class Meta:
        unique_together = ('title', 'aktor')
        verbose_name_plural = "Başlık Aktörleri"

class Yonetmen(models.Model):
    yonetmen_adi = models.CharField(max_length=200)

    def __str__(self):
        return self.yonetmen_adi


class BaslikYonetmenler(models.Model):
    title = models.ForeignKey(Titles, on_delete=models.CASCADE)
    yonetmen = models.ForeignKey('Yonetmen', on_delete=models.CASCADE)
    
    
    class Meta:
        unique_together = ('title', 'yonetmen')


class Puan(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE)
    title = models.ForeignKey(Titles, on_delete=models.CASCADE)
    rating_value = models.DecimalField(max_digits=3, decimal_places=1)
    yorum = models.TextField(blank=True)
    yorum_saati = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('profil', 'title')
        verbose_name_plural = "Puanlar"

class IzleneceklerListesi(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE)
    title = models.ForeignKey(Titles, on_delete=models.CASCADE)
    eklenme_tarihi = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('profil', 'title')
        verbose_name_plural = "İzlenecekler Listeleri"

class Etiketler(models.Model): 
    
    tag_adi = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tag_adi

    class Meta:
        verbose_name_plural = "Etiketler"

class TitleEtiketler(models.Model):
    title = models.ForeignKey(Titles, on_delete=models.CASCADE)
    tag = models.ForeignKey(Etiketler, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('title', 'tag')

class KullaniciTercihleri(models.Model):
   
    kullanici = models.ForeignKey(Profil, on_delete=models.CASCADE)
    tercih_key = models.CharField(max_length=200)
    tercih_value = models.CharField(max_length=200)
    
    class Meta:

        unique_together = ('kullanici', 'tercih_key')
        verbose_name_plural = "Kullanıcı Tercihleri"

class Favori(models.Model):
    profil = models.ForeignKey(
        Profil,
        on_delete=models.CASCADE,
        related_name="favoriler"
    )
    title = models.ForeignKey(
        Titles,
        on_delete=models.CASCADE,
        related_name="favorilenenler"
    )
    eklenme_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profil', 'title')
        verbose_name_plural = "Favoriler"

    def __str__(self):
        return f"{self.profil.profil_adi} ❤️ {self.title.title_name}"

class AramaGecmisi(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name="arama_gecmisi")
    kategori = models.ForeignKey(Tur, on_delete=models.CASCADE, null=True, blank=True)
    aranan_metin = models.CharField(max_length=255, null=True, blank=True)
    tarih = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Arama Geçmişleri ve Tıklama Geçmişleri"

class Fragman(models.Model):
    title = models.OneToOneField(
        Titles,
        on_delete=models.CASCADE,
        related_name="fragman"
    )
    youtube_url = models.URLField()

    def __str__(self):
        return f"{self.title.title_name} Fragman"

class Sezon(models.Model):
    title = models.ForeignKey(Titles, on_delete=models.CASCADE, related_name='sezon_listesi')
    sezon_no = models.IntegerField(default=1)

    class Meta:
        unique_together = ('title', 'sezon_no')
        verbose_name_plural = "Sezonlar"

    def __str__(self):
        return f"{self.title.title_name} - Sezon {self.sezon_no}"

class Bolum(models.Model):

        title = models.ForeignKey(Titles, on_delete=models.CASCADE, related_name="tum_bolumler")
        sezon = models.ForeignKey(Sezon, on_delete=models.CASCADE, related_name="bolumler")
        bolum_no = models.IntegerField()
        bolum_adi = models.CharField(max_length=255, null=True, blank=True)
        bolum_sure = models.IntegerField(null=True, blank=True, help_text="dakika")
        ozet = models.TextField(null=True, blank=True)
        air_date = models.CharField(max_length=50, null=True, blank=True)

        class Meta:
            unique_together = ('sezon', 'bolum_no')
            verbose_name_plural = "Bölümler"

        def __str__(self):
            return f"{self.title.title_name} - S{self.sezon.sezon_no}E{self.bolum_no}"

class OzelListe(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='ozel_listelerim')
    isim = models.CharField(max_length=100)
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)

    icerikler = models.ManyToManyField(Titles, blank=True, related_name='bulundugu_listeler')

    def __str__(self):
        return f"{self.isim} - {self.profil.user.username}"

class IzlemeGecmisi(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE)

    bolum = models.ForeignKey(Bolum, on_delete=models.CASCADE, null=True, blank=True)
    title = models.ForeignKey(Titles, on_delete=models.CASCADE)
    izlenme_zamani = models.DateTimeField(auto_now_add=True)
    izlenilen_saniye = models.IntegerField(default=0)
    tamamlandi = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "İzleme Geçmişleri"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(user=instance, profil_adi=instance.username)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profil'):
        instance.profil.save()