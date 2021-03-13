import os
import tarfile
import pandas as pd
import datetime
from skbio import read as read_sequence
import hashlib

from mag_annotator.annotate_bins import annotate_bins
from mag_annotator.summarize_genomes import summarize_genomes


def annotate_contigs_w_dram(fasta_locs, output_dir, min_contig_size):
    output_files = list()

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
    genes_gff_loc = os.path.join(output_dir, 'genes.gff')
    output_files.append({
        'path': genes_gff_loc,
        'name': 'genes.gff',
        'label': 'genes.gff',
        'description': 'GFF file of all DRAM annotations'
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
    genome_gbks_loc = os.path.join(output_dir, 'genbank.tar.gz')
    tar = tarfile.open(genome_gbks_loc, "w:gz")
    for name in os.listdir(os.path.join(output_dir, 'genbank')):
        tar.add(os.path.join(output_dir, 'genbank', name))
    tar.close()
    output_files.append({
        'path': genome_gbks_loc,
        'name': 'genbank.tar.gz',
        'label': 'genbank.tar.gz',
        'description': 'Compressed folder of output genbank files?'
    })

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

    dram_file_locs = {'annotations': annotations_tsv_loc,
                      'genes_faa': genes_faa_loc,
                      'genes_fna': genes_fna_loc,
                      'distill_product': os.path.join(distill_output_dir, 'product.html')}

    return dram_file_locs, output_files


def generate_genomes(annotations, genes_nucl_loc, genes_aa_loc, assembly_ref_dict, assemblies, workspace, provenance):
    genes_nucl = {i.metadata['id']: i for i in read_sequence(genes_nucl_loc, format='fasta')}
    genes_aa = {i.metadata['id']: i for i in read_sequence(genes_aa_loc, format='fasta')}
    genome_objects = list()
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
                  "assembly_ref": assembly_ref,
                  "cdss": cdss,
                  "mrnas": mrnas,
                  "source": "DRAM annotation pipeline",
                  "gc_content": gc_content,
                  "dna_size": dna_size,
                  "reference_annotation": 0}

        genome_object_name = '%s_genome' % genome_name
        genome_object = {"workspace": workspace,
                         "name": genome_object_name,
                         "data": genome,
                         "provenance": provenance}
        genome_objects.append(genome_object)
    return genome_objects


def add_ontology_terms(annotations, description, version, workspace, workspace_url, genome_ref_dict):
    ontology_events = []
    for genome_name, genome_annotations in annotations.groupby('fasta'):
        # add ontology terms
        # TODO: also add EC and other ontologies

        kegg_ontology_terms = dict()
        terms = list()
        for gene, row in genome_annotations.iterrows():
            if not pd.isna(row['kegg_id']):
                kegg_terms = row['kegg_id'].split(',')
                terms += kegg_terms
                kegg_ontology_terms[gene] = [{'term': i} for i in kegg_terms]

        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        kegg_ontology = {
            'event_id': description,
            'description': description,
            'ontology_id': 'KO',
            'method': 'DRAM',  # from above
            'method_version': version,
            "timestamp": timestamp,
            'ontology_terms': kegg_ontology_terms,
            'gene_count': len(annotations),  # not used in the api
            'term_count': len(set(terms))  # not used in the api
        }

        genome_object_name = '%s_genome' % genome_name
        genome_ref = genome_ref_dict[genome_object_name]

        ontology_event = {
            "input_ref": genome_ref,
            "output_name": genome_object_name,
            "input_workspace": workspace,
            "workspace-url": workspace_url,
            "events": [kegg_ontology],
            "timestamp": timestamp,
            "output_workspace": workspace,
            "save": 1
        }

        ontology_events.append(ontology_event)
    return ontology_events
