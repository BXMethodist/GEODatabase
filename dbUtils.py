from ftplib import FTP
import os
import sqlite3
import urllib
import requests
import mimetypes
import csv
from collections import defaultdict
from GSM import GSM
import re


def connectToGEO(email='bxia@houstonmethodist.org', user='anonymous', ftpAddress='ftp.ncbi.nlm.nih.gov'):
    ### create GEO ftp connection to NCBI
    ftp = FTP(ftpAddress)
    ftp.login(user, email)
    return ftp


def newGSEinGEO(db, update=True):
    # looking for new GSE, if not in local, download from GEO
    localpath = "/home/tmhbxx3/scratch/XMLhttp/GSESoftQuick/"
    localStoredGSEs = set([gse[:-4] for gse in os.listdir(localpath) if gse.startswith("GSE")])

    if not update:
        return localStoredGSEs

    ftp = connectToGEO()

    curGSE = currentGSEinDB(db)

    GEO_prefix = '/geo/series/'
    seriesID = []
    ftp.cwd(GEO_prefix)
    GSE_nnnList = ftp.nlst()
    for GSE_nnn in GSE_nnnList:
        cwd = GEO_prefix+GSE_nnn
        ftp.cwd(cwd)
        GSE_xxxxxList = ftp.nlst()
        seriesID += [id for id in GSE_xxxxxList]

    newSeriesID = set()

    for id in seriesID:
        if id not in curGSE:
            newSeriesID.add(id)
        if id not in localStoredGSEs:
            downloadGSE(id)
    return newSeriesID


def currentGSEinDB(db):
    #get current GSE ids from local database
    gse = [str(id[0]) for id in db.execute("select GSE_ID from GSEtoGSM").fetchall()]
    gse = set(gse)
    return gse


def downloadGSE(gseID):
    #Download GSE from NCBI https website
    url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=" + gseID + "&targ=self&form=text&view=quick"
    response = requests.get(url)
    content_type = response.headers['content-type']
    extension = mimetypes.guess_extension(content_type)
    if content_type == "geo/text" and extension != ".html":
        urllib.urlretrieve(url, '/home/tmhbxx3/scratch/XMLhttp/GSESoftQuick/' + gseID + ".txt")
    return


def gseParser(newSeriesID=()):
    # Parse the GSE SOFT meta data to get GSM ids and organization, which is need to create the map from public project
    # to GSM
    path = "/home/tmhbxx3/scratch/XMLhttp/GSESoftQuick/"
    pairs = []
    if len(newSeriesID) == 0:
        return

    for GSEName in newSeriesID:
        filename = GSEName + ".txt"
        contact = None
        curPair = []
        file = open(path+filename, "r")
        for line in file.readlines():
            if line.startswith("!Series_sample_id"):
                GSMid = line[line.find("GSM"):].strip()
                curPair.append([GSEName, GSMid])
            if line.startswith("!Series_contact_institute"):
                contact = line[line.find("=")+2:].strip()
        for p in curPair:
            p.append(contact)
        file.close()

        pairs += curPair
    return pairs


def updateTableGSE(db, update=True):
    # update function will be called by updateDB module
    newSeriesID = list(newGSEinGEO(db, update))
    pairs = gseParser(newSeriesID)
    return pairs


###
def downloadGSM(gsmID):
    ## download GSM meta data from NCBI
    url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=" + gsmID + "&targ=self&form=text&view=quick"
    response = requests.get(url)
    content_type = response.headers['content-type']
    extension = mimetypes.guess_extension(content_type)
    if content_type == "geo/text" and extension != ".html":
        urllib.urlretrieve(url, '/home/tmhbxx3/scratch/XMLhttp/QuickXMLs/' + gsmID + ".xml")
    return


def newGSMinGEO(db, update=True):
    # looking for local GSM meta data stock and GSM info in current GSM table and GSEtoGSM table
    # return the GSM ids need to be updated
    GSMinGSE = set([id[0] for id in db.execute("select GSM_ID from GSEtoGSM").fetchall()])

    localpath = "/home/tmhbxx3/scratch/XMLhttp/QuickXMLs"
    localStoredGSMs = set([gsm[:-4] for gsm in os.listdir(localpath) if gsm.startswith("GSM")])

    if not update:
        return localStoredGSMs

    newGSMID = set()
    GSMIDinGSMTable = set([id[0] for id in db.execute("select GSM_ID from GSM").fetchall()])

    for id in GSMinGSE:
        if id not in localStoredGSMs:
            downloadGSM(id)
        if id not in GSMIDinGSMTable:
            newGSMID.add(id)
    return newGSMID


def gsmParser(newGSMID=[]):
    # parse the GSM meta data and return the GSM samples objects(dict)
    path = "/home/tmhbxx3/scratch/XMLhttp/QuickXMLs"
    if len(newGSMID) == 0:
        return

    Samples = {}

    for sampleName in newGSMID:
        filename = sampleName + ".xml"
        file = open(path + '/' + filename, "r")
        characteristics = defaultdict(str)
        relations = defaultdict(str)
        feature = {}

        antibody = ""
        treatment = ""
        tissue = ""
        disease = ""
        cellLine = ""
        cellType = ""
        genoType = ""

        sampleTitle = ""
        sampleType = ""
        sampleLibraryStrategy = ""
        sampleOrganism = ""
        samplePlatForm = ""
        sampleInstrumentID = ""
        other = ""


        for line in file.readlines():
            if line.startswith("!Sample_title"):
                sampleTitle = line[line.find("=") + 1:].strip()
            if line.startswith("!Sample_type"):
                sampleType = line[line.find("=") + 1:].strip()
            if line.startswith("!Sample_organism"):
                sampleOrganism = line[line.find("=") + 1:].strip()
            if line.startswith("!Sample_characteristics_ch"):
                characteristic = line[line.find("=") + 1:].strip()
                key, value = characteristic[:characteristic.find(":")].strip(), characteristic[
                                                                                characteristic.find(":") + 1:].strip()
                if key in characteristics:
                    characteristics[key] += ", " + value
                else:
                    characteristics[key] = value
                if re.search("h3k4me3", value, flags=re.IGNORECASE):
                    feature[key] = value
            if line.startswith("!Sample_platform_id "):
                samplePlatForm = line[line.find("=") + 1:].strip()
            if line.startswith("!Sample_library_strategy"):
                sampleLibraryStrategy = line[line.find("=") + 1:].strip()
            if line.startswith("!Sample_relation"):
                relation = line[line.find("=") + 1:].strip()
                key, value = relation[:relation.find(":")].strip(), relation[relation.find(":") + 1:].strip()
                relations[key] = value
            if line.startswith("!Sample_instrument_model"):
                sampleInstrumentID = line[line.find("=") + 1:].strip()

        sample = GSM(sampleName)
        sample.characteristics = characteristics
        sample.title = sampleTitle
        sample.type = sampleType
        sample.libraryStrategy = sampleLibraryStrategy
        sample.organism = sampleOrganism
        sample.SRA = relations["SRA"]

        sample.platForm = samplePlatForm
        sample.features = feature
        sample.InstrumentID = sampleInstrumentID



        for key, value in characteristics.items():
            if key.lower() in ["chip antibody", "chip", "antigen", "antibody", "antibodies", "chip antibodies",
                               "antibody name", "antibody target", "target", "antibody/capture", "antibody/vendor/catalog#",
                               "chip ab", "chip antibody1", "chip antibody2", "chip-antibody", "chip_antibody",
                               "chip-seq antibody", "chip_antibodies", "chip-antibodies", "histone mark",
                               "epigenetic feature",
                               "histone modification", "antibody antibodydescription", "chip antibody (epitope/name)",
                               "factor", "chip antibody/mbd affinity column", "chip/dip antibody", "antibody epiptope",
                               "antibody source", 'modification', "antibody (vendor': ' catalog#, or reference)",
                               "experiment", "purification antibody", "antibody/details", "antibody epiptope",
                               "antibody information", "chip antibody / digestive enzyme", "chip antiboy",
                               "ip antibody", "chip antibody target", "modification", "histone", "enrichment procedure",
                               "antibody (vendor': ' catalog#, or reference)",
                               "developmental stage/condition/extract protocol",
                               "antibody source"] \
                    or re.search('antibody epitope|using[\w\s]+antibod|immunoprecipitat', key, flags=re.IGNORECASE):
                antibody += key.lower()+":"+value.lower()
            elif key.lower() in ["treatment", "condition", "activation stimuli", "cell condition", "cell treatment",
                               "cell-treatment", "drug treatment", "stress", "overexpression", "treatment drug",
                               "treatment group"] \
                    or re.search("(?:dsrna|infect|rnai|shrna|sirna|transduc|transfec|agent[#]*[0-9]*|activat)", key,
                                 flags=re.IGNORECASE):
                treatment += key.lower()+":"+value.lower()

            elif key.lower() in ["tissue", "body part", "body site"]:
                tissue += key.lower()+":"+value.lower()

            elif key.lower() in ["cancer type", "tumor type", "tumor region", "disease", "disease state", "disease status"]:
                disease = key.lower()+":"+value.lower()

            elif key.lower() in ["background strain", "strain", "strain number", "mouse strain", "strain background",
                               "cell line background", "genetic background", "genotype", "genotype/variation",
                               "strain/background", "variation"]:
                genoType += key.lower()+":"+value.lower()

            elif key.lower() in ["cell line", "cell", "cells pointed by barcodes",
                               "chicken line", "line"]:
                cellLine += key.lower()+":"+value.lower()

            elif key.lower() in ["cell_type", "cell-type", "cell type", "cell lineage"]:
                cellType += key.lower()+":"+value.lower()
            else:
                other += key.lower()+":"+value.lower()

        sample.antibody = antibody
        sample.treatment = treatment
        sample.disease = disease
        sample.cellLine = cellLine
        sample.genoType = genoType
        sample.tissue = tissue
        sample.other = other

        Samples[sample.id] = sample

        file.close()

    return Samples


def updateTableGSM(db, update=True):
    # update GSM tables which will be called by updateDB module
    newGSMID = list(newGSMinGEO(db, update))
    samples = gsmParser(newGSMID)
    return samples

####
def downloadSRR(SRXlink):
    ## download GSM meta data from NCBI
    page = urllib.urlopen(SRXlink).read()

    SRRids = re.findall("SRR[0-9]+", page)

    for SRRid in SRRids:
        url = "https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?sp=runinfo&acc="+SRRid+"&retmode=xml"
        response = requests.get(url)
        content_type = response.headers['content-type']
        extension = mimetypes.guess_extension(content_type)
        if content_type == "geo/text" and extension != ".html":
            urllib.urlretrieve(url, '/home/tmhbxx3/scratch/XMLhttp/SRRXMLs/' + SRRid + ".xml")
    return


def getSRR(SRXlink):
    # get SRR id and SRR ftp download address
    # return a list of tuple, [(srr, ftp)...]
    ftp = connectToGEO()

    results = []

    try:
        SRX = SRXlink[(SRXlink.find("=") + 1):].strip()
        SRXfolder = SRX[:6]

        subfolderAddress = "/sra/sra-instant/reads/ByExp/sra/SRX/" + SRXfolder + '/' + SRX + '/'

        ftp.cwd(subfolderAddress)

        SRRfolderList = ftp.nlst()

        for SRRfolder in SRRfolderList:
            SRRfolderAddress = subfolderAddress + SRRfolder + '/'
            ftp.cwd(SRRfolderAddress)

            SRRfiles = ftp.nlst()
            for SRRfile in SRRfiles:
                downloadFTP = ftp.host + SRRfolderAddress + SRRfile
                results.append([SRRfolder, downloadFTP])
    except:
        page = urllib.urlopen(SRXlink).read()

        SRRfolderList = re.findall("SRR[0-9]+", page)

        for SRR in SRRfolderList:
            results.append([SRR, ""])

    for file in results:
        SRRid = file[0]
        link = "https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?sp=runinfo&acc="+SRRid+"&retmode=xml"
        page = urllib.urlopen(link).read()
        type = page[page.find("<LibraryLayout>") + len("<LibraryLayout>"):page.find("</LibraryLayout>")]
        file.append(type)
    return results


def updateGSMtoSRR(db, update=True, newGSMs=None):
    # update GSMtoSRR tables which will be called by updateDB module
    GSMtoSRR = defaultdict(list)

    if newGSMs is None:
        for row in db.execute("select GSM_ID, SRA from GSM").fetchall()[20:200000]:
            GSM_ID, SRXlink = row

            if SRXlink is None or len(SRXlink.strip()) == 0:
                continue
            SRRinfos = getSRR(SRXlink)

            for info in SRRinfos:
                GSMtoSRR[GSM_ID].append(info)
    else:
        for id in newGSMs:
            query = db.execute('select GSM_ID, SRA from GSM where GSM_ID = "'+id+'"').fetchall()
            if len(query) == 1:
                GSM_ID, SRXlink = query[0]
                if len(SRXlink.strip()) == 0:
                    continue
                SRRinfos = getSRR(SRXlink)
                for info in SRRinfos:
                    GSMtoSRR[GSM_ID].append(info)
    return GSMtoSRR
