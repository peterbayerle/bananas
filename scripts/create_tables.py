import sqlite3
import csv

cxn = sqlite3.connect("banana-dict.sqlite")
cur = cxn.cursor()

# create dicts table
cur.execute("drop table if exists dicts")
cur.execute("""\
CREATE TABLE dicts (
    dictid INTEGER primary key autoincrement,
    name text NOT NULL unique,
    description text,
    selected boolean NOT NULL
)
""")
cur.execute("""\
INSERT INTO dicts (name, description, selected)
VALUES
    (
        "NASPA Word List (2020)",
        "The official word reference for SCRABBLE played in the United States and Canada",
        true
    ),
    (
        "NASPA School Word List (2020)",
        "The official word list used in School SCRABBLE competitions",
        true
    )
""")

# create words table
cur.execute("drop table if exists words")
cur.execute("""\
create table words (
    word_friendly text,
    definition_friendly text,
    pos_friendly text,
    dictid integer,
    FOREIGN KEY(dictid) REFERENCES dicts(dictid)
)
""")

# insert words
for wl in ("nwl2020", ): #"nswl2020"):
    with open(f"./scripts/data/{wl}-preprocessed.csv") as f:
        contents = csv.reader(f)
        cols = next(contents)
        cur.executemany(
            f"insert into words ({', '.join(cols)}) values(?, ?, ?, ?)",
            contents,
        )

cxn.commit()
cxn.close()
