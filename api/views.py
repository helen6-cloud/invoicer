from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from django.contrib.auth.models import User
from django.db.models import Q, Count,Avg, Prefetch
from rest_framework import viewsets, status, generics, serializers,permissions
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes,action
from django.contrib.auth import authenticate
from collections import Counter
from django.utils.text import slugify
import logging,requests

from .models import (
    Titles, Aktorler, Profil, Puan,OzelListe,
    IzleneceklerListesi, IzlemeGecmisi, Favori,Tur,AramaGecmisi,Sezon,Bolum,
)
from .serializers import (
    TitlesSerializer, AktorlerSerializer,OzelListeSerializer,
    ProfilSerializer, PuanSerializer, IzleneceklerListesiSerializer,
    IzlemeGecmisiSerializer, KullaniciKayitSerializer,TurSerializer,FavoriSerializer,AramaGecmisiSerializer
)
from .services.omdb import fetch_from_omdb, get_omdb_detail
logger = logging.getLogger(__name__)

OMDB_API_KEY = "36eb0f86"

def get_aktif_profil(user):
    if not user or user.is_anonymous:
        return None
    return Profil.objects.filter(user=user).first()

@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def get_random_titles(request):
    random_titles = Titles.objects.all().order_by('?')[:4]
    serializer = TitlesSerializer(random_titles, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    username_or_email = request.data.get("username")
    password = request.data.get("password")

    if not username_or_email or not password:
        return Response({"error": "Kullanıcı adı ve şifre gereklidir."}, status=400)

    user_obj = User.objects.filter(Q(email=username_or_email) | Q(username=username_or_email)).first()

    if user_obj:
        user = authenticate(username=user_obj.username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "username": user.username,
                "email": user.email
            }, status=200)

    return Response({"error": "Geçersiz kullanıcı adı veya şifre."}, status=401)


class TitlesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Titles.objects.prefetch_related('turler').all()
    serializer_class = TitlesSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cesit']

    def get_queryset(self):

        queryset = Titles.objects.prefetch_related('turler').all()
        cesit = self.request.query_params.get('cesit')
        grup = self.request.query_params.get('grup')
        kategori = self.request.query_params.get('kategori')
        if cesit:

            queryset = queryset.filter(cesit__icontains=cesit)
        if grup and grup != 'genel':
            queryset = queryset.filter(grup=grup)


        if kategori:
            queryset = queryset.filter(turler__baslik__iexact=kategori)


        queryset = queryset.exclude(poster_url='N/A').exclude(poster_url='')

        return queryset.distinct().order_by('-yil')

class ProfilViewSet(viewsets.ModelViewSet):
    serializer_class = ProfilSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Profil.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FavoriViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profil = get_aktif_profil(self.request.user)
        if profil:
            return Favori.objects.filter(profil=profil).order_by('-eklenme_tarihi')
        return Favori.objects.none()

    def perform_create(self, serializer):
        profil = get_aktif_profil(self.request.user)
        if not profil:
            raise serializers.ValidationError({"error": "Profil bulunamadı."})
        serializer.save(profil=profil)

class IzleneceklerListViewSet(viewsets.ModelViewSet):
    serializer_class = IzleneceklerListesiSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profil = get_aktif_profil(self.request.user)
        if profil:
            return IzleneceklerListesi.objects.filter(profil=profil)
        return IzleneceklerListesi.objects.none()

    def perform_create(self, serializer):

        profil = get_aktif_profil(self.request.user)
        serializer.save(profil=profil)

class RegisterView(generics.CreateAPIView):
    serializer_class = KullaniciKayitSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = serializer.save()
            # Profil otomatik oluşturuluyor
            Profil.objects.get_or_create(user=user, defaults={'profil_adi': f"{user.username}"})

            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "username": user.username,
                "message": "Kayıt başarılı."
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TurViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tur.objects.all().order_by('baslik')
    serializer_class = TurSerializer
    permission_classes = [AllowAny]


def register(request):
    data = request.data
    try:

        yeni_user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )


        Profil.objects.create(
            user=yeni_user,
            gender=data.get('gender')
        )
        token, _ = Token.objects.get_or_create(user=yeni_user)
        return Response({
            "message": "Kayıt başarılı",
            "token": token.key,
            "username": yeni_user.username
        }, status=status.HTTP_201_CREATED)

    except Exception as e:

        logger.error(f"Kayıt hatası: {str(e)}")
        return Response(
            {"error": f"Kayıt sırasında hata oluştu: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def search_titles(request):
    query = request.query_params.get('q', '').strip()
    titles = Titles.objects.filter(title_name__icontains=query)

    # --- Arama Geçmişini Kaydetme Kısmı ---
    if query and request.user.is_authenticated:
        profil = get_aktif_profil(request.user)
        if profil:

            eslesen_tur = Tur.objects.filter(baslik__icontains=query).first()

            AramaGecmisi.objects.create(
                profil=profil,
                aranan_metin=query,
                kategori=eslesen_tur
            )


    serializer = TitlesSerializer(titles, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_titles_by_genre(request):
    try:
        turler = Tur.objects.all()
        sonuc = []
        for tur in turler:

            titles = Titles.objects.filter(turler=tur).distinct()[:10]
            if titles.exists():
                serializer = TitlesSerializer(titles, many=True)
                sonuc.append({
                    "kategori_adi": tur.baslik,
                    "icerikler": serializer.data
                })
        return Response(sonuc)
    except Exception as e:

        print("Hata Detayı:", str(e))
        return Response({"error": str(e)}, status=500)

def fetch_from_omdb(title_name):
    api_key = "36eb0f86"
    url = f"http://www.omdbapi.com/?t={title_name}&apikey={OMDB_API_KEY}"
    try:

        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("Response") == "True":
            return {
                "title": data.get("Title"),
                "year": data.get("Year"),
                "plot": data.get("Plot"),
                "director": data.get("Director"),
                "actors": data.get("Actors"),
                "imdb_rating": data.get("imdbRating"),
                "metascore": data.get("Metascore"),
                "rotten_tomatoes": next((r['Value'] for r in data.get('Ratings', []) if r['Source'] == 'Rotten Tomatoes'), None),
                "poster_url": data.get("Poster"),
                "type": data.get("Type"),"genre_raw": data.get("Genre"), # TÜRLER İÇİN GEREKLİ
                "totalSeasons": data.get("totalSeasons")
            }
    except Exception as e:

        print(f"Bağlantı hatası ({title_name}): {e}")
        return None
    return None


def fetch_and_save(movie_title, api_key):
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    data = requests.get(url).json()

    if data.get('Response') == 'True':

        obj, created = Titles.objects.update_or_create(
            title_name=data.get('Title'),
            defaults={
                'yil': int(data.get('Year', 0).split('–')[0]) if data.get('Year') != 'N/A' else 0,
                'cesit': 'dizi' if data.get('Type') == 'series' else 'film',
                'imdb_rating': data.get('imdbRating', ''),
                'ozet': data.get('Plot', ''),
                'poster_url': data.get('Poster', '') if data.get('Poster') != 'N/A' else None,
            }
        )


        save_omdb_data(obj, data, api_key)
        print(f"Kayıt tamamlandı: {obj.title_name}")

def save_omdb_data(title_instance, omdb_data, api_key):

    # TÜRLERİ KAYDET VE BAĞLA
    genres_str = omdb_data.get('Genre', '')
    if genres_str and genres_str != 'N/A':
        genre_list = [g.strip() for g in genres_str.split(',')]
        for g_name in genre_list:
            tur_obj, _ = Tur.objects.get_or_create(baslik=g_name)
            title_instance.turler.add(tur_obj)

    # YÖNETMEN VE AKTÖRLERİ GÜNCELLE
    title_instance.yonetmen = omdb_data.get('Director', '')
    title_instance.aktorler = omdb_data.get('Actors', '')
    title_instance.save()  # Bu alanları kaydetmek için save() şart

    # SEZON VE BÖLÜM KAYDETME
    cesit = title_instance.cesit.lower()
    if cesit in ["dizi", "anime"]:
        total_seasons_raw = omdb_data.get('totalSeasons')

        if total_seasons_raw and total_seasons_raw != 'N/A':
            total_seasons = int(total_seasons_raw)
            imdb_id = omdb_data.get('imdbID')

            for s_num in range(1, total_seasons + 1):
                # Sezonu oluştur veya getir
                sezon_obj, _ = Sezon.objects.get_or_create(
                    title=title_instance,
                    sezon_no=s_num
                )

                # Sezon detaylarını OMDb'den çek
                s_url = f"http://www.omdbapi.com/?i={imdb_id}&Season={s_num}&apikey={api_key}"
                try:
                    s_res = requests.get(s_url).json()
                    if s_res.get('Response') == 'True':
                        for ep_data in s_res.get('Episodes', []):
                            try:
                                ep_num = int(ep_data.get('Episode'))
                                # Bölümü oluştur veya güncelle
                                Bolum.objects.update_or_create(
                                    sezon=sezon_obj,
                                    bolum_no=ep_num,
                                    defaults={
                                        'title': title_instance,
                                        'bolum_adi': ep_data.get('Title'),
                                        'air_date': ep_data.get('Released')
                                    }
                                )
                            except (ValueError, TypeError):
                                continue
                except Exception as e:
                    print(f"Sezon {s_num} verisi çekilirken hata oluştu: {e}")

    return title_instance

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request):
    title_id = request.data.get("title_id")
    profil = get_aktif_profil(request.user)

    try:
        title = Titles.objects.get(id=title_id)
        favori, created = Favori.objects.get_or_create(profil=profil, title=title)

        if not created:
            favori.delete()
            return Response({"status": "removed", "message": "Favorilerden çıkarıldı"})

        return Response({"status": "added", "message": "Favorilere eklendi"}, status=201)
    except Titles.DoesNotExist:
        return Response({"error": "Başlık bulunamadı"}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_as_watched(request):
    title_id = request.data.get("title_id")
    profil = get_aktif_profil(request.user)

    try:
        title = Titles.objects.get(id=title_id)
        # Eğer dizi ise son kaldığı bölümü de tutabiliriz ama şu an genel işaretleme yapıyoruz
        izleme, created = IzlemeGecmisi.objects.get_or_create(
            profil=profil,
            title=title,
            defaults={'tamamlandi': True}
        )

        if not created:
            izleme.tamamlandi = not izleme.tamamlandi
            izleme.save()

        return Response({
            "status": "success",
            "watched": izleme.tamamlandi,
            "message": "İzleme durumu güncellendi"
        })
    except Titles.DoesNotExist:
        return Response({"error": "İçerik bulunamadı"}, status=404)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_title_from_omdb(request):
    title_name = request.data.get("title")
    grup_bilgisi = request.data.get("grup")
    cesit_bilgisi = request.data.get("cesit")

    genre_mapping = {
        "Action": "Aksiyon", "Adventure": "Macera", "Animation": "Animasyon",
        "Biography": "Biyografi", "Comedy": "Komedi", "Crime": "Suç",
        "Documentary": "Belgesel", "Drama": "Dram", "Family": "Aile",
        "Fantasy": "Fantastik", "Film-Noir": "Kara Film", "History": "Tarih",
        "Horror": "Korku", "Music": "Müzik", "Musical": "Müzikal",
        "Mystery": "Gizem", "Romance": "Romantik", "Sci-Fi": "Bilim Kurgu",
        "Short": "Kısa Film", "Sport": "Spor", "Thriller": "Gerilim",
        "War": "Savaş", "Western": "Vahşi Batı"
    }

    target_slug = slugify(title_name.replace('ı', 'i').replace('ğ', 'g'))
    title = Titles.objects.filter(Q(title_name__iexact=title_name) | Q(slug=target_slug)).first()

    omdb_data = fetch_from_omdb(title_name)
    if not omdb_data:
        return Response({"error": "OMDb verisi bulunamadı"}, status=404)


    if not title:
        final_slug = slugify(omdb_data['title'].replace('ı', 'i'))
        raw_seasons = omdb_data.get('totalSeasons')
        sezon_say = int(raw_seasons) if raw_seasons and raw_seasons != 'N/A' else 1

        title = Titles.objects.create(
            slug=final_slug,
            title_name=omdb_data['title'],
            yil=int(omdb_data['year'][:4]) if omdb_data['year'] and omdb_data['year'] != 'N/A' else 0,
            ozet=omdb_data['plot'],
            cesit=cesit_bilgisi,
            grup=grup_bilgisi,
            poster_url=omdb_data['poster_url'],
            yonetmen=omdb_data['director'],
            aktorler=omdb_data['actors'],
            imdb_rating=omdb_data['imdb_rating'] if omdb_data['imdb_rating'] != 'N/A' else 0,
            sezon_sayisi=sezon_say if cesit_bilgisi in ['dizi', 'anime'] else None
        )
        msg = "Yeni içerik eklendi"
    else:
        title.grup = grup_bilgisi
        title.cesit = cesit_bilgisi
        title.yonetmen = omdb_data['director']
        title.aktorler = omdb_data['actors']
        try:
            val = omdb_data['imdb_rating']
            title.imdb_rating = float(val) if val != 'N/A' else 0
        except:
            pass
        title.save()
        msg = "Mevcut içerik güncellendi"


    raw_genres = omdb_data.get('genre_raw', '')
    if raw_genres and raw_genres != 'N/A':
        genres = [g.strip() for g in raw_genres.split(',')]
        for g_name in genres:
            tur_adi_tr = genre_mapping.get(g_name, g_name)
            tur_obj, _ = Tur.objects.get_or_create(baslik=tur_adi_tr)
            title.turler.add(tur_obj)


    if cesit_bilgisi in ['dizi', 'anime']:
        # OMDb ID'yi al (Bölümler için i=imdbID parametresi daha güvenlidir)
        full_detail = requests.get(f"http://www.omdbapi.com/?t={title_name}&apikey={OMDB_API_KEY}").json()
        imdb_id = full_detail.get('imdbID')
        total_seasons = int(full_detail.get('totalSeasons', 0)) if full_detail.get('totalSeasons') != 'N/A' else 0

        for s_idx in range(1, total_seasons + 1):
            sezon_obj, _ = Sezon.objects.get_or_create(title=title, sezon_no=s_idx)
            s_url = f"http://www.omdbapi.com/?i={imdb_id}&Season={s_idx}&apikey={OMDB_API_KEY}"
            s_res = requests.get(s_url).json()

            if s_res.get('Response') == 'True':
                for ep_data in s_res.get('Episodes', []):
                    Bolum.objects.get_or_create(
                        title=title,
                        sezon=sezon_obj,
                        bolum_no=int(ep_data.get('Episode')),
                        defaults={
                            'bolum_adi': ep_data.get('Title'),
                            'air_date': ep_data.get('Released')
                        }
                    )

    return Response({"message": msg}, status=200)

class KullaniciKayitView(generics.CreateAPIView):

    queryset = Profil.objects.all()
    serializer_class = KullaniciKayitSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Kullanıcı başarıyla kaydedildi.", "kullanici_adi": serializer.data['kullanici_adi']},
            status=status.HTTP_201_CREATED,
            headers=headers
        )


from rest_framework.decorators import action


class OzelListeViewSet(viewsets.ModelViewSet):
    serializer_class = OzelListeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profil = get_aktif_profil(self.request.user)
        return OzelListe.objects.filter(profil=profil)

    @action(detail=True, methods=['post'])
    def icerik_cikar(self, request, pk=None):
        ozel_liste = self.get_object()
        title_id = request.data.get('title_id')

        if not title_id:
            return Response({'error': 'title_id gönderilmedi.'}, status=400)
        if ozel_liste.icerikler.filter(id=title_id).exists():
            ozel_liste.icerikler.remove(title_id)
            return Response({'status': 'Icerik listeden cikarildi.'}, status=200)
        else:
            return Response({'error': 'Icerik bu listede bulunamadi.'}, status=404)


    def perform_create(self, serializer):
        profil = get_aktif_profil(self.request.user)
        serializer.save(profil=profil)

    @action(detail=True, methods=['post'], url_path='icerik_ekle')
    def icerik_ekle(self, request, pk=None):
        ozel_liste = self.get_object()
        title_id = request.data.get('title_id')
        liste = self.get_object()

        if not title_id:
            return Response({"error": "title_id alanı eksik"}, status=400)
        try:
            title = Titles.objects.get(id=title_id)
            liste.icerikler.add(title)
            return Response({"status": "İçerik listeye eklendi"}, status=status.HTTP_200_OK)
        except Titles.DoesNotExist:
            return Response({"error": "İçerik bulunamadı"}, status=status.HTTP_404_NOT_FOUND)

class TitlesFilter(django_filters.FilterSet):
    kategori = django_filters.CharFilter(
        field_name='turler__tur__baslik',
        lookup_expr='iexact'
    )
    cesit = django_filters.CharFilter(field_name='cesit', lookup_expr='iexact')

    class Meta:
        model = Titles
        fields = ['kategori', 'cesit']


class AktorlerViewSet(viewsets.ModelViewSet):

    queryset = Aktorler.objects.all()
    serializer_class = AktorlerSerializer


def get_aktif_profil(user):

    aktif_profil = Profil.objects.filter(user=user).first()
    if not aktif_profil:
        raise serializers.ValidationError({"hata": "Profil bulunamadı."})
    return aktif_profil


class PuanViewSet(viewsets.ModelViewSet):
    queryset = Puan.objects.all()
    serializer_class = PuanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Puan.objects.all()

        title_id = self.request.query_params.get('title')
        if title_id is not None:
            queryset = queryset.filter(title_id=title_id)
        return queryset

    def perform_create(self, serializer):

        aktif_profil = get_aktif_profil(self.request.user)

        title_obj = serializer.validated_data.get('title')
        rating_val = serializer.validated_data.get('rating_value')
        yorum_metni = serializer.validated_data.get('yorum', '')

        puan_obj, created = Puan.objects.update_or_create(
            profil=aktif_profil,
            title=title_obj,
            defaults={
                'rating_value': rating_val,
                'yorum': yorum_metni
            }
        )
        serializer.instance = puan_obj

class IzlemeGecmisiViewSet(viewsets.ModelViewSet):
    queryset = IzlemeGecmisi.objects.all()
    serializer_class = IzlemeGecmisiSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return IzlemeGecmisi.objects.filter(profil__user=self.request.user)
    def perform_create(self, serializer):
        aktif_profil = get_aktif_profil(self.request.user)
        serializer.save(profil=aktif_profil)


class OneriListAPIView(generics.ListAPIView):
    serializer_class = TitlesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        profil = get_aktif_profil(user)

        # 1. TEMEL VERİLERİ TOPLA
        izlenen_ids = IzlemeGecmisi.objects.filter(profil=profil).values_list('title_id', flat=True)
        favori_ids = Favori.objects.filter(profil=profil).values_list('title_id', flat=True)
        puanlananlar = Puan.objects.filter(profil=profil, rating_value__gte=7).values_list('title_id', flat=True)
        arama_tur_ids = AramaGecmisi.objects.filter(profil=profil).values_list('kategori_id', flat=True)

        # Önemli Başlıklar
        oncelikli_ids = set(list(favori_ids) + list(puanlananlar))

        # 2. İLGİ PUANLARI HESAPLA
        kategori_puan = Counter()
        aktor_listesi = []
        yonetmen_listesi = []


        etkilesimdeki_yapimlar = Titles.objects.filter(id__in=set(list(izlenen_ids) + list(oncelikli_ids)))

        for title in etkilesimdeki_yapimlar:
            # Kategorilere puan ver
            for tur in title.turler.all():
                kategori_puan[tur.id] += 5 if title.id in oncelikli_ids else 2


            if title.aktorler:
                aktor_listesi.extend([a.strip() for a in title.aktorler.split(',')])
            if title.yonetmen:
                yonetmen_listesi.extend([y.strip() for y in title.yonetmen.split(',')])


        for tur_id in arama_tur_ids:
            if tur_id: kategori_puan[tur_id] += 1


        top_tur_ids = [k[0] for k in kategori_puan.most_common(3)]
        top_aktorler = [a[0] for a in Counter(aktor_listesi).most_common(3)]
        top_yonetmenler = [y[0] for y in Counter(yonetmen_listesi).most_common(2)]


        oneri_sorgusu = Q()

        # Kategori benzerliği
        if top_tur_ids:
            oneri_sorgusu |= Q(turler__id__in=top_tur_ids)

        # Aktör benzerliği
        for aktor in top_aktorler:
            oneri_sorgusu |= Q(aktorler__icontains=aktor)

        # Yönetmen benzerliği
        for yonetmen in top_yonetmenler:
            oneri_sorgusu |= Q(yonetmen__icontains=yonetmen)

        # 4. FİLTRELE VE SIRALA

        return Titles.objects.filter(oneri_sorgusu) \
            .exclude(id__in=izlenen_ids) \
            .distinct() \
            .order_by('-imdb_rating', '?')[:24]


class TitlesByGenreAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = TitlesSerializer

    def get_queryset(self):
        genre_slug = self.kwargs['genre_slug']


        queryset = Titles.objects.filter(
            turler__baslik__slug=genre_slug
        ).distinct().order_by('-yil')

        return queryset

class AramaGecmisiKayitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        kategori_id = request.data.get('kategori_id')

        if not kategori_id:
            return Response({"error": "kategori_id gerekli."}, status=status.HTTP_400_BAD_REQUEST)

        try:

            aktif_profil = get_aktif_profil(request.user)


            kategori = Tur.objects.get(id=kategori_id)

            # 3. Kaydı oluştur
            AramaGecmisi.objects.create(
                profil=aktif_profil,
                kategori=kategori
            )

            return Response({"message": "Etkileşim kaydedildi."}, status=status.HTTP_201_CREATED)

        except Tur.DoesNotExist:
            return Response({"error": "Kategori bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def save_title(request):
    imdb_id = request.data.get("imdb_id")
    trailer_url = request.data.get("trailer_url", "")

    data = get_omdb_detail(imdb_id)

    title, created = Titles.objects.get_or_create(
        title=data["Title"],
        defaults={
            "year": data.get("Year"),
            "plot": data.get("Plot"),
            "poster": data.get("Poster"),
            "genre": data.get("Genre"),
            "imdb_rating": data.get("imdbRating"),
            "trailer_url": trailer_url,
        }
    )

    return Response({"created": created})