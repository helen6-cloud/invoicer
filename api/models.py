from django.db import models

#---------------------
#Müşteri Tablosu
#--------------------
class Customer(models.Model): # Müşteri Bilgilerini Tutuyor
    name = models.CharField(max_length=200) #Müşterinin adı
    email = models.EmailField(blank=True, null=True) #E-Posta
    phone = models.CharField(max_length=50, blank=True) #Telefon
    address = models.TextField(blank=True) #Adres

    def __str__(self): #str admin panelde gösterilecek isim
        return self.name #admin panelde görünür isim

   #Ürün Tablosu
   #blank=true, null=true alan boş bırakılabilir

class Product(models.Model): #Ürün Bilgileri:adı, açıklaması, fiyatı
    name = models.CharField(max_length=200) #Ürün adı
    description = models.TextField(blank=True) #Açıklama
    price = models.DecimalField(max_digits=12, decimal_places=2) #Fiyat
        #decimalField: Para Değerleri için 
    def __str__(self):
        return self.name

#--------------
#Fatura Tablosu
#--------------  
class Invoice(models.Model): #Fatura: hangi müşteri, fatura tarihi, ödeme tarihi, notlar
    #fatura sadece bir müşteriye ait
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices')
    #Hangi müşteri için fatura silinirse fatura da silinir
    date=models.DateField(auto_now_add=True) #Fatura tarihi otomatik eklenir
    due_date=models.DateField(blank=True, null=True) #Ödeme tarihi
    notes = models.TextField(blank=True) #notlar

    def total(self):
        #Bu faturadaki tüm hepsinin toplamı
        return sum([item.total_price() for item in self.items.all()])

    def __str__(self):
         return f"INV-{self.id} - {self.customer.name}"

#-----------------
 # Fatura Tablosu
 #----------------
class InvoiceItem(models.Model):
    invoice=models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT) # hangi faturaya ait, fatura silinirse kalemde silinir
    quantity = models.PositiveIntegerField(default=1) #Miktar -Ürün silinirse kalem silinmez, Protectle koruyoruz
    unit_price= models.DecimalField(max_digits=12, decimal_places=2) #Birim fiyat

    def total_price(self): #bu kalemin toplam fiyatı
        return self.quantity * self.unit_price

    def total_price(self): # bu kalemin toplam fiyatı
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"



