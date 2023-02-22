# Bananas! Scrabble word search and dictionary

**Bananas!** Is a Scrabble word search app for iPhone. The app includes the official NASPA Scrabble dictionary, the NASPA Word List (2020).

| Word Search | Retrieve Definitions |
| ----------- | ----------- |
|<img src="./static/knowing.png">| <img src="./static/knowing-def.png"> |

## Running the app
1. Download JSON word list from NASPA site, and put in `scripts/data`. Then, run 
```bash
bash scripts/build_db.sh
```
2. Insert resulting `.sqlite` file into `Bananas/Bananas/Data`