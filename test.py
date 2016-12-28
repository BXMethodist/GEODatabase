import os
import requests
import mimetypes
# fileNames = os.listdir("./SRA")
#
# for name in fileNames:
#     print name
#     cmd = "/home/tmhbxx3/tools/sratoolkit/bin/fastq-dump --split-3 "+"./SRA"+name
#     print cmd
#     os.system(cmd)


url = "https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?sp=runinfo&acc="+"DRR022442"+"&retmode=xml"
response = requests.get(url)

print response
content_type = response.headers['content-type']
extension = mimetypes.guess_extension(content_type)

print extension

print response
print content_type
https://www.ncbi.nlm.nih.gov/sra?term=DRX020503
[]
https://www.ncbi.nlm.nih.gov/sra?term=DRX020504
[]
https://www.ncbi.nlm.nih.gov/sra?term=DRX020505