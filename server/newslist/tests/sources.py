from newslist.sources import LeMondeNewsSource, DerStandardNewsSorce, \
                             DiePresseNewsSource
import unittest


class TestSources(unittest.TestCase):

    def test_get_articles_lemonde(self):
        with open("newslist/fixtures/lemonde_index.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_articles(source)

        self.assertEqual(len(result), 12)
        self.assertEqual(result[0], "http://www.lemonde.fr/international/article/2016/02/01/la-belgique-a-des-difficultes-avec-le-fanatisme-mais-pas-plus-que-les-banlieues-francaises_4856969_3210.html")
        self.assertEqual(result[3], "http://www.lemonde.fr/europe/article/2016/01/27/polemiques-sur-les-risques-d-infiltration-par-des-djihadistes-des-sites-nucleaires-en-belgique_4854572_3214.html")
        self.assertEqual(result[5], "http://www.lemonde.fr/les-decodeurs/article/2016/02/01/primaire-democrate-aux-etats-unis-quand-et-comment-chaque-etat-vote-t-il_4857044_4355770.html")
        self.assertEqual(result[8], "http://www.lemonde.fr/ameriques/article/2016/01/30/la-colere-moteur-des-primaires-americaines_4856414_3222.html")
        self.assertEqual(result[11], "http://www.lemonde.fr/m-gastronomie/article/2016/02/01/michelin-trois-etoiles-pour-alain-ducasse-au-plaza-athenee-et-le-cinq_4857129_4497540.html")

    def test_get_article_lemonde_normal(self):
        with open("newslist/fixtures/lemonde_article_normal.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "")

        self.assertRegex(result.title, "^Charles Michel.*droit..$")
        self.assertEqual(result.image_url, "http://s2.lemde.fr/image/2016/02/01/534x0/4857146_4_214a_le-premier-ministre-belge-charles-michel-le-27_c269d14b5aaf17ab2c0d9c4a6999476b.jpg")
        self.assertRegex(result.summary, "^Les responsables.*du Monde.$")

    def test_get_article_lemonde_decodeurs(self):
        with open("newslist/fixtures/lemonde_article_decodeurs.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "")

        self.assertRegex(result.title, "^Les .*\xa0\\?")
        self.assertIsNone(result.image_url)
        self.assertRegex(result.summary, "^L.Iowa ouvre lundi.*en novembre.$")

    def test_get_article_lemonde_blog(self):
        with open("newslist/fixtures/lemonde_article_blog.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "")

        self.assertRegex(result.title, "^Pourquoi un requin en a.*oul$")
        self.assertEqual(result.image_url, "http://ecologie.blog.lemonde.fr/files/2016/01/01-29-sharkeatingshark-01-1024x660.jpg")
        self.assertRegex(result.summary, "^Vous avez.*lutte de territoire.$")

    def test_get_article_lemonde_video(self):
        with open("newslist/fixtures/lemonde_article_video.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "")

        self.assertRegex(result.title, "^Premiers secours.*qui sauvent$")
        self.assertIsNone(result.image_url)
        self.assertRegex(result.summary, "^Mettre en s.*des vies.$")

    def test_get_article_lemonde_paywall(self):
        with open("newslist/fixtures/lemonde_article_paywall.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "")

        self.assertRegex(result.title, "^La deuxi.me mort.*des attentats$")
        self.assertEqual(result.image_url, "http://s1.lemde.fr/image/2016/01/01/534x0/4840638_7_88c9_devant-le-restaurant-le-petit-cambodge-a_340b2fc82edc9f866d93da3d1debb028.jpg")
        self.assertRegex(result.summary, "^Lorsqu.on a.*en t.moigner.$")

    def test_get_article_lemonde_festival(self):
        with open("newslist/fixtures/lemonde_article_festival.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "")

        self.assertRegex(result.title, "^Benjamin.*ma.tres$")
        self.assertEqual(result.image_url, "http://s2.lemde.fr/image/2015/09/09/534x0/4750235_6_c816_benjamin-millepied-en-repetition-pour-la_3eb09811d4631d969115cfed5a5a5c33.jpg")
        self.assertRegex(result.summary, "^C.est quasiment.*grandi.$")

    def test_get_article_lemonde_afrique(self):
        with open("newslist/fixtures/lemonde_article_afrique.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = LeMondeNewsSource().get_article(source, "")

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
        result = DerStandardNewsSorce().get_article(source, "")

        self.assertRegex(result.title, "^M.dchen bei Zentralmatura.*schlecht$")
        self.assertEqual(result.image_url, "http://images.derstandard.at/t/12/2016/01/31/zentralmaturaArtikelbild.jpg")
        self.assertRegex(result.summary, "^Die Premiere.*Problemfall$")

    def test_get_article_derstandard_nosidebar(self):
        with open("newslist/fixtures/derstandard_article_nosidebar.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DerStandardNewsSorce().get_article(source, "")

        self.assertEqual(result.title, "Das Zika-Virus: Seit 70 Jahren kaum bekannt")
        self.assertEqual(result.image_url, "http://images.derstandard.at/2016/02/03/zika_1.jpg")
        self.assertRegex(result.summary, "^Die von.*epidemisch aus$")

    def test_get_article_derstandard_ansichtssache(self):
        with open("newslist/fixtures/derstandard_article_ansichtssache.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DerStandardNewsSorce().get_article(source, "")

        self.assertEqual(result.title, "Renault: RS16-Enthüllung in Paris")
        self.assertEqual(result.image_url, "http://images.derstandard.at/2016/02/03/a.jpg")
        self.assertRegex(result.summary, "^Neu formierter.*die Saison$")

    def test_get_article_derstandard_slides(self):
        with open("newslist/fixtures/derstandard_article_slides.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DerStandardNewsSorce().get_article(source, "")

        self.assertEqual(result.title, "Zum 90er der Spraydose: Die schönsten Streetart-Touren")
        self.assertEqual(result.image_url, "http://images.derstandard.at/t/E716/2016/02/01/Wien--3-Stunden-Polaroid-Fototour-durch-die-Stadt.jpg")
        self.assertRegex(result.summary, "^Als der.*sst. .red, 3.2.2016.$")

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
        result = DiePresseNewsSource().get_article(source, "")

        self.assertRegex(result.title, "^EU prophezeit.*mehr Arbeitslose$")
        self.assertEqual(result.image_url, "http://static.diepresse.com/images/uploads_580/d/5/2/4918610/533027A3-1218-4234-A7E4-54A31637CF0C_v0_h.jpg")
        self.assertRegex(result.summary, "^Laut EU-Winterprognose.*Arbeitslosenrate.$")

    def test_get_article_diepresse_galerie(self):
        with open("newslist/fixtures/diepresse_article_galerie.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DiePresseNewsSource().get_article(source, "")

        self.assertEqual(result.title, "ZTE Blade V6: Ein iPhone mit Haken")
        self.assertEqual(result.image_url, "http://static.diepresse.com/images/uploads_564/b/a/6/4918182/2_1454512771965620.jpg")
        self.assertRegex(result.summary, "^Sieht aus wie.*gro.en Haken.$")
    
    def test_get_article_diepresse_galerie2(self):
        with open("newslist/fixtures/diepresse_article_galerie2.html", "r", encoding="utf-8") as fp:
            source = fp.read()
        result = DiePresseNewsSource().get_article(source, "")

        self.assertEqual(result.title, "Die zehn reichsten Frauen der Weltgeschichte")
        self.assertEqual(result.image_url, "http://static.diepresse.com/images/uploads_620/a/0/7/4917767/A-woman-drinks-as-she-attends-the-Summer-Fair-in-Moscow_1454581261228828_v0_h.jpg")
        self.assertRegex(result.summary, "^Ob tot oder lebendig.*Epochen vertreten.$")
