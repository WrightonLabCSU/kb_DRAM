
Validating module in (/Users/shafferm/lab/kb-sdk/kb_DRAM)

Validating method in (/Users/shafferm/lab/kb-sdk/kb_DRAM/ui/narrative/methods/run_kb_dram_annotate)


Congrats- this module is valid.


Delete old Docker containers
4911e7b9e001

Build Docker image
Sending build context to Docker daemon 498.2 kB

Step 1/13 : FROM kbase/sdkbase2:python
 ---> 1475f4fb2c91
Step 2/13 : MAINTAINER michael.t.shaffer@colostate.edu
 ---> Using cache
 ---> 0f004db203c8
Step 3/13 : RUN apt-get update &&     apt-get install wget &&     wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh &&     sh Miniconda3-latest-Linux-x86_64.sh -b -p /root/miniconda
 ---> Using cache
 ---> b92c457affd1
Step 4/13 : ENV PATH=/root/miniconda/bin:$PATH
 ---> Using cache
 ---> 946626fd7f44
Step 5/13 : RUN echo $(which conda) &&     conda config --set always_yes yes &&     conda config --add channels bioconda &&     conda config --add channels conda-forge &&     conda update conda
 ---> Using cache
 ---> f78876a7365a
Step 6/13 : RUN conda install pandas scikit-bio prodigal "mmseqs2!=10.6d92c" hmmer "trnascan-se >=2" sqlalchemy barrnap "altair >=4" openpyxl networkx ruby parallel wget &&     pip install DRAM-bio
 ---> Using cache
 ---> 89e482cbcce4
Step 7/13 : COPY ./ /kb/module
 ---> cd6b055be160
Step 8/13 : RUN mkdir -p /kb/module/work
 ---> Running in 51fd30c3a21c
Removing intermediate container 51fd30c3a21c
 ---> 5091cb9a1a69
Step 9/13 : RUN chmod -R a+rw /kb/module
 ---> Running in a5aaa8626576
Removing intermediate container a5aaa8626576
 ---> 2e0e7d5eaeba
Step 10/13 : WORKDIR /kb/module
 ---> Running in b767e14571a4
Removing intermediate container b767e14571a4
 ---> cbac2899dcc4
Step 11/13 : RUN make all
 ---> Running in 5152fdcfa078
kb-sdk compile kb_DRAM.spec \
	--out lib \
	--pysrvname kb_DRAM.kb_DRAMServer \
	--pyimplname kb_DRAM.kb_DRAMImpl;
KBase SDK version 1.1.0 (commit aa2b6f2eb5d7b28cfd1ce2197764076a09050972)
chmod +x scripts/entrypoint.sh
mkdir -p bin
echo '#!/bin/bash' > scripts/start_server.sh
echo 'script_dir=$(dirname "$(readlink -f "$0")")' >> scripts/start_server.sh
echo 'export KB_DEPLOYMENT_CONFIG=$script_dir/../deploy.cfg' >> scripts/start_server.sh
echo 'export PYTHONPATH=$script_dir/../lib:$PATH:$PYTHONPATH' >> scripts/start_server.sh
echo 'uwsgi --master --processes 5 --threads 5 --http :5000 --wsgi-file $script_dir/../lib/kb_DRAM/kb_DRAMServer.py' >> scripts/start_server.sh
chmod +x scripts/start_server.sh
mkdir -p bin
echo '#!/bin/bash' > bin/run_kb_DRAM_async_job.sh
echo 'script_dir=$(dirname "$(readlink -f "$0")")' >> bin/run_kb_DRAM_async_job.sh
echo 'export PYTHONPATH=$script_dir/../lib:$PATH:$PYTHONPATH' >> bin/run_kb_DRAM_async_job.sh
echo 'python -u $script_dir/../lib/kb_DRAM/kb_DRAMServer.py $1 $2 $3' >> bin/run_kb_DRAM_async_job.sh
chmod +x bin/run_kb_DRAM_async_job.sh
echo '#!/bin/bash' > test/run_tests.sh
echo 'script_dir=$(dirname "$(readlink -f "$0")")' >> test/run_tests.sh
echo 'export KB_DEPLOYMENT_CONFIG=$script_dir/../deploy.cfg' >> test/run_tests.sh
echo 'export KB_AUTH_TOKEN=`cat /kb/module/work/token`' >> test/run_tests.sh
echo 'echo "Removing temp files..."' >> test/run_tests.sh
echo 'rm -rf /kb/module/work/tmp/*' >> test/run_tests.sh
echo 'echo "...done removing temp files."' >> test/run_tests.sh
echo 'export PYTHONPATH=$script_dir/../lib:$PATH:$PYTHONPATH' >> test/run_tests.sh
echo 'cd $script_dir/../test' >> test/run_tests.sh
echo 'python -m nose --with-coverage --cover-package=kb_DRAM --cover-html --cover-html-dir=/kb/module/work/test_coverage --nocapture  --nologcapture .' >> test/run_tests.sh
chmod +x test/run_tests.sh
Removing intermediate container 5152fdcfa078
 ---> 588942eb9796
Step 12/13 : ENTRYPOINT [ "./scripts/entrypoint.sh" ]
 ---> Running in b651aaedc60a
Removing intermediate container b651aaedc60a
 ---> 0db1242c7fe1
Step 13/13 : CMD [ ]
 ---> Running in f565cf0ef021
Removing intermediate container f565cf0ef021
 ---> 29774bc20d18
Successfully built 29774bc20d18
Successfully tagged test/kb_dram:latest
Delete old Docker image
Deleted: sha256:f8e215d3e784b6bbe8c7c128fe2d1bb9035a9e22205070408516153c0d289a9e
Deleted: sha256:9cc564089438509e9899f26d11012f75cbd64610762ea9d374f391bed66073f9
Deleted: sha256:af9479c452bcaf427a79e9dd4638503ce9e682502aa01bca09a751639eb5cfb8
Deleted: sha256:0695b66027bd2810da8d2c0ab32bb6363ce7de6fc467b136ccda948f6edcd275
Deleted: sha256:221bf71065be16d6125cf699bc53b900d0475944e514ebc137931f0e9e066439
Deleted: sha256:f9a8ee530c43d7c4e35f7bf98593df94eb0ab375f6f062d394df1a27794fd960
Deleted: sha256:11b3a2afeff758f1fb24bf7a460d219c00979ebe6547eaee47b174eac79346b4
Deleted: sha256:c50c468a8490ce80f7ce3dc769bbfa874444541d6a640b4c53521c307e942f0a
Deleted: sha256:f715905fe6fad99415309b83dc927dc7e0195beecd5f75ab79de66fc77426b8d
Deleted: sha256:e18b2d37bba3e4c5b1a816a3bccac6edecad72fadc4b737dde6cd4f004c38e45
Deleted: sha256:ca8f279803dbabe79ee057eac156028874d9e24f87fc57547bddce801e4886ee

Run Tests
if [ ! -f /kb/module/work/token ]; then echo -e '\nOutside a docker container please run "kb-sdk test" rather than "make test"\n' && exit 1; fi
bash test/run_tests.sh
Removing temp files...
...done removing temp files.
E
======================================================================
ERROR: Failure: ModuleNotFoundError (No module named 'mag_annotator')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/miniconda/lib/python3.6/site-packages/nose/failure.py", line 39, in runTest
    raise self.exc_val.with_traceback(self.tb)
  File "/miniconda/lib/python3.6/site-packages/nose/loader.py", line 418, in loadTestsFromName
    addr.filename, addr.module)
  File "/miniconda/lib/python3.6/site-packages/nose/importer.py", line 47, in importFromPath
    return self.importFromDir(dir_path, fqname)
  File "/miniconda/lib/python3.6/site-packages/nose/importer.py", line 94, in importFromDir
    mod = load_module(part_fqname, fh, filename, desc)
  File "/miniconda/lib/python3.6/imp.py", line 235, in load_module
    return load_source(name, filename, file)
  File "/miniconda/lib/python3.6/imp.py", line 172, in load_source
    module = _load(spec)
  File "<frozen importlib._bootstrap>", line 684, in _load
  File "<frozen importlib._bootstrap>", line 665, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 678, in exec_module
  File "<frozen importlib._bootstrap>", line 219, in _call_with_frames_removed
  File "/kb/module/test/kb_DRAM_server_test.py", line 7, in <module>
    from kb_DRAM.kb_DRAMImpl import kb_DRAM
  File "/kb/module/lib/kb_DRAM/kb_DRAMImpl.py", line 6, in <module>
    from mag_annotator.annotate_bins import annotate_bins
ModuleNotFoundError: No module named 'mag_annotator'

Name                  Stmts   Miss  Cover
-----------------------------------------
kb_DRAM/__init__.py       0      0   100%
----------------------------------------------------------------------
Ran 1 test in 0.007s

FAILED (errors=1)
Makefile:61: recipe for target 'test' failed
make: *** [test] Error 1
Shutting down callback server...
1588958840.72 - CallbackServer: Shutting down executor service
