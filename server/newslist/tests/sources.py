from newslist.sources import LeMondeNewsSource, DerStandardNewsSorce, \
                             DiePresseNewsSource, SueddeutscheNewsSource
import unittest
import os


def _read_fixture(name):
    with open(os.path.join("newslist/fixtures", name), "r",
              encoding="utf-8") as fp:
        return fp.read()


class TestSources(unittest.TestCase):

    def test_get_articles_lemonde(self):
        source = _read_fixture("lemonde_index.html")
        result = LeMondeNewsSource().get_articles(source)

        self.assertEqual(len(result), 21)
        self.assertEqual(result[0], "http://www.lemonde.fr/international/article/2016/02/01/la-belgique-a-des-difficultes-avec-le-fanatisme-mais-pas-plus-que-les-banlieues-francaises_4856969_3210.html")
        self.assertEqual(result[3], "http://ecologie.blog.lemonde.fr/2016/02/01/pourquoi-un-requin-en-a-devore-un-autre-dans-un-aquarium-de-seoul/")
        self.assertEqual(result[5], "http://www.lemonde.fr/europe/article/2016/02/01/brexit-journee-decisive-de-negociations-entre-m-cameron-et-les-europeens_4857157_3214.html")
        self.assertEqual(result[8], "http://www.lemonde.fr/proche-orient/article/2016/02/01/a-geneve-des-discussions-s-amorcent-sur-le-volet-humanitaire-en-syrie_4857009_3218.html")
        self.assertEqual(result[20], "http://www.lemonde.fr/bande-dessinee/article/2016/01/31/festival-de-bd-d-angouleme-le-mea-culpa-de-l-auteur-du-canular_4856851_4420272.html")

    def test_get_article_lemonde_normal(self):
        with open("newslist/fixtures/lemonde_article_normal.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "http://lemonde.fr/")

        self.assertRegex(result.title, "^Charles Michel.*droit..$")
        self.assertEqual(result.image_url, "http://s2.lemde.fr/image/2016/02/01/534x0/4857146_4_214a_le-premier-ministre-belge-charles-michel-le-27_c269d14b5aaf17ab2c0d9c4a6999476b.jpg")
        self.assertRegex(result.summary, "^Les responsables.*du Monde.$")

    def test_get_article_lemonde_normal2(self):
        with open("newslist/fixtures/lemonde_article_normal2.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "http://bigbrowser.blog.lemonde.fr/2016/02/09/les-cinq-commandements-de-linternet/")

        self.assertEqual(result.title, "Les 5 commandements pour un Internet plus sûr")
        self.assertEqual(result.image_url, "http://bigbrowser.blog.lemonde.fr/files/2016/02/1212-530x267.png")
        self.assertRegex(result.summary, "^Mardi 9.*combats..$")

    def test_get_article_lemonde_normal3(self):
        with open("newslist/fixtures/lemonde_article_normal3.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "http://bigbrowser.blog.lemonde.fr/2016/02/09/les-cinq-commandements-de-linternet/")

        self.assertEqual(result.title, "Alain Juppé en position de force avant la primaire et la présidentielle")
        self.assertEqual(result.image_url, "http://s2.lemde.fr/image/2016/02/09/534x0/4861991_7_e152_2016-02-09-ea7d2bb-27904-1jlah20_10af72ca376a8904efbb1c955b6f3ae3.png")
        self.assertRegex(result.summary, "^L’enquête.*suivront.$")

    def test_get_article_lemonde_decodeurs(self):
        with open("newslist/fixtures/lemonde_article_decodeurs.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "http://lemonde.fr/")

        self.assertRegex(result.title, "^Les .*\xa0\\?")
        self.assertIsNone(result.image_url)
        self.assertRegex(result.summary, "^L.Iowa ouvre lundi.*en novembre.$")

    def test_get_article_lemonde_blog(self):
        with open("newslist/fixtures/lemonde_article_blog.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "http://lemonde.fr/")

        self.assertRegex(result.title, "^Pourquoi un requin en a.*oul$")
        self.assertEqual(result.image_url, "http://ecologie.blog.lemonde.fr/files/2016/01/01-29-sharkeatingshark-01-1024x660.jpg")
        self.assertRegex(result.summary, "^Vous avez.*lutte de territoire.$")

    def test_get_article_lemonde_blog_noimg(self):
        with open("newslist/fixtures/lemonde_article_blog_noimg.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "http://lemonde.fr/")

        self.assertRegex(result.title, "^D.ch.ance.*parole..$")
        self.assertIsNone(result.image_url)
        self.assertRegex(result.summary, "^Inscrire la.*apatride..$")

    def test_get_article_lemonde_video(self):
        with open("newslist/fixtures/lemonde_article_video.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "http://lemonde.fr/")

        self.assertRegex(result.title, "^Premiers secours.*qui sauvent$")
        self.assertIsNone(result.image_url)
        self.assertRegex(result.summary, "^Mettre en s.*des vies.$")

    def test_get_article_lemonde_paywall(self):
        with open("newslist/fixtures/lemonde_article_paywall.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "http://lemonde.fr/")

        self.assertRegex(result.title, "^La deuxi.me mort.*des attentats$")
        self.assertEqual(result.image_url, "http://s1.lemde.fr/image/2016/01/01/534x0/4840638_7_88c9_devant-le-restaurant-le-petit-cambodge-a_340b2fc82edc9f866d93da3d1debb028.jpg")
        self.assertRegex(result.summary, "^Lorsqu.on a.*en t.moigner.$")

    def test_get_article_lemonde_festival(self):
        with open("newslist/fixtures/lemonde_article_festival.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "http://lemonde.fr/")

        self.assertRegex(result.title, "^Benjamin.*ma.tres$")
        self.assertEqual(result.image_url, "http://s2.lemde.fr/image/2015/09/09/534x0/4750235_6_c816_benjamin-millepied-en-repetition-pour-la_3eb09811d4631d969115cfed5a5a5c33.jpg")
        self.assertRegex(result.summary, "^C.est quasiment.*grandi.$")

    def test_get_article_lemonde_afrique(self):
        with open("newslist/fixtures/lemonde_article_afrique.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "http://lemonde.fr/")

        self.assertRegex(result.title, "^Proc.s Gbagbo.*du juge$")
        self.assertEqual(result.image_url, "http://s2.lemde.fr/image/2016/02/04/768x0/4859284_6_d696_manifestation-a-abidjan-en-marge-de-la_8efe93e89910ada336c1586433368683.jpg")
        self.assertRegex(result.summary, "^..P547...parle.*r.publicaine.$")

    def test_get_articles_derstandard(self):
        with open("newslist/fixtures/derstandard_index.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DerStandardNewsSorce().get_articles(source)

        self.assertEqual(len(result), 24)
        self.assertEqual(result[0], "http://derstandard.at/2000030158047/Grossbritannien-erlaubt-Genmanipulation-von-Embryonen")
        self.assertEqual(result[2], "http://derstandard.at/2000030115353/Maedchen-bei-Zentralmatura-in-Englisch-unerwartet-schlecht")
        self.assertEqual(result[4], "http://derstandard.at/2000030111049/Biogasanlagen-die-auch-Kompost-abwerfen")
        self.assertEqual(result[7], "http://derstandard.at/2000030113319/Matthias-Franz-Stein-Alle-Eltern-haben-ein-schlechtes-Gewissen")
        self.assertEqual(result[23], "http://derstandard.at/2000029871110/Ernaehrung-Oesterreich-kommt-relativ-gut-wer")

    def test_get_article_derstandard_normal(self):
        with open("newslist/fixtures/derstandard_article_normal.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DerStandardNewsSorce().get_article(source, "http://derstandard.at/")

        self.assertRegex(result.title, "^M.dchen bei Zentralmatura.*schlecht$")
        self.assertEqual(result.image_url, "http://images.derstandard.at/t/12/2016/01/31/zentralmaturaArtikelbild.jpg")
        self.assertRegex(result.summary, "^Die Premiere.*Problemfall$")

    def test_get_article_derstandard_normal2(self):
        with open("newslist/fixtures/derstandard_article_normal2.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DerStandardNewsSorce().get_article(source, "http://derstandard.at/2000030602066/New-Hampshire-als-Feuerprobe-fuer-Donald-Trump")

        self.assertEqual(result.title, "New Hampshire als Feuerprobe für Trump")
        self.assertEqual(result.image_url, "http://images.derstandard.at/t/E400/2016/02/08/trumphaha.jpg")
        self.assertRegex(result.summary, "^Immobilientycoon.*Marco Rubio$")

    def test_get_article_derstandard_nosidebar(self):
        with open("newslist/fixtures/derstandard_article_nosidebar.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DerStandardNewsSorce().get_article(source, "http://derstandard.at/")

        self.assertEqual(result.title, "Das Zika-Virus: Seit 70 Jahren kaum bekannt")
        self.assertEqual(result.image_url, "http://images.derstandard.at/2016/02/03/zika_1.jpg")
        self.assertRegex(result.summary, "^Die von.*epidemisch aus$")

    def test_get_article_derstandard_ansichtssache(self):
        with open("newslist/fixtures/derstandard_article_ansichtssache.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DerStandardNewsSorce().get_article(source, "http://derstandard.at/")

        self.assertEqual(result.title, "Renault: RS16-Enthüllung in Paris")
        self.assertEqual(result.image_url, "http://images.derstandard.at/2016/02/03/a.jpg")
        self.assertRegex(result.summary, "^Neu formierter.*die Saison$")

    def test_get_article_derstandard_slides(self):
        with open("newslist/fixtures/derstandard_article_slides.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DerStandardNewsSorce().get_article(source, "http://derstandard.at/")

        self.assertEqual(result.title, "Zum 90er der Spraydose: Die schönsten Streetart-Touren")
        self.assertEqual(result.image_url, "http://images.derstandard.at/t/E716/2016/02/01/Wien--3-Stunden-Polaroid-Fototour-durch-die-Stadt.jpg")
        self.assertRegex(result.summary, "^Als der.*sst. .red, 3.2.2016.$")

    def test_get_article_derstandard_live(self):
        with open("newslist/fixtures/derstandard_article_live.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DerStandardNewsSorce().get_article(source, "http://derstandard.at/")

        self.assertEqual(result.title, "Heute Abend: Wir schauen Opernball!")
        self.assertIsNone(result.image_url)
        self.assertRegex(result.summary, "^Sehen und.*Sie durch den Abend$")

    def test_get_article_derstandard_live(self):
        with open("newslist/fixtures/derstandard_article_space.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DerStandardNewsSorce().get_article(source, "http://derstandard.at/2000030454375/Ich-wollte-meinen-Kindern-zeigen-dass-sich-Kaempfen-lohnt")

        self.assertEqual(result.title, "\"Ich wollte meinen Kindern zeigen, dass sich Kämpfen lohnt\"")
        self.assertEqual(result.image_url, "http://images.derstandard.at/t/E2000/2016/02/09/zaun2000.jpg")
        self.assertRegex(result.summary, "^Am liebsten.*Erfahrung.$")

    def test_get_articles_diepresse(self):
        with open("newslist/fixtures/diepresse_index.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DiePresseNewsSource().get_articles(source)

        self.assertEqual(len(result), 35)
        self.assertEqual(result[0], "http://diepresse.com/home/wirtschaft/economist/4918610/EU-prophezeit-Osterreich-noch-mehr-Arbeitslose")
        self.assertEqual(result[1], "http://diepresse.com/home/politik/aussenpolitik/4918522/Islamisten-planten-offenbar-Anschlag-am-Alexanderplatz")
        self.assertEqual(result[3], "http://diepresse.com/home/wirtschaft/economist/4918807/Glucksspiel_CasinosBieter-wollen-Krieg-beenden")
        self.assertEqual(result[5], "http://diepresse.com/home/politik/innenpolitik/4918547/RathgeberProzess_Mir-sind-in-der-Zeitnot-Fehler-passiert")
        self.assertEqual(result[8], "http://diepresse.com/home/meinung/kommentare/leitartikel/4918278/Die-Feinde-des-Bargelds-sind-auf-dem-falschen-Dampfer")
        self.assertEqual(result[34], "http://diepresse.com/home/panorama/welt/105316/Blickfang_Die-besten-Bilder-aus-aller-Welt")

    def test_get_article_diepresse_normal(self):
        with open("newslist/fixtures/diepresse_article_normal.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DiePresseNewsSource().get_article(source, "http://diepresse.com/")

        self.assertRegex(result.title, "^EU prophezeit.*mehr Arbeitslose$")
        self.assertEqual(result.image_url, "http://static.diepresse.com/images/uploads_580/d/5/2/4918610/533027A3-1218-4234-A7E4-54A31637CF0C_v0_h.jpg")
        self.assertRegex(result.summary, "^Laut EU-Winterprognose.*Arbeitslosenrate.$")

    def test_get_article_diepresse_galerie(self):
        with open("newslist/fixtures/diepresse_article_galerie.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DiePresseNewsSource().get_article(source, "http://diepresse.com/")

        self.assertEqual(result.title, "ZTE Blade V6: Ein iPhone mit Haken")
        self.assertEqual(result.image_url, "http://static.diepresse.com/images/uploads_564/b/a/6/4918182/2_1454512771965620.jpg")
        self.assertRegex(result.summary, "^Sieht aus wie.*gro.en Haken.$")

    def test_get_article_diepresse_galerie2(self):
        with open("newslist/fixtures/diepresse_article_galerie2.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DiePresseNewsSource().get_article(source, "http://diepresse.com/")

        self.assertEqual(result.title, "Die zehn reichsten Frauen der Weltgeschichte")
        self.assertEqual(result.image_url, "http://static.diepresse.com/images/uploads_620/a/0/7/4917767/A-woman-drinks-as-she-attends-the-Summer-Fair-in-Moscow_1454581261228828_v0_h.jpg")
        self.assertRegex(result.summary, "^Ob tot oder lebendig.*Epochen vertreten.$")
    
    def test_get_article_diepresse_galerie3(self):
        with open("newslist/fixtures/diepresse_article_galerie3.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DiePresseNewsSource().get_article(source, "http://immobilien.diepresse.com/home/4921362/Modell_Wie-der-Schwedenplatz-kunftig-aussehen-konnte")

        self.assertRegex(result.title, "^Modell: Wie der.*aussehen k.nnte$")
        self.assertEqual(result.image_url, "http://immobilien.diepresse.com/images/uploads_600/8/1/2/4921362/Schweden1_1454934867185881.jpg")
        self.assertRegex(result.summary, "^Die Neugestaltung.*Wahl genommen.$")

    def test_get_article_diepresse_quiz(self):
        with open("newslist/fixtures/diepresse_article_quiz.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DiePresseNewsSource().get_article(source, "http://diepresse.com/home/kultur/film/oscar/4909162/index")

        self.assertEqual(result.title, "Oscar 2016")
        self.assertEqual(result.image_url, "http://diepresse.com/images/uploads/8/6/a/4909162/Actor-DiCaprio-poses-as-he-arrives-for-the-British-premiere-of-The-Revenant-in-London-Britain_1453382553722379.jpg")
        self.assertEqual(result.summary, "Film-Quiz: Wie heißt diese Oscar-Nominierte?")

    def test_get_article_diepresse_thema(self):
        with open("newslist/fixtures/diepresse_article_thema.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DiePresseNewsSource().get_article(source, "http://immobilien.diepresse.com/home/4921362/Modell_Wie-der-Schwedenplatz-kunftig-aussehen-konnte")

        self.assertEqual(result.title, "Börseblitz")
        self.assertEqual(result.image_url, "http://static.diepresse.com/images/uploads_300/a/b/4/4922036/atx_1455016899418842.jpg")
        self.assertRegex(result.summary, "^Somit hinkte.*Richtung fanden.$")

    def test_get_articles_sueddeutsche(self):
        with open("newslist/fixtures/sueddeutsche_index.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = SueddeutscheNewsSource().get_articles(source)

        self.assertEqual(len(result), 14)
        self.assertEqual(result[0], "http://www.sueddeutsche.de/panorama/nordrhein-westfalen-im-raster-1.2849393")
        self.assertEqual(result[2], "http://www.sueddeutsche.de/politik/alltag-im-buergerkrieg-wie-syrische-kinder-die-luftangriffe-erleben-1.2850789")
        self.assertEqual(result[4], "http://www.sueddeutsche.de/politik/wikileaks-julian-assange-in-der-blackbox-der-menschenrechte-1.2851168")
        self.assertEqual(result[7], "http://www.sueddeutsche.de/geld/trendwende-goldflimmern-1.2848837")
        self.assertEqual(result[-1], "http://www.sueddeutsche.de/leben/eternal-rules-of-nightclubbing-so-wird-das-vorgluehen-noch-besser-als-die-party-1.2850930")
    
    def test_get_article_sueddeutsche_normal(self):
        with open("newslist/fixtures/sueddeutsche_article_normal.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = SueddeutscheNewsSource().get_article(source, "http://www.sueddeutsche.de/")

        self.assertRegex(result.title, "^Festnahmen: Polizei.*Attentat$")
        self.assertEqual(result.image_url, "http://polpix.sueddeutsche.com/polopoly_fs/1.2850232.1454606934!/httpImage/image.jpg_gen/derivatives/300x168/image.jpg")
        self.assertRegex(result.summary, "^Nach bundesweiten.*Sicherheitskreise.$")

    def test_get_article_sueddeutsche_noimg(self):
        with open("newslist/fixtures/sueddeutsche_article_noimg.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = SueddeutscheNewsSource().get_article(source, "http://www.sueddeutsche.de/")

        self.assertRegex(result.title, "^VW verschiebt.*Hauptversammlung$")
        self.assertIsNone(result.image_url)
        self.assertRegex(result.summary, "^Das Unternehmen.* nach.$")

    def test_get_article_sueddeutsche_gallery(self):
        with open("newslist/fixtures/sueddeutsche_article_gallery.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = SueddeutscheNewsSource().get_article(source, "http://www.sueddeutsche.de/")

        self.assertEqual(result.title, "Transfermarkt: China erstaunt die Fußballwelt")
        self.assertEqual(result.image_url, "http://polpix.sueddeutsche.com/polopoly_fs/1.2850573.1454667310!/httpImage/image.jpg_gen/derivatives/900x600/image.jpg")
        self.assertRegex(result.summary, "^Alex Teixeira.*.Überblick.$")
   
    def test_get_article_sueddeutsche_quiz(self):
        with open("newslist/fixtures/sueddeutsche_article_quiz.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = SueddeutscheNewsSource().get_article(source, "http://quiz.sueddeutsche.de/quiz/1df4a0211b9280f8f824b135e68e6d22-reisequiz-der-woche--amsterdam")

        self.assertEqual(result.title, "Reisequiz der Woche: Amsterdam")
        self.assertEqual(result.image_url, "http://quiz.sueddeutsche.de/upload/9964/7666/Tulpen_Reuters_560.jpg")
        self.assertRegex(result.summary, "^Gibt es.*sieben Fragen.$")
