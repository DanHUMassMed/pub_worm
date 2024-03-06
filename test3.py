import pandas as pd
import json

# JSON data
json_data = [
    {
        "year": "2021",
        "journal": "Nat Commun",
        "title": "PDZD-8 and TEX-2 regulate endosomal PI(4,5)P 2 homeostasis via lipid transport to promote embryogenesis in C. elegans",
        "author": "Jeyasimman D|Ercan B|Dharmawan D|Naito T|Sun J|Saheki Y"
    },
    {
        "year": "2023",
        "journal": "PLoS Biol",
        "title": "The active zone protein Clarinet regulates synaptic sorting of ATG-9 and presynaptic autophagy.",
        "author": "Xuan Z|Yang S|Clark B|Hill SE|Manning L|Colon-Ramos DA"
    },
    {
        "year": "1980",
        "journal": "Genetics",
        "title": "The genetics of levamisole resistance in the nematode Caenorhabditis elegans.",
        "author": "Lewis JA|Wu CH|Berg H|Levine JH"
    },
    {
        "year": "2021",
        "journal": "International Worm Meeting",
        "title": "pOpsicle: An all-optical reporter system for synaptic vesicle recycling using pH-sensitive fluorescent proteins",
        "author": "Seidenthal, Marius|Janosi, Barbara|Zhao, Xhinda|Willoughby, Miles|Liewald, Jana F.|Ding, Jimmy|Peng, Lucinda|Lu, Hang|Gottschalk, Alexander"
    }
]

# Convert JSON to DataFrame
df = pd.DataFrame(json_data)

# Split the 'author' column by '|'
#df['author'] = df['author'].str.split('|')

# Explode the 'author' column to separate rows for each author
df = df.explode('author')

# Save DataFrame to CSV
df.to_csv('output.csv', index=False)
