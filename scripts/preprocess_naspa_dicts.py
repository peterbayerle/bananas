import pandas as pd
import json


def intake_df(file_path):
    with open(file_path, 'r') as f:
        data = f.read()

    defs = json.loads(data)

    return pd.DataFrame(
        defs["words"],
        columns=["word", "root", "pos", "num", "definition"]
    )


def partition(df):
    """
    Partition df into:
    1. Roots (records where "root" column is equal to the "word" column)
    2. Words with one root (records where "root" column in not equal to the
       "word" column, and where "root" column is associated with exactly one
       record in the database)
    3. Words with >1 roots (records where "root" column in not equal to the
       "word" column, and where "root" column is associated with >1
       record in the database)
    """
    # first, distinguish between roots and nonroots
    roots_idx = df['word'] == df['root']
    has_ref_idx = df["definition"].str.contains("<")

    df_roots = df[roots_idx & ~has_ref_idx]
    nonroots_idx = ~roots_idx | has_ref_idx

    assert df.shape[0] == df_roots.shape[0] + df[nonroots_idx].shape[0]

    # next, deal with roots that have a reference in their definition
    df.loc[roots_idx & has_ref_idx, "root"] = df.loc[roots_idx & has_ref_idx, "definition"].apply(lambda s: s.split(" ")[1].upper())
    new_roots = {row.word: row.root for row in df.loc[roots_idx & has_ref_idx, ["word", "root"]].itertuples()}

    # support 1 level of nesting
    for k, v in new_roots.items():
        if v in new_roots:
            new_roots[k] = new_roots[v]

    df.loc[nonroots_idx, "root"] = df.loc[nonroots_idx, "root"].apply(lambda r: new_roots.get(r, r))

    root_counts = (
        df_roots
        .groupby('word')
        .agg({'word': 'count'})
        .rename({'word': 'count'}, axis=1)
        .reset_index()
    )

    df_nonroots_merged = df[nonroots_idx].merge(
        root_counts,
        how="left",
        left_on='root',
        right_on='word',
        suffixes=('', '_root')
    )

    df_error = df_nonroots_merged.loc[df_nonroots_merged["count"].isna()]
    df_has_one_root = df_nonroots_merged[df_nonroots_merged['count'] == 1]
    df_has_many_roots = df_nonroots_merged[df_nonroots_merged['count'] > 1]

    df_roots = pd.concat((df_roots, df_error))

    c = df_roots.shape[0] + df_has_one_root.shape[0] + df_has_many_roots.shape[0]
    assert c == df.shape[0], df.shape[0] - c

    return df_roots, df_has_one_root, df_has_many_roots


def handle_roots(df_roots):
    def clean_def(s):
        if s == "a word or phrase preceded by the symbol # that categorizes the accompanying text":
          return s

        s = s.replace("*", "")
        s = s.replace("#", "")
        s = s.replace("{mdash}", "—")

        return s

    df_roots["definition_friendly"] = df_roots["definition"].apply(clean_def)

    return df_roots


def handle_single_root(df_has_one_root, df_roots):
    df_has_one_root = df_has_one_root.merge(
        df_roots[['word', 'definition_friendly', 'pos']],
        left_on='root',
        right_on='word',
        suffixes=('', '_friendly')
    )

    return df_has_one_root


def set_row_fields(row, matching):
    row['word'] = row["word"]
    row['definition_friendly'] = matching.iloc[0]["definition_friendly"]
    row['pos'] = matching.iloc[0]["pos"]


def handle_multiple_roots(df_has_many_roots, df_roots):
    def get_friendly(row):
        r = row['root']
        roots = df_roots[df_roots['word'] == r]
        num = row['num']

        if len(set(roots['pos'])) == 1:
            # If all have same POS, select the one with the matching num
            matching = roots[roots['num'] == num]

            if matching.shape[0] == 1:
                set_row_fields(row, matching)
                return row

        # else, there are multiple roots, and some have different POS
        pos_beginning = row['pos'].partition('_')[0]
        roots['pos_beginning'] = roots['pos'].apply(lambda s: s.partition('_')[0])

        roots_matching_pos = roots[roots['pos_beginning'] == pos_beginning]

        if roots_matching_pos.shape[0] == 1:
            # only one root has the matching pos, that must be it!
            set_row_fields(row, roots_matching_pos)
            return row

        # else, at least two roots have the same POS, so we go by number
        matching = roots_matching_pos[roots_matching_pos['num'] == num]

        if matching.shape[0] == 1:
            set_row_fields(row, matching)
            return row

        # we will try to pick one with a definition
        matching_with_def = matching[matching['definition'] != '']

        if matching_with_def.shape[0] > 0:
            set_row_fields(row, matching_with_def)
            return row

        # worst case scenario, just select any definition of the root, even if POS doesn't match
        matching = roots[roots.definition != '']
        if matching.shape[0] > 0:
            set_row_fields(row, matching)

        return row

    df_has_many_roots = df_has_many_roots.apply(get_friendly, axis=1)

    return df_has_many_roots


def transform(df):
    df_roots, df_has_one_root, df_has_many_roots = partition(df)

    df_roots = handle_roots(df_roots)
    df_has_one_root = handle_single_root(df_has_one_root, df_roots)
    df_has_many_roots = handle_multiple_roots(df_has_many_roots, df_roots)

    final = pd.concat(
        (df_roots, df_has_one_root, df_has_many_roots)
    ).reset_index(drop=True)

    # shared preprocessing
    final["word_friendly"] =  final["word"]
    final["pos_friendly"] =  final["pos"]

    final["word_friendly"] = final["word_friendly"].apply(lambda s: s.lower())
    final["pos_friendly"] = final["pos_friendly"].apply(lambda s: s.replace("_", " "))

    return final[["word_friendly", "definition_friendly", "pos_friendly"]]


if __name__ == "__main__":
    for idx, wl in enumerate(("nwl2020", "nswl2020")):
        naspa_json_path = f"./scripts/data/{wl}-defs.json"
        out_path = f"./scripts/data/{wl}-preprocessed.csv"

        df = intake_df(naspa_json_path)
        df = transform(df)
        df["dictid"] = idx+1

        df.to_csv(out_path, index=False)
