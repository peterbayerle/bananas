import re
import sqlite3
from collections import defaultdict


def get_all_pos(f):
    pos = set()
    for line in f.readlines():
        _, _, rest = line.strip().partition(" ")
        messy_definitions = rest.split(" / ")
        for s in messy_definitions:
            pos.add(
                s[s.find("[")+1:s.find("]")].partition(" ")[0]
            ) 

    print(pos)


def clean_definition(messy_definition):
    # example messy_definition:
    # not {good=adj} [adj BADDER, BADDEST] : BADDISH [adj], BADLY [adv], BADNESS [n]

    # replace tokens like {good=adj} and <good=n> with good
    definition = re.sub(r"({|<)(\w+)=(\w*)(}|>)", r"\2", messy_definition).split("[")[0].strip()

    # remove list of related words
    pos = messy_definition.split("[")[1].split("]")[0].split(" ")[0]
    
    return f"{definition}:{pos}"


def add_words(f, col_name, words):
    for line in f.readlines():
        word, _, rest = line.strip().partition(" ")
        word = word.lower()
        messy_definitions = rest.split(" / ")

        words[word] = {
            **words[word],
            "word": word,
            "definitions": ";".join(clean_definition(messy_def) for messy_def in messy_definitions), 
            f"in_{col_name}": True,
        }



def create_tables_and_upload(words):
    cxn = sqlite3.connect("banana-dict.sqlite")
    cur = cxn.cursor()

    # create words table
    cur.execute("drop table if exists words")
    cur.execute("""\
    create table words (
        word text,
        in_nwl_23 integer,
        in_nwl_20 integer,
        definitions text
    );
    """)

    cur.executemany(
        """\
        insert into words (word, in_nwl_23, in_nwl_20, definitions)
        values (:word, :in_nwl_23, :in_nwl_20, :definitions);
        """,
        words.values(),
    )

    cxn.commit()
    cxn.close()


if __name__ == "__main__":
    dictionaries = ["nwl_20", "nwl_23"]
    words = defaultdict(lambda: {f"in_{name}": False for name in dictionaries})

    for name in dictionaries:
        with open(f"./scripts/data/{name}.txt") as f:
            add_words(f, name, words)

    # print(words.get("dumbphone"))
    # print(words.get("luving"))
    # print(words.get("goy"))

    create_tables_and_upload(words)

