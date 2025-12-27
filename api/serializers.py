from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Avg
from .models import (
 Tur,Titles, Aktorler, Yonetmen, BaslikAktorler, BaslikYonetmenler,OzelListe,
    Profil, Puan, IzleneceklerListesi, IzlemeGecmisi,AramaGecmisi, Favori
)

User = get_user_model()

class TurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tur
        fields = ['id','baslik']

class PuanSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    title_name = serializers.ReadOnlyField(source='title.title_name')

    class Meta:
        model = Puan
        fields = ['id', 'user_name', 'title', 'title_name', 'rating_value', 'yorum', 'yorum_saati']

    def get_user_name(self, obj):
        # Puan modelinde 'profil' üzerinden kullanıcıya gidiyoruz
        try:
            return obj.profil.user.username
        except:
            return "Kullanıcı"
class BaslikAktorlerSerializer(serializers.ModelSerializer):
    aktor_adi = serializers.ReadOnlyField(source='aktor.aktor_adi')
    class Meta:
        model = BaslikAktorler
        fields = ['aktor_adi','rol_adi']

class BaslikYonetmenlerSerializer(serializers.ModelSerializer):

    yonetmen_adi = serializers.ReadOnlyField(source='yonetmen.yonetmen_adi')
    class Meta:
        model = BaslikYonetmenler
        fields = ['yonetmen_adi']

class CustomerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BaslikYonetmenler
        fields = ['yonetmen']


class TitlesSerializer(serializers.ModelSerializer):

    turler = TurSerializer(many=True, read_only=True)
    poster = serializers.SerializerMethodField()
    ortalama_puan = serializers.SerializerMethodField()
    sezon_sayisi = serializers.SerializerMethodField()
    yorumlar = PuanSerializer(many=True, read_only=True, source='puan_set')
    aktorler_listesi = BaslikAktorlerSerializer(
        source='baslikaktorler_set',
        many=True,
        read_only=True
    )
    yonetmenler_listesi = BaslikYonetmenlerSerializer(
        source='baslikyonetmenler_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Titles
        fields = '__all__'

    def get_sezon_sayisi(self, obj):
        # HATA BURADAYDI: Models.py'da related_name='sezon_listesi' demiştin
        if obj.cesit in ['dizi', 'anime']:
            return obj.sezon_listesi.count()
        return 0

    def get_ortalama_puan(self, obj):
        try:
            res = obj.puan_set.aggregate(Avg('rating_value'))['rating_value__avg']
            return round(res, 1) if res else 0
        except:
            return 0

    def get_poster(self, obj):
        if obj.poster_image:
            return obj.poster_image.url
        return obj.poster_url if obj.poster_url else None


class ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profil
        fields = '__all__'

class AktorlerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aktorler
        fields = '__all__'

class YonetmenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Yonetmen
        fields = '__all__'


class KullaniciKayitSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=6, required=True)
    password2 = serializers.CharField(write_only=True, min_length=6, required=True)
    gender = serializers.CharField(required=False, allow_blank=True, default='O')

    def validate(self, data):
        if data.get("password") != data.get("password2"):
            raise serializers.ValidationError({"password": "Şifreler eşleşmiyor."})

        if User.objects.filter(username=data.get("username")).exists():
            raise serializers.ValidationError({"username": "Bu kullanıcı adı zaten alınmış."})

        if User.objects.filter(email=data.get("email")).exists():
            raise serializers.ValidationError({"email": "Bu e-posta adresi zaten kullanımda."})
        return data

    def create(self, validated_data):
        with transaction.atomic():

            password = validated_data.pop("password")
            validated_data.pop("password2", None)


            user = User.objects.create_user(
                username=validated_data.get("username"),
                email=validated_data.get("email"),
                password=password
            )
            return user

class IzleneceklerListesiSerializer(serializers.ModelSerializer):
    title_name = serializers.CharField(source='title.title_name', read_only=True)
    title_details = TitlesSerializer(source='title', read_only=True)
    class Meta:
        model = IzleneceklerListesi
        fields = ['id', 'title', 'title_name', 'title_details', 'eklenme_tarihi', 'completed']
        extra_kwargs = {'profil': {'read_only': True}}

class IzlemeGecmisiSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = IzlemeGecmisi
        fields = ['id', 'bolum', 'title', 'izlenme_zamani', 'izlenilen_saniye']
        read_only_fields = ['profil']
class AramaGecmisiSerializer(serializers.ModelSerializer):
    class Meta:
        model = AramaGecmisi
        fields = ['id', 'kategori', 'tarih']
        read_only_fields = ['id', 'tarih']

class SimpleTitleSerializer(serializers.ModelSerializer):
    poster = serializers.SerializerMethodField()
    class Meta:
        model = Titles
        fields = ['id', 'title_name', 'yil', 'poster','slug','ozet','cesit']

    def get_poster(self, obj):
        if obj.poster_image: return obj.poster_image.url
        return obj.poster_url

class OzelListeSerializer(serializers.ModelSerializer):
    title_count = serializers.IntegerField(source='icerikler.count', read_only=True)
    icerikler_detay = SimpleTitleSerializer(source='icerikler', many=True, read_only=True)
    class Meta:
        model = OzelListe
        fields = ['id', 'isim', 'title_count', 'olusturulma_tarihi','icerikler_detay']

class FavoriSerializer(serializers.ModelSerializer):
    title_name = serializers.CharField(source="title.title_name", read_only=True)
    title_details = SimpleTitleSerializer(source='title', read_only=True)
    poster = serializers.SerializerMethodField()
    cesit = serializers.CharField(source="title.cesit", read_only=True)
    yil = serializers.IntegerField(source="title.yil", read_only=True)
    ozet = serializers.CharField(source="title.ozet", read_only=True)

    class Meta:
        model = Favori
        fields = ["id", "profil", "title", 'title_name', "title_details", "poster", "cesit", "yil", "ozet",
                  "eklenme_tarihi"]
        read_only_fields = ["profil"]

    def get_poster(self, obj):
        try:
            if obj.title.poster_image:
                return obj.title.poster_image.url
        except:
            pass
        return obj.title.poster_url if obj.title.poster_url else None



