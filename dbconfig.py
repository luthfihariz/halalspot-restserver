from pymongo import Connection

#MongoDB Connection
MONGOHQ_URL= "mongodb://admin:luthfi329245@oceanic.mongohq.com:10082/HalalSpot"

conn = Connection(MONGOHQ_URL)
db = conn['HalalSpot']