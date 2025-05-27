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
    fileNames = cms.untracked.vstring("root://xrootd-cms.infn.it//store/user/anstahll/CERN/PbPb2023/MC/2024_07_09/STARLIGHT/STARLIGHT_5p36TeV_2023Run3/coh_phi_dika_STARLIGHT_5p36TeV_2023Run3_UPCRECO_2024_07_09/240708_095519/0000/STARLIGHT_coh_phi_dika_RECO_10.root"),
)
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(2000))

# Set the global tag
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.GlobalTag.globaltag = cms.string('132X_mcRun3_2023_realistic_HI_v9')


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

generalTrackParticles = generalParticles.clone(
    recoToSimTrackMap = cms.InputTag('trackingParticleRecoTrackAsssociation')
)

process.tracks = generalTrackParticles.clone(
    tracks = cms.InputTag('generalTracks'),
    dEdxInputs = cms.vstring('dedxHarmonic2', 'dedxPixelHarmonic2')
)

# process.pixelTracks = generalParticles.clone(
#     tracks = cms.InputTag('hiConformalPixelTracks'),
#     dEdxInputs = cms.vstring('dedxHarmonic2', 'dedxPixelHarmonic2'),
#     recoToSimTrackMap = cms.InputTag('trackingParticlePixelTrackAsssociation')
# )

# process.track_step = cms.Path(process.tracks * process.pixelTracks)
process.track_step = cms.Path(process.tracks)

# Add event selection
# process.oneTracks = cms.EDFilter("TrackCountFilter", src = cms.InputTag("generalTracks"), minNumber = cms.uint32(1))
# process.oneTracks = cms.EDFilter("TrackCountFilter", src = cms.InputTag("hiConformalPixelTracks"), minNumber = cms.uint32(1))
# process.pixelTracks = cms.EDFilter("TrackSelector", src = cms.InputTag("hiConformalPixelTracks"), cut = cms.string(""))
# process.pixelCands = cms.EDProducer("ChargedCandidateProducer", src = cms.InputTag("pixelTracks"), particleType = cms.string('pi+'))
# process.maxOneCands = cms.EDFilter("PATCandViewCountFilter", src = cms.InputTag("pixelCands"), minNumber = cms.uint32(1), maxNumber = cms.uint32(1))


# process.trackSel = cms.Sequence(process.oneTracks)
# process.trackSel = cms.Sequence(process.oneTracks * process.pixelCands * process.maxOneCands)


# Add PbPb collision event selection
process.load('VertexCompositeAnalysis.VertexCompositeProducer.collisionEventSelection_cff')
process.load('VertexCompositeAnalysis.VertexCompositeProducer.hfCoincFilter_cff')
process.colEvtSel = cms.Sequence(process.hiClusterCompatibility)

# Define the event selection sequence
process.eventFilter_HM = cms.Sequence(
    process.colEvtSel
    # process.trackSel
)
process.eventFilter_HM_step = cms.Path( process.eventFilter_HM )

## Adding the VertexComposite tree ################################################################################################

event_filter = cms.untracked.vstring(
        "Flag_colEvtSel",
        "Flag_clusterCompatibilityFilter",
        "Flag_hfPosFilterNTh7",
        "Flag_hfPosFilterNTh7p3",
        "Flag_hfPosFilterNTh8",
        "Flag_hfPosFilterNTh10",
        "Flag_hfNegFilterNTh7",
        "Flag_hfNegFilterNTh7p6",
        "Flag_hfNegFilterNTh8",
        "Flag_hfNegFilterNTh10",
    )

# trig_info = cms.untracked.VPSet([
#     # Zero Bias triggers
#     # cms.PSet(path = cms.string('HLT_HIZeroBias_v*')),
#     # cms.PSet(path = cms.string('HLT_HIZeroBias_HighRate_v*')),
#     # UPC ZB triggers
#     # cms.PSet(path = cms.string('HLT_HIUPC_ZeroBias_SinglePixelTrack_MaxPixelTrack_v*')),
#     cms.PSet(path = cms.string('HLT_HIUPC_ZeroBias_SinglePixelTrackLowPt_MaxPixelCluster400_v*'), filter = cms.string('hltSinglePixelTrackLowPtForUPC'), minN = cms.int32(1)),
#     # cms.PSet(path = cms.string('HLT_HIUPC_ZeroBias_MinPixelCluster400_MaxPixelCluster10000_v*')),
#     # UPC ZDC triggers
#     # cms.PSet(path = cms.string('HLT_HIUPC_ZDC1nOR_SinglePixelTrack_MaxPixelTrack_v*')),
#     # cms.PSet(path = cms.string('HLT_HIUPC_ZDC1nOR_SinglePixelTrackLowPt_MaxPixelCluster400_v*')),
#     # cms.PSet(path = cms.string('HLT_HIUPC_ZDC1nOR_MinPixelCluster400_MaxPixelCluster10000_v*')),
#   ])

from VertexCompositeAnalysis.VertexCompositeAnalyzer.particle_tree_cff import particleAna_mc
process.trackAna = particleAna_mc.clone(
  recoParticles = cms.InputTag("tracks"),
  selectEvents = cms.string(""),
  eventFilterNames = event_filter,
#   addTrgObj = cms.untracked.bool(True),
#   triggerInfo = trig_info,
)

# Define the output
process.TFileService = cms.Service("TFileService", fileName = cms.string('track_ana_mc.root'))
# process.p = cms.EndPath(process.trackAna * process.pixelTrackAna)
process.p = cms.EndPath(process.trackAna)

#! Define the process schedule !!!!!!!!!!!!!!!!!!
process.schedule = cms.Schedule(
    process.eventFilter_HM_step,
    process.track_step,
    process.p
)
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

## Add the event selection filters ###############################################################################################
process.Flag_colEvtSel = cms.Path(process.colEvtSel)
process.Flag_clusterCompatibilityFilter = cms.Path(process.eventFilter_HM * process.hiClusterCompatibility)
process.Flag_hfPosFilterNTh7 = cms.Path(process.eventFilter_HM * process.hfPosFilterNTh7_seq)
process.Flag_hfPosFilterNTh7p3 = cms.Path(process.eventFilter_HM * process.hfPosFilterNTh7p3_seq)
process.Flag_hfPosFilterNTh8 = cms.Path(process.eventFilter_HM * process.hfPosFilterNTh8_seq)
process.Flag_hfPosFilterNTh10 = cms.Path(process.eventFilter_HM * process.hfPosFilterNTh10_seq)
process.Flag_hfNegFilterNTh7 = cms.Path(process.eventFilter_HM * process.hfNegFilterNTh7_seq)
process.Flag_hfNegFilterNTh7p6 = cms.Path(process.eventFilter_HM * process.hfNegFilterNTh7p6_seq)
process.Flag_hfNegFilterNTh8 = cms.Path(process.eventFilter_HM * process.hfNegFilterNTh8_seq)
process.Flag_hfNegFilterNTh10 = cms.Path(process.eventFilter_HM * process.hfNegFilterNTh10_seq)

eventFilterPaths = [ process.Flag_colEvtSel , process.Flag_clusterCompatibilityFilter , process.Flag_hfPosFilterNTh7 , process.Flag_hfPosFilterNTh7p3 , process.Flag_hfPosFilterNTh8 , process.Flag_hfPosFilterNTh10 , process.Flag_hfNegFilterNTh7 , process.Flag_hfNegFilterNTh7p6 , process.Flag_hfNegFilterNTh8 , process.Flag_hfNegFilterNTh10 ]

#! Adding the process schedule !!!!!!!!!!!!!!!!!!
for P in eventFilterPaths:
    process.schedule.insert(0, P)
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
