# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import hashlib
import pandas as pd
from skbio import read as read_sequence

from mag_annotator.database_processing import import_config, print_database_locations
from mag_annotator.annotate_bins import annotate_bins
from mag_annotator.summarize_genomes import summarize_genomes
from mag_annotator.utils import remove_suffix

from installed_clients.WorkspaceClient import Workspace as workspaceService
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.GenomeFileUtilClient import GenomeFileUtil

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
    GIT_COMMIT_HASH = "841dbe5ba8fc4081377fd7ab7848d41262a33015"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.workspaceURL = config['workspace-url']
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
        # validate inputs
        if not isinstance(params['assembly_input_ref'], str) or not len(params['assembly_input_ref']):
            raise ValueError('Pass in a valid assembly reference string')
        if not isinstance(params['desc'], str) or not len(params['desc']):
            raise ValueError('Pass in a valid genomeSet description')
        if not isinstance(params['output_name'], str) or not len(params['output_name']):
            raise ValueError('Pass in a valid genomeSet output name')
        if not isinstance(params['min_contig_size'], int) or (params['min_contig_size'] < 0):
            raise ValueError('Min contig size must be a non-negative integer')

        # setup params
        min_contig_size = params['min_contig_size']
        output_dir = os.path.join(self.shared_folder, 'DRAM_annos')
        output_files = []
        output_objects = []

        # create Util objects
        wsClient = workspaceService(self.workspaceURL, token=ctx['token'])
        assembly_util = AssemblyUtil(self.callback_url)
        genome_util = GenomeFileUtil(self.callback_url)
        datafile_util = DataFileUtil(self.callback_url)
        report_util = KBaseReport(self.callback_url)

        # set DRAM database locations
        import_config('/data/DRAM_databases/CONFIG')
        print_database_locations()

        # get files
        assemblies = assembly_util.get_fastas({'ref_lst': [params['assembly_input_ref']]})
        # would paths ever have more than one thing?
        fasta_locs = [assembly_data['paths'][0] for assembly_ref, assembly_data in assemblies.items()]
        # get assembly refs from dram assigned genome names
        # TODO: rewrite annotate_bins to take optional list of fasta names and pass assembly refs as list
        assembly_ref_dict = {os.path.splitext(os.path.basename(remove_suffix(assembly_data['paths'][0], '.gz')))[0]:
                                 assembly_ref for assembly_ref, assembly_data in assemblies.items()}

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
        if os.path.exists(rrnas_loc):
            output_files.append({
                'path': rrnas_loc,
                'name': 'rrnas.tsv',
                'label': 'rrnas.tsv',
                'description': 'Tab separated table of rRNAs as detected by barrnap'
            })
        else:
            rrnas_loc = None
        trnas_loc = os.path.join(output_dir, 'trnas.tsv')
        if os.path.exists(trnas_loc):
            output_files.append({
                'path': trnas_loc,
                'name': 'trnas.tsv',
                'label': 'trnas.tsv',
                'description': 'Tab separated table of tRNAs as detected by tRNAscan-SE'
            })
        else:
            trnas_loc = None

        # distill
        distill_output_dir = os.path.join(output_dir, 'distilled')
        summarize_genomes(annotations_tsv_loc, trnas_loc, rrnas_loc, output_dir=distill_output_dir,
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

        # generate genome files
        annotations = pd.read_csv(annotations_tsv_loc, sep='\t', index_col=0)
        genes_nucl = {i.metadata['id']: i for i in read_sequence(genes_fna_loc, format='fasta')}
        genes_aa = {i.metadata['id']: i for i in read_sequence(genes_faa_loc, format='fasta')}
        genome_ref_list = list()
        genome_set_elements = dict()
        for genome_name, genome_annotations in annotations.groupby('fasta'):
            # set scientific name, domain and genetic code
            if 'bin_taxonomy' in genome_annotations.columns:  # assuming gtdb taxa strings
                scientific_name = genome_annotations['bin_taxonomy'].iloc[0]  # not really the scientific name, whatever
                domain = scientific_name.split[';'][0]
            else:
                scientific_name = 'Unknown'
                domain = 'Unknown'
            # get assembly information
            assembly_ref = assembly_ref_dict[genome_name]
            sequence = ''.join([str(i) for i in read_sequence(assemblies[assembly_ref]['paths'][0], format='fasta')])
            sequence = sequence.upper()
            dna_size = len(sequence)
            gc_content = sum([(i == 'G') or (i == 'C') for i in sequence]) / dna_size
            # get ORF features
            cdss = []
            mrnas = []
            features = []
            for feature_name, row in genome_annotations.iterrows():
                # get general gene information
                fid = feature_name
                strandedness = '+' if row['strandedness'] == 1 else '-'
                location = [[row['scaffold'], row['start_position'], strandedness,
                             row['end_position']-row['start_position']]]
                aliases = []
                # get gene sequence
                dna = str(genes_nucl[feature_name])
                md5 = hashlib.md5(dna.encode()).hexdigest()
                prot = str(genes_aa[feature_name])
                # get mrna and cds data
                cds_id = fid + "_CDS"
                mrna_id = fid + "_mRNA"
                if not pd.isna(row['kegg_hit']):
                    product = ' '.join(row['kegg_hit'].split()[1:]).split(';')[0]
                else:
                    product = ''
                # define feature
                feature = {"id": fid, "location": location, "type": "gene", "aliases": aliases, "md5": md5,
                           "dna_sequence": dna, "dna_sequence_length": len(dna), "protein_translation": prot,
                           "protein_translation_length": len(prot), "cdss": [cds_id], "mrans": [mrna_id]}
                if product != '':
                    feature["function"] = product
                features.append(feature)
                # define cds
                cds = {"id": cds_id, "location": location, "md5": md5, "parent_gene": fid, "parent_mrna": mrna_id,
                       "function": (product if product else ""), "ontology_terms": {}, "protein_translation": prot,
                       "protein_translation_length": len(prot), "aliases": aliases}
                cdss.append(cds)
                # define mrna
                mrna = {"id": mrna_id, "location": location, "md5": md5,
                        "parent_gene": fid, "cds": cds_id}
                mrnas.append(mrna)
            # TODO: get rRNA features
            # TODO: get tRNA features
            genome = {"id": "Unknown",
                      "features": features,
                      "scientific_name": scientific_name,
                      "domain": domain,
                      "genetic_code": 0,  # might be able to get this from prodigal calls
                      "assembly_ref": assembly_ref,
                      "cdss": cdss,
                      "mrnas": mrnas,
                      "source": "DRAM annotation pipeline",
                      "gc_content": gc_content,
                      "dna_size": dna_size,
                      "reference_annotation": 0}

            info = genome_util.save_one_genome({"workspace": params["workspace_name"],
                                                "name": '%s_genome' % genome_name,
                                                "data": genome,
                                                "provenance": ctx.provenance()})["info"]
            genome_ref = '%s/%s/%s' % (info[6], info[0], info[4])
            genome_set_elements['%s_genome' % genome_name] = dict()
            genome_set_elements['%s_genome' % genome_name]['ref'] = genome_ref
            output_objects.append({"ref": genome_ref,
                                   "description": 'Annotated Genome'})
            genome_ref_list.append(genome_ref)

        # make genome set
        provenance = [{}]
        if 'provenance' in ctx:
            provenance = ctx['provenance']
        # add additional info to provenance here, in this case the input data object reference
        provenance[0]['input_ws_objects'] = []
        for ass_ref in genome_ref_list:
            provenance[0]['input_ws_objects'].append(ass_ref)
        provenance[0]['service'] = 'kb_SetUtilities'
        provenance[0]['method'] = 'KButil_Batch_Create_GenomeSet'
        output_genomeSet_obj = {'description': params['desc'],
                                'elements': genome_set_elements
                                }
        output_genomeSet_name = params['output_name']
        new_obj_info = wsClient.save_objects({'workspace': params['workspace_name'],
                                              'objects': [{'type': 'KBaseSearch.GenomeSet',
                                                           'data': output_genomeSet_obj,
                                                           'name': output_genomeSet_name,
                                                           'meta': {},
                                                           'provenance': provenance
                                                           }]
                                              })[0]
        # genome_set_ref = '%s/%s/%s' % (new_obj_info[6], new_obj_info[0], new_obj_info[4])
        # output_objects.append({"ref": genome_set_ref,
        #                        "description": params['desc']})

        # generate report
        html_file = os.path.join(output_dir, 'product.html')
        # move html to main directory uploaded to shock so kbase can find it
        os.rename(os.path.join(distill_output_dir, 'product.html'), html_file)
        report_shock_id = datafile_util.file_to_shock({
            'file_path': output_dir,
            'pack': 'zip'
        })['shock_id']
        html_report = [{
            'shock_id': report_shock_id,
            'name': os.path.basename(html_file),
            'label': os.path.basename(html_file),
            'description': 'DRAM product.'
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
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
