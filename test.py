import os

fileNames = os.listdir("./SRA")

for name in fileNames:
    print name
    cmd = "/home/tmhbxx3/tools/sratoolkit/bin/fastq-dump --split-3 "+"./SRA"+name
    print cmd
    os.system(cmd)

