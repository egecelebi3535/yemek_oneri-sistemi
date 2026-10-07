from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


class Yemek:

    def __init__(self, isim, kategori, bolge, malzemeler, tarif, resim):
        self.isim = isim
        self.kategori = kategori
        self.bolge = bolge
        self.malzemeler = malzemeler
        self.tarif = tarif
        self.resim = resim

    def eslesen_malzemeler(self, kullanici_malzemeleri):

        eslesenler = []

        for kullanici_malzeme in kullanici_malzemeleri:

            for yemek_malzeme in self.malzemeler:

                if kullanici_malzeme.lower() in yemek_malzeme.lower():

                    if kullanici_malzeme not in eslesenler:
                        eslesenler.append(kullanici_malzeme)

                    break

        return eslesenler


def yemekleri_getir():

    yemekler = []

    for harf in "abcdefghijklmnopqrstuvwxyz":

        url = f"https://www.themealdb.com/api/json/v1/1/search.php?f={harf}"

        try:

            response = requests.get(
                url,
                timeout=10
            )

            if response.status_code != 200:
                continue

            # BeautifulSoup kullanıyoruz
            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            data = response.json()

            if data["meals"] is None:
                continue

            for yemek_data in data["meals"]:

                malzemeler = []

                for i in range(1, 21):

                    malzeme = yemek_data.get(
                        f"strIngredient{i}"
                    )

                    if malzeme:

                        malzeme = malzeme.strip()

                        if malzeme != "":
                            malzemeler.append(malzeme)

                yemek = Yemek(

                    isim=yemek_data["strMeal"],

                    kategori=yemek_data["strCategory"],

                    bolge=yemek_data["strArea"],

                    malzemeler=malzemeler,

                    tarif=yemek_data["strInstructions"],

                    resim=yemek_data["strMealThumb"]
                )

                yemekler.append(yemek)

        except Exception as hata:

            print(
                f"{harf.upper()} harfi alınırken hata:",
                hata
            )

    return yemekler


def yemekleri_bul(yemekler, kullanici_malzemeleri):

    sonuclar = []

    for yemek in yemekler:

        eslesenler = yemek.eslesen_malzemeler(
            kullanici_malzemeleri
        )

        if len(eslesenler) > 0:

            sonuclar.append(
                (yemek, eslesenler)
            )

    # En fazla eşleşen yemek en üstte
    sonuclar.sort(
        key=lambda x: len(x[1]),
        reverse=True
    )

    return sonuclar


@app.route("/", methods=["GET", "POST"])
def index():

    sonuclar = []

    girilen_malzemeler = ""

    if request.method == "POST":

        girilen_malzemeler = request.form.get(
            "malzemeler",
            ""
        )

        kullanici_malzemeleri = []

        for malzeme in girilen_malzemeler.split(","):

            malzeme = malzeme.strip().lower()

            if malzeme != "":
                kullanici_malzemeleri.append(malzeme)

        if len(kullanici_malzemeleri) > 0:

            print("\n⏳ Yemekler getiriliyor...")

            yemekler = yemekleri_getir()

            print(
                f"✅ {len(yemekler)} yemek getirildi."
            )

            print(
                "\n🔎 Malzemeler karşılaştırılıyor..."
            )

            sonuclar = yemekleri_bul(
                yemekler,
                kullanici_malzemeleri
            )

    return render_template(
        "index.html",
        sonuclar=sonuclar,
        girilen=girilen_malzemeler
    )


if __name__ == "__main__":
    app.run(debug=True)