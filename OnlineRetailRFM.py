#Online Retail II - RFM

#Online Retail II isimli veri seti İngiltere merkezli bir perakende şirketinin 01/12/2009 - 09/12/2011 tarihleri
# arasındaki online satış işlemlerini içeriyor. Şirketin ürün kataloğunda hediyelik eşyalar yer almaktadır ve çoğu
# müşterisinin toptancı olduğu bilgisi mevcuttur.
#8 Değişken
# 541.909 Gözlem

#InvoiceNo : Fatura Numarası ( Eğer bu kod C ile başlıyorsa işlemin iptal edildiğini ifade eder )
#StockCode : Ürün kodu ( Her bir ürün için eşsiz )
#Description : Ürün ismi
#Quantity : Ürün adedi ( Faturalardaki ürünlerden kaçar tane satıldığı)
#InvoiceDate : Fatura tarihi
#UnitPrice : Fatura fiyatı ( Sterlin )
#CustomerID : Eşsiz müşteri numarası
#Country : Ülke ismi


import pandas as pd
import datetime as dt
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.width',1000)


#############   Görev 1: Veriyi Anlama ve Hazırlama   #############

# Adım 1: Online Retail II excelindeki 2010-2011 verisini okuyunuz. Oluşturduğunuz dataframe’in kopyasını oluşturunuz.
df_copy = pd.read_excel("online_retail_II.xlsx")

df = df_copy.copy()


#Adım 2: Veri setinin betimsel istatistiklerini inceleyiniz.

def check_df(dataframe):
    print("##################### Shape #####################")
    print(dataframe.shape)
    print("##################### Types #####################")
    print(dataframe.dtypes)
    print("##################### Head #####################")
    print(dataframe.head(3))
    print("##################### Tail #####################")
    print(dataframe.tail(3))
    print("##################### NA #####################")
    print(dataframe.isnull().sum())
    print("##################### Quantiles #####################")
    print(dataframe.describe().T)


check_df(df)


#Adım3: Veri setinde eksik gözlem var mı? Varsa hangi değişkende kaç tane eksik gözlem vardır?
df.isnull().sum()
df.isnull().sum().sum()


#Adım4: Eksik gözlemleri veri setinden çıkartınız. Çıkarma işleminde ‘inplace=True’ parametresini kullanınız.
df.dropna(inplace = True)


#Adım5: Eşsiz ürün sayısı kaçtır?
df["Description"].nunique()


#Adım6: Hangi üründen kaçar tane vardır?
df.groupby("Description").agg({"Quantity": "sum"}).head()


#Adım7: En çok sipariş edilen 5 ürünü çoktan aza doğru sıralayınız.
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()


#Adım 8: Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkartınız.
df = df[~df["Invoice"].str.contains("C", na=False)]


#Adım 9: Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturunuz
df["TotalPrice"] = df["Quantity"] * df["Price"]
df.head()



#############   Görev 2: RFM Metriklerinin Hesaplanması   #############
#Adım 1: Müşteri özelinde Recency, Frequency ve Monetary metriklerini groupby, agg ve lambda ile hesaplayınız.

#recency değeri için bugünün tarihini (2011, 12, 11) olarak kabul ediniz.

today_date = dt.datetime(2011,12,11)

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

#Adım 2: Oluşturduğunuz metriklerin isimlerini recency, frequency ve monetary olarak değiştiriniz.

rfm.columns = ['recency', 'frequency', 'monetary']

rfm.describe().T

rfm = rfm[rfm["monetary"] > 0]





#############   Görev 3: RFM Skorlarının Oluşturulması ve Tek bir Değişkene Çevrilmesi           #############
#Adım 1: Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz.

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])

rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])


#Adım 3: recency_score ve frequency_score’u tek bir değişken olarak ifade ediniz ve RFM_SCORE olarak kaydediniz.

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))




#############     Görev 4: RF Skorunun Segment Olarak Tanımlanması          #############
#Adım 1: Oluşturulan RFM skorları segmentlere çeviriniz.

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

rfm.head()

rfm[rfm["segment"] == "cant_loose"]