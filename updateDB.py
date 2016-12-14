from dbUtils import *
import sqlite3
from createDB import createDB

def update(update=True):
    # if not update:
    db = sqlite3.connect('geoMetaData.db')

    db.text_factory = str

    ###GSEtoGSM, GSE table
    newGSEinfo  = updateTableGSE(db, update)
    GSEtable = set()
    for line in newGSEinfo:
        db.execute("insert into GSEtoGSM values(?, ?)", (line[0], line[1]))
        if line[0] not in GSEtable:
            db.execute("insert into GSE values(?, ?)", (line[0], line[2]))
            GSEtable.add(line[0])

    db.commit()

    newSamples = updateTableGSM(db, update)
    #### update GSM table

    for sample in newSamples.values():
        db.execute("insert into GSM values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (sample.id, sample.title, sample.organism, sample.SRA, sample.libraryStrategy, sample.platForm, sample.InstrumentID,
                    sample.antibody, sample.input, sample.control,
                    sample.cellType, sample.cellLine, sample.genoType, sample.treatment, sample.disease))

    db.commit()

    ### update GSMtoSRR table
    GSMtoSRR = updateGSMtoSRR(db, update, newSamples.keys())

    for gsmid, srr in GSMtoSRR.items():
        for s in srr:
            db.execute("insert into GSMtoSRR values(?, ?, ?, ?)", (gsmid, s[0], s[1], s[2]))

    db.commit()
    db.close()


if __name__ == "__main__":
    # update(True)
    db = sqlite3.connect('geoMetaData.db')

    db.text_factory = str

    GSMtoSRR = updateGSMtoSRR(db, update)

    for gsmid, srr in GSMtoSRR.items():
        for s in srr:
            db.execute("insert into GSMtoSRR values(?, ?, ?, ?)", (gsmid, s[0], s[1], s[2]))



    db.commit()
    db.close()