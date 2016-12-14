class GSM:
    def __init__(self, GSMID):
        self.id = GSMID
        self.series = []
        self.platForm = None
        self.characteristics = {}
        self.supplementaryData = {}
        self.relations = {}
        self.libraryStrategy = None
        self.SRA = None
        self.type = None
        self.features = None
        self.title = None
        self.InstrumentID = None
        self.organism = None

        self.control = None
        self.input = None

    # potential attributes
        self.antibody = None
        self.treatment = None
        self.tissue = None
        self.disease = None
        self.cellLine = None
        self.cellType = None
        self.genoType = None
        self.title_found = False
        self.ab_found = False
        self.title_ab = False

        self.other = None
