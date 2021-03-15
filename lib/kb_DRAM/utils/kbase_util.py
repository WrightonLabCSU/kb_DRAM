import os

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.DataFileUtilClient import DataFileUtil


def generate_product_report(callback_url, workspace_name, output_dir, product_html_loc, output_files,
                            output_objects=None):
    # setup utils
    datafile_util = DataFileUtil(callback_url)
    report_util = KBaseReport(callback_url)

    # move html to main directory uploaded to shock so kbase can find it
    html_file = os.path.join(output_dir, 'product.html')
    os.rename(product_html_loc, html_file)
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
                                                 'workspace_name': workspace_name,
                                                 'html_links': html_report,
                                                 'direct_html_link_index': 0,
                                                 'file_links': [value for key, value in output_files.items()
                                                                if value['path'] is not None],
                                                 'objects_created': output_objects,
                                                 })
    return report
