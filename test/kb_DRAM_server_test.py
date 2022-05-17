# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser

from dram_beta.dram_betaImpl import dram_beta
from dram_beta.dram_betaServer import MethodContext
from dram_beta.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace
from installed_clients.AssemblyUtilClient import AssemblyUtil


class kb_DRAMTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('dram_beta'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'dram_beta',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = dram_beta(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def test_kb_dram_annotate_bad_params(self):
        # missing assembly ref
        with self.assertRaises(KeyError):
            self.serviceImpl.run_kb_dram_annotate(self.ctx, {'workspace_name': self.wsName,
                                                             'min_contig_size': 100})
        # bad min length
        with self.assertRaises(ValueError):
            self.serviceImpl.run_kb_dram_annotate(self.ctx, {'workspace_name': self.wsName,
                                                             'assembly_input_ref': '41343/4/1',
                                                             'min_contig_size': -200})

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_kb_dram_annotate_is_metagenome(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        ref = "41343/4/1"
        params = {'workspace_name': self.wsName,
                  'assembly_input_ref': ref,
                  'min_contig_size': 1000,
                  'is_metagenome': True
                  }
        ret = self.serviceImpl.run_kb_dram_annotate(self.ctx, params)
        self.assertTrue(len(ret[0]['report_name']))
        self.assertTrue(len(ret[0]['report_ref']))

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_kb_dram_annotate_test(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        ref = "41343/4/1"
        params = {'workspace_name': self.wsName,
                  'assembly_input_ref': ref,
                  'min_contig_size': 1000}
        ret = self.serviceImpl.run_kb_dram_annotate(self.ctx, params)
        self.assertTrue(len(ret[0]['report_name']))
        self.assertTrue(len(ret[0]['report_ref']))

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_kb_dram_annotate_test(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        ref = "41343/4/1"
        params = {'workspace_name': self.wsName,
                  'assembly_input_ref': ref,
                  'min_contig_size': 1000}
        ret = self.serviceImpl.run_kb_dram_annotate(self.ctx, params)
        self.assertTrue(len(ret[0]['report_name']))
        self.assertTrue(len(ret[0]['report_ref']))

    def test_what_is_fastas(self):
        assembly_util = AssemblyUtil(self.callback_url)
        fastas = assembly_util.get_fastas({'ref_lst': ['41343/11/3']})
        print(fastas)
