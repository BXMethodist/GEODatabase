# This module is used for download the SRRMetaData

import sqlite3
from dbUtils import downloadSRR

db = sqlite3.connect('geoMetaData.db')
db.text_factory = str

for row in db.execute("select distinct SRA from GSM").fetchall():
    SRXlink = row[0]
    if SRXlink is None or len(SRXlink.strip()) == 0:
        continue

    downloadSRR(SRXlink)