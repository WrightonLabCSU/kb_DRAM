#!/bin/bash

. /kb/deployment/user-env.sh

PATH=/root/miniconda/bin:$PATH

python ./scripts/prepare_deploy_cfg.py ./deploy.cfg ./work/config.properties

if [ -f ./work/token ] ; then
  export KB_AUTH_TOKEN=$(<./work/token)
fi

if [ $# -eq 0 ] ; then
  sh ./scripts/start_server.sh
elif [ "${1}" = "test" ] ; then
  echo "Run Tests"
  make test
elif [ "${1}" = "async" ] ; then
  sh ./scripts/run_async.sh
elif [ "${1}" = "init" ] ; then
  echo "Initialize module"
  # Could be this to setup?
  pip install -q zenodo_get
  cd /data
  mkdir DRAM_databases
  cd DRAM_databases
  zenodo_get -w files_to_download.txt -r 4581775 # This is the deposition number for the databases dated 3/3/2021
  wget -i files_to_download.txt -nv
  ls
  if md5sum -c md5sums.txt ; then
    DRAM-setup.py set_database_locations --kofam_hmm_loc kofam_profiles.hmm \
                                         --kofam_ko_list_loc kofam_ko_list.tsv \
                                         --pfam_db_loc pfam.mmspro \
                                         --pfam_hmm_dat Pfam-A.hmm.dat.gz \
                                         --dbcan_db_loc dbCAN-HMMdb-V9.txt \
                                         --dbcan_fam_activities CAZyDB.07312019.fam-activities.txt \
                                         --vogdb_db_loc vog_latest_hmms.txt \
                                         --vog_annotations vog_annotations_latest.tsv.gz \
                                         --viral_db_loc refseq_viral.20210303.mmsdb \
                                         --peptidase_db_loc peptidases.20210303.mmsdb \
                                         --description_db_loc description_db.sqlite \
                                         --genome_summary_form_loc genome_summary_form.20210303.tsv \
                                         --module_step_form_loc module_step_form.20210303.tsv \
                                         --etc_module_database_loc etc_mdoule_database.20210303.tsv \
                                         --function_heatmap_form_loc function_heatmap_form.20210303.tsv \
                                         --amg_database_loc amg_database.20210303.tsv
    DRAM-setup.py export_config --output_file CONFIG
    cd /data
    touch __READY__
  else
    echo "Init failed"
  fi
  # or this?
#  DRAM-setup.py prepare_databases --output_dir /data/DRAM_databases --skip_uniref
#  touch __READY__
  # or this?

elif [ "${1}" = "bash" ] ; then
  bash
elif [ "${1}" = "report" ] ; then
  export KB_SDK_COMPILE_REPORT_FILE=./work/compile_report.json
  make compile
else
  echo Unknown
fi
