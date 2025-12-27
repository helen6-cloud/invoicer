from . import views
from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from .views import (
    TitlesViewSet,
    AktorlerViewSet,
    login_view,
    ProfilViewSet,
    PuanViewSet,
    IzleneceklerListViewSet,
    IzlemeGecmisiViewSet,
    RegisterView,
    OneriListAPIView,
    get_random_titles,
    OzelListeViewSet,
    TitlesByGenreAPIView,
    KullaniciKayitView,
    FavoriViewSet,
    TurViewSet,
    search_titles,
    AramaGecmisiKayitAPIView,
    add_title_from_omdb
)

router = DefaultRouter()
router.register(r'titles', TitlesViewSet, basename='title')
router.register(r'aktorler', AktorlerViewSet, basename='aktorler')
router.register(r'profil', ProfilViewSet, basename='profil')
router.register(r'puanlar', PuanViewSet, basename='puanlar')
router.register(r'izlenecekler', IzleneceklerListViewSet, basename='izlenecekler')
router.register(r'izleme-gecmisi', IzlemeGecmisiViewSet, basename='izleme-gecmisi')
router.register(r'favoriler', FavoriViewSet, basename='favoriler')
router.register(r'turler', TurViewSet, basename='turler')
router.register(r'ozel-listeler', views.OzelListeViewSet, basename='ozel-listeler')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', login_view, name='login'),
    path('add-from-omdb/', add_title_from_omdb, name='add_from_omdb'),
    path('genres/<slug:genre_slug>/', TitlesByGenreAPIView.as_view(), name='titles-by-genre'),
    path('kayit/', KullaniciKayitView.as_view(), name='kayit'),
    path('log-interaction/', AramaGecmisiKayitAPIView.as_view(), name='log-interaction'),
    path('add-from-omdb/', add_title_from_omdb, name='add_from_omdb'),
    path("search/", search_titles),
    path('titles/random/', get_random_titles, name='random-titles'),
    path('titles-by-genre/', views.get_titles_by_genre, name='titles-by-genre'),
    path('onerilenler/', OneriListAPIView.as_view(), name='onerilenler'),
    path('add_title_from_omdb/', views.add_title_from_omdb, name='add_title_from_omdb'),

]
