# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import pandas as pd

from mag_annotator.database_processing import import_config, print_database_locations
from mag_annotator.annotate_bins import annotate_bins
from mag_annotator.summarize_genomes import summarize_genomes

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.DataFileUtilClient import DataFileUtil

# TODO: Fix no pfam annotations bug
#END_HEADER


class kb_DRAM:
    '''
    Module Name:
    kb_DRAM

    Module Description:
    A KBase module: kb_DRAM
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/shafferm/kb_DRAM.git"
    GIT_COMMIT_HASH = "5eb40b83c26e9a74bf254e2ac223dc1072fce493"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_kb_dram_annotate(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_kb_dram_annotate
        # setup params
        min_contig_size = params['min_contig_size']
        output_dir = os.path.join(self.shared_folder, 'DRAM_annos')
        output_files = []
        output_objects = []

        # create Util objects
        assembly_util = AssemblyUtil(self.callback_url)
        datafile_util = DataFileUtil(self.callback_url)
        report_util = KBaseReport(self.callback_url)

        # set DRAM database locations
        import_config('/data/DRAM_databases/CONFIG')
        print_database_locations()

        # get files
        fastas = assembly_util.get_fastas({'ref_lst': [params['assembly_input_ref']]})
        fasta_locs = [fasta['paths'][0] for fasta in fastas.values()]  # would paths ever have more than one thing?

        # annotate bins
        annotate_bins(fasta_locs, output_dir, min_contig_size, low_mem_mode=True, rename_bins=False, keep_tmp_dir=False,
                      threads=4, verbose=False)
        annotations_tsv_loc = os.path.join(output_dir, 'annotations.tsv')
        output_files.append({
            'path': annotations_tsv_loc,
            'name': 'annotations.tsv',
            'label': 'annotations.tsv',
            'description': 'DRAM annotations in a tab separate table format'
        })
        genes_fna_loc = os.path.join(output_dir, 'genes.fna')
        output_files.append({
            'path': genes_fna_loc,
            'name': 'genes.fna',
            'label': 'genes.fna',
            'description': 'Genes as nucleotides predicted by DRAM with brief annotations'
        })
        genes_faa_loc = os.path.join(output_dir, 'genes.faa')
        output_files.append({
            'path': genes_faa_loc,
            'name': 'genes.faa',
            'label': 'genes.faa',
            'description': 'Genes as amino acids predicted by DRAM with brief annotations'
        })
        rrnas_loc = os.path.join(output_dir, 'rrnas.tsv')
        output_files.append({
            'path': rrnas_loc,
            'name': 'rrnas.tsv',
            'label': 'rrnas.tsv',
            'description': 'Tab separated table of rRNAs as detected by barrnap'
        })
        trnas_loc = os.path.join(output_dir, 'trnas.tsv')
        output_files.append({
            'path': trnas_loc,
            'name': 'trnas.tsv',
            'label': 'trnas.tsv',
            'description': 'Tab separated table of tRNAs as detected by tRNAscan-SE'
        })

        # distill
        distill_output_dir = os.path.join(output_dir, 'distilled')
        trna_path = os.path.join(output_dir, 'trnas.tsv')
        if not os.path.exists(trna_path):
            trna_path = None
        rrna_path = os.path.join(output_dir, 'rrnas.tsv')
        if not os.path.exists(rrna_path):
            rrna_path = None
        summarize_genomes(annotations_tsv_loc, trna_path, rrna_path, output_dir=distill_output_dir,
                          groupby_column='fasta')
        product_tsv_loc = os.path.join(distill_output_dir, 'product.tsv')
        output_files.append({
            'path': product_tsv_loc,
            'name': 'product.tsv',
            'label': 'product.tsv',
            'description': 'DRAM product in tabular format'
        })
        metabolism_summary_loc = os.path.join(distill_output_dir, 'metabolism_summary.xlsx')
        output_files.append({
            'path': metabolism_summary_loc,
            'name': 'metabolism_summary.xlsx',
            'label': 'metabolism_summary.xlsx',
            'description': 'DRAM metabolism summary tables'
        })
        genome_stats_loc = os.path.join(distill_output_dir, 'genome_stats.tsv')
        output_files.append({
            'path': genome_stats_loc,
            'name': 'genome_stats.tsv',
            'label': 'genome_stats.tsv',
            'description': 'DRAM genome statistics table'
        })

        # generate report
        html_file = os.path.join(distill_output_dir, 'product.html')
        report_shock_id = datafile_util.file_to_shock({
            'file_path': distill_output_dir,
            'pack': 'zip'
        })['shock_id']
        html_report = [{
            'shock_id': report_shock_id,
            'name': os.path.basename(html_file),
            'label': os.path.basename(html_file),
            'description': 'HTML summary report for DRAM annotations.'
        }]
        report = report_util.create_extended_report({'message': 'Here are the results from your DRAM run.',
                                                     'workspace_name': params['workspace_name'],
                                                     'html_links': html_report,
                                                     'direct_html_link_index': 0,
                                                     'file_links': output_files,
                                                     'objects_created': output_objects,
                                                     })
        output = {
            'report_name': report['name'],
            'report_ref': report['ref'],
        }

        #END run_kb_dram_annotate

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kb_dram_annotate return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def run_kb_dram_distill(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_kb_dram_distill
        output = {}
        #END run_kb_dram_distill

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kb_dram_distill return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def run_kb_dramv_annotate(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_kb_dramv_annotate
        output = {}
        #END run_kb_dramv_annotate

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kb_dramv_annotate return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def run_kb_dramv_distill(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_kb_dramv_distill
        output = {}
        #END run_kb_dramv_distill

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kb_dramv_distill return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
