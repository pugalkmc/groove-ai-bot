from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb+srv://pugalkmc:pugalkmc@cluster0.dzcnjxc.mongodb.net/")
db = client['telegram_bot']
warnings_col = db['warnings']
mutes_col = db['mutes']