import os
import tarfile
import pandas as pd
import datetime
from skbio import read as read_sequence
import hashlib
import re


def get_annotation_files(output_dir, output_files=None):
    if output_files is None:
        output_files = dict()

    annotations_tsv_loc = os.path.join(output_dir, 'annotations.tsv')
    output_files['annotations'] = {'path': annotations_tsv_loc,
                                   'name': 'annotations.tsv',
                                   'label': 'annotations.tsv',
                                   'description': 'DRAM annotations in a tab separate table format'}
    genes_fna_loc = os.path.join(output_dir, 'genes.fna')
    if not os.path.exists(genes_fna_loc):
        genes_fna_loc = None
    output_files['genes_fna'] = {'path': genes_fna_loc,
                                 'name': 'genes.fna',
                                 'label': 'genes.fna',
                                 'description': 'Genes as nucleotides predicted by DRAM with brief annotations'}
    genes_faa_loc = os.path.join(output_dir, 'genes.faa')
    output_files['genes_faa'] = {'path': genes_faa_loc,
                                 'name': 'genes.faa',
                                 'label': 'genes.faa',
                                 'description': 'Genes as amino acids predicted by DRAM with brief annotations'}
    genes_gff_loc = os.path.join(output_dir, 'genes.gff')
    if not os.path.exists(genes_gff_loc):
        genes_gff_loc = None
    output_files['genes_gff'] = {'path': genes_gff_loc,
                                 'name': 'genes.gff',
                                 'label': 'genes.gff',
                                 'description': 'GFF file of all DRAM annotations'}
    rrnas_loc = os.path.join(output_dir, 'rrnas.tsv')
    if not os.path.exists(rrnas_loc):
        rrnas_loc = None
    output_files['rrnas'] = {'path': rrnas_loc,
                             'name': 'rrnas.tsv',
                             'label': 'rrnas.tsv',
                             'description': 'Tab separated table of rRNAs as detected by barrnap'}
    trnas_loc = os.path.join(output_dir, 'trnas.tsv')
    if not os.path.exists(trnas_loc):
        trnas_loc = None
    output_files['trnas'] = {'path': trnas_loc,
                             'name': 'trnas.tsv',
                             'label': 'trnas.tsv',
                             'description': 'Tab separated table of tRNAs as detected by tRNAscan-SE'}
    gbks_loc = os.path.join(output_dir, 'genbank')
    gbk_loc = os.path.join(output_dir, 'scaffolds.gbk')
    if os.path.exists(gbks_loc):
        genome_gbks_loc = os.path.join(output_dir, 'genbank.tar.gz')
        tar = tarfile.open(genome_gbks_loc, "w:gz")
        for name in os.listdir(gbks_loc):
            tar.add(os.path.join(output_dir, 'genbank', name))
        tar.close()
        output_files['gbks'] = {'path': genome_gbks_loc,
                                'name': 'genbank.tar.gz',
                                'label': 'genbank.tar.gz',
                                'description': 'Compressed folder of output genbank files'}
    elif os.path.exists(gbk_loc):
        output_files['gbks'] = {'path': gbk_loc,
                                'name': 'scaffolds.gbk',
                                'label': 'scaffolds.gbk',
                                'description': 'Genbank file with annotations for all '}
    else:
        pass
    return output_files


def get_distill_files(distill_output_dir, output_files=None):
    if output_files is None:
        output_files = dict()
    product_tsv_loc = os.path.join(distill_output_dir, 'product.tsv')
    output_files['product_tsv'] = {'path': product_tsv_loc,
                                   'name': 'product.tsv',
                                   'label': 'product.tsv',
                                   'description': 'DRAM product in tabular format'}
    metabolism_summary_loc = os.path.join(distill_output_dir, 'metabolism_summary.xlsx')
    output_files['metabolism_summary'] = {'path': metabolism_summary_loc,
                                          'name': 'metabolism_summary.xlsx',
                                          'label': 'metabolism_summary.xlsx',
                                          'description': 'DRAM metabolism summary tables'}
    genome_stats_loc = os.path.join(distill_output_dir, 'genome_stats.tsv')
    output_files['genome_stats'] = {'path': genome_stats_loc,
                                    'name': 'genome_stats.tsv',
                                    'label': 'genome_stats.tsv',
                                    'description': 'DRAM genome statistics table'}
    return output_files


def generate_genomes(annotations, genes_nucl_loc, genes_aa_loc, assembly_ref_dict, assemblies, workspace, provenance, dram_sufix='DRAM'):
    genes_nucl = {i.metadata['id']: i for i in read_sequence(genes_nucl_loc, format='fasta')}
    genes_aa = {i.metadata['id']: i for i in read_sequence(genes_aa_loc, format='fasta')}
    genome_objects = list()
    for fasta_name, genome_annotations in annotations.groupby('fasta'):
        # set scientific name, domain and genetic code
        if 'bin_taxonomy' in genome_annotations.columns:  # assuming gtdb taxa strings
            scientific_name = genome_annotations['bin_taxonomy'].iloc[0]  # not really the scientific name, whatever
            domain = scientific_name.split[';'][0]
        else:
            scientific_name = 'Unknown'
            domain = 'Unknown'
        # get assembly information
        assembly_ref = assembly_ref_dict[fasta_name]
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
                         row['end_position'] - row['start_position']]]
            aliases = []
            # get gene sequence
            dna = str(genes_nucl[feature_name])
            md5 = hashlib.md5(dna.encode()).hexdigest()
            prot = str(genes_aa[feature_name])
            # get mrna and cds data
            cds_id = fid + "_CDS"
            mrna_id = fid + "_mRNA"
            # get product
            if not pd.isna(row['kegg_hit']):
                product = row['kegg_hit']
            else:
                product = ''
            # define feature
            feature = {"id": fid, "location": location, "type": "gene", "aliases": aliases, "md5": md5,
                       "dna_sequence": dna, "dna_sequence_length": len(dna), "protein_translation": prot,
                       "protein_translation_length": len(prot), "cdss": [cds_id], "mrans": [mrna_id],
                       "function": product, "ontology_terms": {}}
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
                  "assembly_ref": '_'.join([assembly_ref, dram_sufix]), # Added this just to double check things don't get overwritten
                  "cdss": cdss,
                  "mrnas": mrnas,
                  "source": "DRAM annotation pipeline",
                  "gc_content": gc_content,
                  "dna_size": dna_size,
                  "reference_annotation": 0}

        genome_object = {"workspace": workspace,
                         "name": '_'.join([fasta_name, dram_sufix]),
                         "data": genome,
                         "provenance": provenance}
        genome_objects.append(genome_object)
    return genome_objects


def add_ontology_terms(annotations, description, version, workspace, workspace_url, genome_ref_dict):
    ontology_events = []
    for fasta_name, genome_annotations in annotations.groupby('fasta'):
        # add ontology terms
        # TODO: also add EC and other ontologies

        kegg_ontology_terms = dict()
        ko_terms = list()
        ec_ontology_terms = dict()
        ec_terms = list()
        for gene, row in genome_annotations.iterrows():  # this is slow, could probably be an apply
            # get kos
            if not pd.isna(row['ko_id']):
                kegg_terms = row['ko_id'].split(',')
                ko_terms += kegg_terms
                kegg_ontology_terms[gene] = [{'term': i} for i in kegg_terms]
            # get ECs
            # TODO: be able to capute EC's with - (i.e. EC 3.2.1.-)
            for label, value in row.items():
                if not pd.isna(value) and ('_hit' in label):
                    current_ec_terms = [i.replace(' ', ':') for i in re.findall(r"EC[ :]\d+.\d+.\d+.\d+", value)]
                    ec_terms += current_ec_terms
                    ec_ontology_terms[gene] = [{'term': i} for i in current_ec_terms]

        kegg_timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        kegg_description = '%s_%s_%s' % (description, 'KO', kegg_timestamp)
        kegg_ontology = {
            'description': kegg_description,
            'ontology_id': 'KO',
            'method': 'DRAM',  # from above
            'method_version': version,
            "timestamp": kegg_timestamp,
            'ontology_terms': kegg_ontology_terms,
            'gene_count': len(annotations),  # not used in the api
            'term_count': len(set(ko_terms))  # not used in the api
        }

        ec_timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        ec_description = '%s_%s_%s' % (description, 'EC', kegg_timestamp)
        ec_ontology = {
            'description': ec_description,
            'ontology_id': 'EC',
            'method': 'DRAM',  # from above
            'method_version': version,
            "timestamp": ec_timestamp,
            'ontology_terms': ec_ontology_terms,
            'gene_count': len(annotations),  # not used in the api
            'term_count': len(set(ec_terms))  # not used in the api
        }

        # this is because when annotating assemblies we rename genomes based on input name and _DRAM
        # TODO: turn '%s_DRAM' in an argument with desired replacement or None for no replacement
        genome_name = None
        if isinstance(fasta_name,float):
            fasta_name = str(fasta_name)
        # genome_ref_dict = {"ap1.000", 'ap3.0000', 'ap1.', 'ap1.noe','ap1._DRAM'}
        # fasta_name = "ap1."
        likly_genome_name = [i for i in genome_ref_dict if re.fullmatch(f"{fasta_name}0*[_DRAM]?", i)]
        if len(likly_genome_name) == 1:
            genome_name = likly_genome_name[0]
        elif len(likly_genome_name) > 1:
            raise ValueError('Fasta name %s is ambiguous in genome_ref_dict with keys %s, note that names ending in 0s or \"_DRAM\" have these removed from the name' %
                         (fasta_name, ', '.join(genome_ref_dict.keys())))
        else:
            raise ValueError('Fasta name %s not found in genome_ref_dict with keys %s' %
                         (fasta_name, ', '.join(genome_ref_dict.keys())))
        #  if fasta_name in genome_ref_dict:
        #      genome_name = fasta_name
        #  elif '%s_DRAM' % fasta_name in genome_ref_dict:
        #      genome_name = '%s_DRAM' % fasta_name
        #  else:
        #      #Deal with the possiblity that fasta_name was a float with trailing zeros

        #      for i in range(0,10):
        #          fasta_name += "0"
        #          if fasta_name in genome_ref_dict:
        #              genome_name = fasta_name
        #              break
        #          elif '%s_DRAM' % fasta_name in genome_ref_dict:
        #              genome_name = '%s_DRAM' % fasta_name
        #              break

        genome_ref = genome_ref_dict[genome_name]
        ontology_event = {
            "input_ref": genome_ref,
            "output_name": genome_name,
            "input_workspace": workspace,
            "workspace-url": workspace_url,
            "events": [kegg_ontology, ec_ontology],
            "timestamp": datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),
            "output_workspace": workspace,
            "save": 1
        }

        ontology_events.append(ontology_event)
    return ontology_events


def get_viral_distill_files(distill_output_dir, output_files=None):
    if output_files is None:
        output_files = dict()
    amg_summary_loc = os.path.join(distill_output_dir, 'amg_summary.tsv')
    output_files['amg_summary'] = {'path': amg_summary_loc,
                                   'name': 'amg_summary.tsv',
                                   'label': 'amg_summary.tsv',
                                   'description': 'DRAM-v AMG summary table'}
    vmag_stats_loc = os.path.join(distill_output_dir, 'vMAG_stats.tsv')
    output_files['genome_stats'] = {'path': vmag_stats_loc,
                                    'name': 'vMAG_stats.tsv',
                                    'label': 'vMAG_stats.tsv',
                                    'description': 'DRAM-v vMAG statistics table'}
    return output_files
