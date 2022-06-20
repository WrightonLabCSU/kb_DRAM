/*
A KBase module: kb_DRAM
*/

module dram_beta {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_kb_dram_annotate(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;
    funcdef run_kb_dram_annotate_genome(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;
    funcdef run_kb_dramv_annotate(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;
};
