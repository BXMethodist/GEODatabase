# This module is used for download the SRRMetaData

import sqlite3
from dbUtils import downloadSRR

db = sqlite3.connect('geoMetaData.db')
db.text_factory = str

query = db.execute("select distinct GSM_ID, SRA from GSM")

print "fetching complete!"

gsmToSRR = []

for row in query.fetchall()[0:1000000]:
    GSM_ID, SRXlink = row

    if SRXlink is None or len(SRXlink.strip()) == 0:
        continue

    SRRids = downloadSRR(SRXlink)

    for id in SRRids:
        gsmToSRR.append((GSM_ID, id))
        print GSM_ID, "\t", id

db.close()

output = open("gsmToSRR.csv", "w")

for row in gsmToSRR:
    output.write(row[0]+"\t"+row[1]+"\n")

output.close()