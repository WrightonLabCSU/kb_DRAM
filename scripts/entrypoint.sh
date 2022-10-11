#!/bin/bash

. /kb/deployment/user-env.sh

PATH=/root/miniconda/bin:$PATH
ZENODO_REF=7183884  # This is the deposition number for the databases dated October 6, 2022

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
  zenodo_get -w files_to_download.txt -r $ZENODO_REF
  # cat files_to_download.txt
  wget -c  https://zenodo.org/record/7154703/files/CONFIG.tar.gz -O - | tar -xz
  wget -i files_to_download.txt -nv
  if md5sum -c md5sums.txt ; then
      for file in *.tar.gz; do tar xzvf "${file}" && rm -f "${file}"; done
      # DRAM-setup.py set_database_locations
      DRAM-setup.py mv_db_folder --old_config_file ./CONFIG
      DRAM-setup.py export_config --output_file CONFIG
      cd /data
      touch __READY__
  else
    echo "Init failed"
fi
# or this?
elif [ "${1}" = "bash" ] ; then
  bash
elif [ "${1}" = "report" ] ; then
  export KB_SDK_COMPILE_REPORT_FILE=./work/compile_report.json
  make compile
else
  echo Unknown
fi
