# This module is to create a sqlite database

import sqlite3

def createDB():
    db = sqlite3.connect('geoMetaData.db')

    db.execute('drop table if exists GSEtoGSM')
    db.execute('drop table if exists GSM')
    db.execute('drop table if exists GSE')
    db.execute('drop table if exists GSMtoSRR')
    # db.execute('drop table if exists H3K4me3')
    # db.execute('drop table if exists H3K27ac')
    # db.execute('drop table if exists H3K27me3')
    # db.execute('drop table if exists H3K36me3')
    # db.execute('drop table if exists H3K4me1')
    # db.execute('drop table if exists H3K4me2')
    # db.execute('drop table if exists H3K79me2')
    # db.execute('drop table if exists H3K9ac')
    # db.execute('drop table if exists H3K9me1')
    # db.execute('drop table if exists H3K9me3')
    # db.execute('drop table if exists H4K20me1')
    ###


#TO DO: update column name GSM
    db.execute('create table GSEtoGSM(GSE_ID text, GSM_ID text)')
    db.execute("CREATE INDEX index_GSEtoGSM1 ON GSEtoGSM (GSM_ID);")

    # sample.id, sample.title, sample.organism, sample.SRA, sample.libraryStrategy, sample.platForm, sample.InstrumentID,
    # sample.antibody, sample.input, sample.control,
    # sample.cellType, sample.cellLine, sample.genoType, sample.treatment, sample.disease


    db.execute('create table GSM(GSM_ID text, title text, organism text, SRA text, Library_Strategy text, Platform_ID text,InstrumentID text, antibody, input text, control text,cell_type text, cell_line text, geno_type text, treatment text, disease text)')
    db.execute("CREATE INDEX index_GSM1 ON GSM (GSM_ID);")

    db.execute('create table GSE(GSE_ID text, organization text)')
    db.execute("CREATE INDEX index_GSE1 ON GSE (GSE_ID);")


    db.execute('create table GSMtoSRR(GSM_ID text, SRR text, SRR_ftp text, Reads_Type text)')
    db.execute("CREATE INDEX index_GSMtoSRR ON GSMtoSRR (SRR);")
    # db.execute("CREATE INDEX index_GSMtoSRR ON GSMtoSRR (SRR);")




    # db.execute('create table H3K4me3(GSM_ID text, title text, organism text, SRA text, Library_Strategy text, Platform_ID text,'
    #            'InstrumentID text, antibody, input text, control text,'
    #            'cell_type text, cell_line text, geno_type text, treatment text, disease text,)')
    #
    # db.execute("CREATE INDEX index_H3K4me3 ON GSM (GSM_ID);")

