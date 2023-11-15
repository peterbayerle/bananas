# Bananas! Scrabble word search and dictionary

**Bananas!** Is a Scrabble word search app for iPhone. The app includes the official NASPA Scrabble dictionary, the NASPA Word List (2020).

| Word Search | Retrieve Definitions |
| ----------- | ----------- |
|<img src="./static/rando.png">| <img src="./static/zoodle.png"> |

## Running the app
1. Download Zyzzyva definition text files from NASPA site, and put in `scripts/data` as `nwl_20.txt` and `nwl_23.txt` Then, run 
```bash
python3 ./scripts/preprocess_naspa_dicts.py
```
2. Move the resulting `.sqlite` file into `/Bananas/Bananas/Data`