import unittest
from preprocess_naspa_dicts import intake_df, transform
import sys


class TestPreprocessNaspa(unittest.TestCase):
    def setUp(self):
        naspa_json_path = "./scripts/data/nwl2020-defs.json"
        self.df = intake_df(naspa_json_path)

    def test_bat(self):
        """
        Input:
               word root                 pos  num         definition
        13354   BAT  BAT        verb_present    1  to hit a baseball
        13443  BATS  BAT  verb_present_third    1              < BAT

        This input consists of a root (BAT) and a word with 1 root (BATS).
        So, in the final output, we expect the definition of bats to be the same as bat
        """
        df = self.df[self.df["word"].isin(["BAT", "BATS"])]
        df = transform(df)
        self.assertEqual(df.iloc[0].definition_friendly, df.iloc[1].definition_friendly)

    def test_beat(self):
        """
        Input:
                 word  root                   pos  num            definition
        13795    BEAT  BEAT             verb_past    1
        13796    BEAT  BEAT          verb_present    1  to strike repeatedly
        13806  BEATEN  BEAT  verb_past_participle    1                < BEAT

        This input consists of a root (BEAT, verb_present) and a word with 2 roots (BEATEN)
        The word with the non-empty definition is preferred
        """
        df = self.df[self.df["word"].isin(["BEAT", "BEATEN"])]
        df = transform(df)

        self.assertEqual(df[df["word_friendly"]=="beaten"].iloc[0].definition_friendly, "to strike repeatedly")

    def test_agora(self):
        """
        Input:
                 word   root            pos  num                       definition
        3084    AGORA  AGORA  noun_singular    1  a marketplace in ancient Greece
        3085    AGORA  AGORA  noun_singular    2        a monetary unit of Israel
        3086   AGORAE  AGORA    noun_plural    1                          < AGORA
        3093   AGORAS  AGORA    noun_plural    1                          < AGORA
        3094   AGOROT  AGORA    noun_plural    1
        3095   AGOROT  AGORA    noun_plural    2                          < AGORA
        3096  AGOROTH  AGORA    noun_plural    1
        3097  AGOROTH  AGORA    noun_plural    2                          < AGORA

        This input consists of two roots (AGORA, 1) and (AGORA, 2)
        Some words map to root 1, others to root 2
        """
        df = self.df[self.df["word"].isin(['AGORA', 'AGORAE', 'AGORAS', 'AGOROT', 'AGOROTH'])]
        df = transform(df)

        self.assertEqual(set(df[df["word_friendly"] == "agoroth"].definition_friendly), {"a marketplace in ancient Greece", "a monetary unit of Israel"})
        self.assertEqual(set(df[df["word_friendly"] == "agorot"].definition_friendly), {"a marketplace in ancient Greece", "a monetary unit of Israel"})
        self.assertEqual(df[df["word_friendly"] == "agoras"].iloc[0].definition_friendly, "a marketplace in ancient Greece")
        self.assertEqual(df[df["word_friendly"] == "agorae"].iloc[0].definition_friendly, "a marketplace in ancient Greece")

    def test_know(self):
        """
        Input:

                  word     root                   pos  num                                    definition
        90917     KNOW     KNOW          verb_present    1               to have a true understanding of
        90921  KNOWING     KNOW           verb_gerund    1                                        < KNOW
        90922  KNOWING  KNOWING    adjective_positive    1                                        astute
        90923  KNOWING  KNOWING         noun_singular    1                                     knowledge
        90934    KNOWN     KNOW             verb_past    1
        90935    KNOWN     KNOW  verb_past_participle    1                                        < KNOW
        90936    KNOWN    KNOWN         noun_singular    1  a mathematical quantity whose value is given

        Several identical words have different definitions
        """
        df = self.df[self.df["word"].isin(['KNOW', "KNOWING", "KNOWN"])]
        df = transform(df)

        self.assertEqual(df[df.word_friendly=="know"].iloc[0].definition_friendly, "to have a true understanding of")
        self.assertEqual(set(df[df.word_friendly=="knowing"].definition_friendly), {"knowledge", "astute", "to have a true understanding of"})
        self.assertEqual(set(df[df.word_friendly=="known"].definition_friendly), {"to have a true understanding of", "a mathematical quantity whose value is given"})

    def test_weird_defs(self):
        """
        Input:
                     word        root            pos  num                                         definition
        12069   BAHUVRIHI   BAHUVRIHI  noun_singular    1    a possessive, exocentric#, grammatical compound
        22991  CALAMANDER  CALAMANDER  noun_singular    1     the ebony wood of the Disopyros quaesita* tree
        74989     HASHTAG     HASHTAG  noun_singular    1  a word or phrase preceded by the symbol # that...

        Inputs have strange definitions. For example, they have valid hashtags (eg, in the definition of hashtag) and invalid chars like *
        and #, which generally denote if a word in a definition is a valid NASPA word or not
        """
        df = self.df[self.df["word"].isin(["CALAMANDER", "VELCRO", "BAHUVRIHI", "HASHTAG"])]
        df = transform(df)

        self.assertFalse("*" in df[df.word_friendly=="calamander"].iloc[0].definition_friendly)
        self.assertFalse("#" in df[df.word_friendly=="bahuvrihi"].iloc[0].definition_friendly)
        self.assertTrue("#" in df[df.word_friendly=="hashtag"].iloc[0].definition_friendly)

    def test_pouringly(self):
        """
        Input:

                     word       root              pos  num        definition
        130283       POUR       POUR     verb_present    1  to cause to flow
        130291  POURINGLY  POURINGLY  adverb_positive    1            < POUR
        """
        df = self.df[self.df["word"].isin(["POUR", "POURINGLY"])]
        df = transform(df)

        self.assertEqual(df[df["word_friendly"]=="pouringly"].iloc[0].definition_friendly, "to cause to flow")

    def test_adoptive(self):
        """
                      word        root  ... num           definition
        1642      ADAPTION    ADAPTION  ...   1  the act of adapting
        1644      ADAPTIVE    ADAPTIVE  ...   1         < ADAPTION n
        1648  ADAPTIVITIES  ADAPTIVITY  ...   1
        1649    ADAPTIVITY  ADAPTIVITY  ...   1           < ADAPTIVE

        Here, adaptivities -> adaptivity -> adaptive -> adaption
        """
        df = self.df[self.df["word"].isin(["ADAPTIVITIES", "ADAPTIVITY", "ADAPTIVE", "ADAPTION"])]
        df = transform(df)

        self.assertEqual(df[df["word_friendly"]=="adaptivities"].iloc[0].definition_friendly, "the act of adapting")

if __name__ == '__main__':
    unittest.main()
