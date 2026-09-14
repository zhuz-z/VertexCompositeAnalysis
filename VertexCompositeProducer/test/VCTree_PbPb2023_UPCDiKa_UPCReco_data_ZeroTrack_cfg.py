import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras
process = cms.Process('ANASKIM', eras.Run3_2023_UPC)

process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Reconstruction_Data_cff')

# Limit the output messages
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))
process.options.numberOfThreads=cms.untracked.uint32(1)

# Define the input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring("root://xrootd-cms.infn.it///store/hidata/HIRun2023A/HIZeroBias0/AOD/16Jan2024-v1/2810000/0425f6d3-cac4-4968-b8d4-8f1186af09e8.root"),
)
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))

# Set the global tag
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.GlobalTag.globaltag = cms.string('132X_dataRun3_Prompt_HI_LowPtPhotonReg_v2')


## ##############################################################################################################################
## Variables Production #########################################################################################################

#* Set ZDC information
process.es_pool = cms.ESSource("PoolDBESSource",
    timetype = cms.string('runnumber'),
    toGet = cms.VPSet(cms.PSet(record = cms.string("HcalElectronicsMapRcd"), tag = cms.string("HcalElectronicsMap_2021_v2.0_data"))),
    connect = cms.string('frontier://FrontierProd/CMS_CONDITIONS'),
    authenticationMethod = cms.untracked.uint32(1)
)
process.es_prefer = cms.ESPrefer('HcalTextCalibrations', 'es_ascii')
process.es_ascii = cms.ESSource('HcalTextCalibrations',
    input = cms.VPSet(cms.PSet(object = cms.string('ElectronicsMap'), file = cms.FileInPath("VertexCompositeAnalysis/VertexCompositeProducer/data/emap_2023_newZDC_v3.txt")))
)

#* cent_seq: Add PbPb centrality
process.load("RecoHI.HiCentralityAlgos.CentralityBin_cfi")
process.GlobalTag.snapshotTime = cms.string("9999-12-31 23:59:59.000")
process.GlobalTag.toGet.extend([
    cms.PSet(record = cms.string("HeavyIonRcd"),
        tag = cms.string("CentralityTable_HFtowers200_DataPbPb_periHYDJETshape_run3v1302x04_offline_374289"),
        connect = cms.string("sqlite_file:CentralityTable_HFtowers200_DataPbPb_periHYDJETshape_run3v1302x04_offline_374289.db"),
        label = cms.untracked.string("HFtowers")
        )
    ]
)
process.cent_seq = cms.Sequence(process.centralityBin)

#* Add the Particle producer
from VertexCompositeAnalysis.VertexCompositeProducer.generalParticles_cff import generalParticles

# Add trigger selection
import HLTrigger.HLTfilters.hltHighLevel_cfi
process.hltFilter = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()
process.hltFilter.andOr = cms.bool(True)
process.hltFilter.throw = cms.bool(False)
process.hltFilter.HLTPaths = [
    # Zero Bias triggers
    # 'HLT_HIZeroBias_v*',
    'HLT_HIZeroBias_HighRateRAW_v*'
    # 'HLT_HIZeroBias_HighRate_v*',
]

# Add PbPb collision event selection
# process.load('VertexCompositeAnalysis.VertexCompositeProducer.primaryVertexRecoveryForUPC_cfi')
process.load('VertexCompositeAnalysis.VertexCompositeProducer.collisionEventSelection_cff')
process.load('VertexCompositeAnalysis.VertexCompositeProducer.hfCoincFilter_cff')
process.colEvtSel = cms.Sequence(process.hiClusterCompatibility)
# process.primaryVertexFilterRecoveryForUPC = process.primaryVertexFilter.clone(src = "primaryVertexRecoveryForUPC")

# Define the event selection sequence
process.eventFilter_HM = cms.Sequence(
    process.hltFilter
)
process.eventFilter_HM_step = cms.Path( process.eventFilter_HM )

# Define the analysis steps
process.zb_rereco_step = cms.Path(process.eventFilter_HM * process.hfPosFilterNTh10_seq * process.hfNegFilterNTh10_seq * process.cent_seq)

## Adding the VertexComposite tree ################################################################################################

event_filter = cms.untracked.vstring(
    "Flag_colEvtSel",
    "Flag_clusterCompatibilityFilter",
    "Flag_primaryVertexFilter",
    "Flag_hfPosFilterNTh7",
    "Flag_hfPosFilterNTh7p3",
    "Flag_hfPosFilterNTh8",
    "Flag_hfPosFilterNTh10",
    "Flag_hfNegFilterNTh7",
    "Flag_hfNegFilterNTh7p6",
    "Flag_hfNegFilterNTh8",
    "Flag_hfNegFilterNTh10",
)

trig_info = cms.untracked.VPSet([
    # Zero Bias triggers
    cms.PSet(path = cms.string('HLT_HIZeroBias_HighRateRAW_v*')),
    # cms.PSet(path = cms.string('HLT_HIZeroBias_v*')),
    # cms.PSet(path = cms.string('HLT_HIZeroBias_HighRate_v*')),
])

from VertexCompositeAnalysis.VertexCompositeAnalyzer.particle_tree_cff import particleAna
process.ZeroBiasAna = particleAna.clone(
  recoParticles = cms.InputTag("generalTracks"),
  selectEvents = cms.string("zb_rereco_step"),
  eventFilterNames = event_filter,
  addTrgObj = cms.untracked.bool(True),
  triggerInfo = trig_info,
)

# Define the output
process.TFileService = cms.Service("TFileService", fileName = cms.string('ZeroBias_ana.root'))
process.p = cms.EndPath(process.ZeroBiasAna)

#! Define the process schedule !!!!!!!!!!!!!!!!!!
process.schedule = cms.Schedule(
    process.eventFilter_HM_step,
    process.zb_rereco_step,
    process.p
)
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

## Add the event selection filters ###############################################################################################
process.Flag_colEvtSel = cms.Path(process.colEvtSel)
process.Flag_clusterCompatibilityFilter = cms.Path(process.eventFilter_HM * process.hiClusterCompatibility)
process.Flag_primaryVertexFilter = cms.Path(process.eventFilter_HM * process.primaryVertexFilter)
# process.Flag_primaryVertexFilterRecoveryForUPC = cms.Path(process.eventFilter_HM * process.primaryVertexFilterRecoveryForUPC)
process.Flag_hfPosFilterNTh7 = cms.Path(process.eventFilter_HM * process.hfPosFilterNTh7_seq)
process.Flag_hfPosFilterNTh7p3 = cms.Path(process.eventFilter_HM * process.hfPosFilterNTh7p3_seq)
process.Flag_hfPosFilterNTh8 = cms.Path(process.eventFilter_HM * process.hfPosFilterNTh8_seq)
process.Flag_hfPosFilterNTh10 = cms.Path(process.eventFilter_HM * process.hfPosFilterNTh10_seq)
process.Flag_hfNegFilterNTh7 = cms.Path(process.eventFilter_HM * process.hfNegFilterNTh7_seq)
process.Flag_hfNegFilterNTh7p6 = cms.Path(process.eventFilter_HM * process.hfNegFilterNTh7p6_seq)
process.Flag_hfNegFilterNTh8 = cms.Path(process.eventFilter_HM * process.hfNegFilterNTh8_seq)
process.Flag_hfNegFilterNTh10 = cms.Path(process.eventFilter_HM * process.hfNegFilterNTh10_seq)

eventFilterPaths = [ process.Flag_colEvtSel , process.Flag_clusterCompatibilityFilter , process.Flag_primaryVertexFilter , process.Flag_hfPosFilterNTh7 , process.Flag_hfPosFilterNTh7p3 , process.Flag_hfPosFilterNTh8 , process.Flag_hfPosFilterNTh10 , process.Flag_hfNegFilterNTh7 , process.Flag_hfNegFilterNTh7p6 , process.Flag_hfNegFilterNTh8 , process.Flag_hfNegFilterNTh10 ]

#! Adding the process schedule !!!!!!!!!!!!!!!!!!
for P in eventFilterPaths:
    process.schedule.insert(0, P)
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
