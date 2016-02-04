from newslist.sources import LeMondeNewsSource, DerStandardNewsSorce
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
        self.assertEqual(result[3], "http://derstandard.at/2000030115353/Maedchen-bei-Zentralmatura-in-Englisch-unerwartet-schlecht")
        self.assertEqual(result[5], "http://derstandard.at/2000030111049/Biogasanlagen-die-auch-Kompost-abwerfen")
        self.assertEqual(result[8], "http://derstandard.at/2000030113319/Matthias-Franz-Stein-Alle-Eltern-haben-ein-schlechtes-Gewissen")
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
