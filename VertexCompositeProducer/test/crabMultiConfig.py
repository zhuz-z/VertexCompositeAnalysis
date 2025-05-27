from datetime import datetime
from CRABAPI.RawCommand import crabCommand
from CRABClient.UserUtilities import config

config = config()
date = datetime.now().strftime('%y%m%d')
date_time = datetime.now().strftime('%y%m%d_%H%M%S')

## User Input ##############################################################################
pset_name       = 'VCTree_PbPb2023_UPCDiKa_UPCReco_cfg.py'

output_dir      = '/store/group/phys_heavyions/jiazhao/Data_Run3/VCTree/crabMulti_%s/' %  date_time

## General #################################################################################
config.section_('General')
config.General.workArea = 'crab_projects/'+date_time
config.General.transferOutputs = True
config.General.transferLogs = False

## JobType ##################################################################################
config.section_('JobType')
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = pset_name
config.JobType.scriptExe = 'submitScript.sh'
config.JobType.inputFiles = ['emap_2023_newZDC_v3.txt', 'CentralityTable_HFtowers200_DataPbPb_periHYDJETshape_run3v1302x04_offline_374289.db']
config.JobType.maxMemoryMB = 2500
# config.JobType.maxJobRuntimeMin = 720

## Data #####################################################################################
config.section_('Data')
config.Data.lumiMask = '/eos/user/c/cmsdqm/www/CAF/certification/Collisions23HI/Cert_Collisions2023HI_374288_375823_Muon.json'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 1
config.Data.inputDBS = 'global'
config.Data.outputDatasetTag = 'PbPb2023'
config.Data.outLFNDirBase = output_dir
config.Data.publication = False

## Site #####################################################################################
config.section_('Site')
config.Site.whitelist = ['T2_US_Vanderbilt', 'T2_CH_CERN']
config.Site.storageSite = 'T2_CH_CERN'

## Submit PDs ###############################################################################
for i in range(0, 20):
    config.General.requestName = f'HIForward{i}_HIRun2023A_16Jan2024_'+ date_time
    config.Data.inputDataset = f'/HIForward{i}/HIRun2023A-16Jan2024-v1/AOD'

    crabCommand('submit', config = config, dryrun=False)

print('='*50)
print('All jobs submitted.')
print(f'Output directory: {output_dir}')
print('='*50)