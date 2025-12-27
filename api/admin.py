from django.contrib import admin
# Veri Tabanı Modellerini içe aktarır
from .models import (
     Titles, Profil, Bolum,
    Aktorler, Yonetmen, Puan, IzleneceklerListesi,
    IzlemeGecmisi,Tur,Favori,BaslikTurleri, Sezon
)
from .services.omdb import fetch_from_omdb

#Titles modeline bağlı türler için inline admin ayarı
class TurInline(admin.TabularInline):
    model = BaslikTurleri
    extra = 1

#Diziler için sezonların film dizi ekleme ekranında göstermek için
class SezonInline(admin.TabularInline):
    model = Sezon
    extra = 1

#titles modelini admine kaydeder
@admin.register(Titles)
class TitlesAdmin(admin.ModelAdmin):
    #sütun olarak gösterilecek alanlar
    list_display = ('title_name', 'cesit', 'yil', 'bilgi_ozeti', 'has_fragman','grup','get_sezon_sayisi')
    # düzenlenebilir alanlar forma girmeden değiştirilebilir
    list_editable = ('grup', 'cesit')
    #sağ tarafa filtreleme paneli ekler
    list_filter = ('cesit', 'yil','grup','turler')
    #arama çubuğu film/dizi adına göre
    search_fields = ('title_name',)
    #toplu işlem menüsü bu fonksiyonlar burda tanımlı değil
    actions = ['delete_tmdb_titles', 'delete_manual_titles']

    #film dizi eklerken tür ve sezonları aynı sayfada eklenmeyi sağlar
    inlines = [TurInline, SezonInline]
    #admin komutunu bölümlere ayır
    fieldsets = (
        (None, {
            'fields': ('title_name', 'cesit', 'yil')
        }),
        #sadece film için geçerli ayarlar js ile dizi seçilince gizlenir
        ('Film Ayarları', {
            'fields': ('sure',),
            'classes': ('field-film-group',),
        }),
        ('Görsel ve Fragman', {
            'fields': ('poster_url', 'poster_image', 'fragman_url'),
        }),

    )

#admin paneline özel js ekler
    class Media:
        js = ('admin/js/title_toggle.js',) #film seçince süre, dizi seçince sezon göster
#film ise süre, dizi ise kaç sezon
    def bilgi_ozeti(self, obj):
        if obj.cesit in ['dizi', 'anime']:
            return f"{obj.sezon_listesi.count()} Sezon"
        return "Film"
# fragman linki var mı yok mu kontrol eder
    def has_fragman(self, obj):
        return bool(obj.fragman_url)

    has_fragman.boolean = True
    has_fragman.short_description = 'Fragman ✓'

    def get_sezon_sayisi(self, obj):
        # Related name 'sezon_listesi' olduğu için:
        return obj.sezon_listesi.count()

    get_sezon_sayisi.short_description = "Sezon Sayısı"

#türleri yönetmek için admin ayarı
@admin.register(Tur)
class TurAdmin(admin.ModelAdmin):
    #tür ıd ve ad listelenir
    list_display = ('id', 'baslik')
    #tür adına göre arama yapılır
    search_fields = ('baslik',)
#admin kayıtları özel ayar yapılmadan varysaılan admin paneline kaydeder
admin.site.register(Profil)
admin.site.register(Bolum)
admin.site.register(Aktorler)
admin.site.register(Yonetmen)
admin.site.register(Puan)
admin.site.register(IzleneceklerListesi)
admin.site.register(IzlemeGecmisi)
admin.site.register(Favori)
#