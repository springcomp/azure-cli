# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# AZURE CLI VM TEST DEFINITIONS
import json
import os
import platform
import tempfile
import time
import unittest
from unittest import mock
import uuid

from azure.cli.testsdk.exceptions import JMESPathCheckAssertionError
from knack.util import CLIError
from azure.cli.testsdk.scenario_tests import AllowLargeResponse, record_only, live_only
from azure.cli.core.azclierror import ArgumentUsageError, RequiredArgumentMissingError, MutuallyExclusiveArgumentError
from azure.cli.core.profiles import ResourceType
from azure.cli.testsdk import (
    ScenarioTest, ResourceGroupPreparer, LiveScenarioTest, api_version_constraint,
    StorageAccountPreparer, JMESPathCheck, StringContainCheck, VirtualNetworkPreparer, KeyVaultPreparer)
from azure.cli.testsdk.constants import AUX_SUBSCRIPTION, AUX_TENANT
TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

TEST_SSH_KEY_PUB = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCbIg1guRHbI0lV11wWDt1r2cUdcNd27CJsg+SfgC7miZeubtwUhbsPdhMQsfDyhOWHq1+ZL0M+nJZV63d/1dhmhtgyOqejUwrPlzKhydsbrsdUor+JmNJDdW01v7BXHyuymT8G4s09jCasNOwiufbP/qp72ruu0bIA1nySsvlf9pCQAuFkAnVnf/rFhUlOkhtRpwcq8SUNY2zRHR/EKb/4NWY1JzR4sa3q2fWIJdrrX0DvLoa5g9bIEd4Df79ba7v+yiUBOS0zT2ll+z4g9izHK3EO5d8hL4jYxcjKs+wcslSYRWrascfscLgMlMGh0CdKeNTDjHpGPncaf3Z+FwwwjWeuiNBxv7bJo13/8B/098KlVDl4GZqsoBCEjPyJfV6hO0y/LkRGkk7oHWKgeWAfKtfLItRp00eZ4fcJNK9kCaSMmEugoZWcI7NGbZXzqFWqbpRI7NcDP9+WIQ+i9U5vqWsqd/zng4kbuAJ6UuKqIzB0upYrLShfQE3SAck8oaLhJqqq56VfDuASNpJKidV+zq27HfSBmbXnkR/5AK337dc3MXKJypoK/QPMLKUAP5XLPbs+NddJQV7EZXd29DLgp+fRIg3edpKdO7ZErWhv7d+3Kws+e1Y+ypmR2WIVSwVyBEUfgv2C8Ts9gnTF4pNcEY/S2aBicz5Ew2+jdyGNQQ== test@example.com\n"
TEST_SSH_KEY_PUB_2 = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCof7rG2sYVyHSDPp4lbrq5zu8N8D7inS4Qb+ZZ5Kh410znTcoVJSNsLOhrM2COxg5LXca3DQMBi4S/V8UmMnwxwDVf38GvU+0QVDR6vSO6lPlj2OpPLk4OEdTv3qcj/gpEBvv1RCacpFuu5bL546r4BqG4f0dJXqBd5tT4kjpO9ytOZ1Wkg8tA35UvbucVAsDBfOZ5GtsnflPtKCY9h20LeXEjyDZ8eFzAGH/vNrfWPiWWznwN9EoPghIQHCiC0mnJgdsABraUzeTTMjxahi0DXBxb5dsKd6YbJxQw/V+AohVMPfPvs9y95Aj7IxM2zrtgBswC8bT0z678svTJSFX9 test@example.com"


def _write_config_file(user_name):

    public_key = ('ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC8InHIPLAu6lMc0d+5voyXqigZfT5r6fAM1+FQAi+mkPDdk2hNq1BG0Bwfc88G'
                  'm7BImw8TS+x2bnZmhCbVnHd6BPCDY7a+cHCSqrQMW89Cv6Vl4ueGOeAWHpJTV9CTLVz4IY1x4HBdkLI2lKIHri9+z7NIdvFk7iOk'
                  'MVGyez5H1xDbF2szURxgc4I2/o5wycSwX+G8DrtsBvWLmFv9YAPx+VkEHQDjR0WWezOjuo1rDn6MQfiKfqAjPuInwNOg5AIxXAOR'
                  'esrin2PUlArNtdDH1zlvI4RZi36+tJO7mtm3dJiKs4Sj7G6b1CjIU6aaj27MmKy3arIFChYav9yYM3IT')
    config = {
        'username': user_name,
        'ssh_key': public_key
    }
    _, config_file = tempfile.mkstemp()
    with open(config_file, 'w') as outfile:
        json.dump(config, outfile)
    return config_file


@api_version_constraint(ResourceType.MGMT_COMPUTE, min_api='2017-03-30')
class VMZoneScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_vm_zone', location='eastus2')
    @AllowLargeResponse(size_kb=99999)
    def test_vm_create_zones(self, resource_group, resource_group_location):

        self.kwargs.update({
            'zones': '2',
            'vm': 'vm123',
            'ip': 'vm123ip'
        })
        self.cmd('vm create -g {rg} -n {vm} --admin-username clitester --admin-password PasswordPassword1! --image debian --zone {zones} --public-ip-address {ip} --nsg-rule NONE',
                 checks=self.check('zones', '{zones}'))
        self.cmd('network public-ip show -g {rg} -n {ip}',
                 checks=self.check('zones[0]', '{zones}'))
        # Test VM's specific table output
        result = self.cmd('vm show -g {rg} -n {vm} -otable')
        table_output = set(result.output.splitlines()[2].split())
        self.assertTrue(set([resource_group_location, self.kwargs['zones']]).issubset(table_output))

    @ResourceGroupPreparer(name_prefix='cli_test_vm_zone', location='westus')
    @AllowLargeResponse(size_kb=99999)
    def test_vm_error_on_zone_unavailable(self, resource_group, resource_group_location):
        try:
            self.cmd('vm create -g {rg} -n vm1 --admin-username clitester --admin-password PasswordPassword1! --image debian --zone 1')
        except Exception as ex:
            self.assertTrue('availability zone is not yet supported' in str(ex))

    @unittest.skip('Can\'t test due to no qualified subscription')
    @ResourceGroupPreparer(name_prefix='cli_test_vmss_zones', location='eastus2')
    @AllowLargeResponse(size_kb=99999)
    def test_vmss_create_single_zone(self, resource_group, resource_group_location):

        self.kwargs.update({
            'zones': '2',
            'vmss': 'vmss123'
        })
        self.cmd('vmss create -g {rg} -n {vmss} --admin-username clitester --admin-password PasswordPassword1! --image debian --zones {zones}')
        self.cmd('vmss show -g {rg} -n {vmss}',
                 checks=self.check('zones[0]', '{zones}'))
        result = self.cmd('vmss show -g {rg} -n {vmss} -otable')
        table_output = set(result.output.splitlines()[2].split())
        self.assertTrue(set([resource_group_location, self.kwargs['vmss'], self.kwargs['zones']]).issubset(table_output))
        result = self.cmd('vmss list -g {rg} -otable')
        table_output = set(result.output.splitlines()[2].split())
        self.assertTrue(set([resource_group_location, self.kwargs['vmss'], self.kwargs['zones']]).issubset(table_output))

        self.cmd('network lb list -g {rg}', checks=[
            self.check('[0].sku.name', 'Standard')
        ])
        self.cmd('network public-ip list -g {rg}', checks=[
            self.check('[0].sku.name', 'Standard'),
            self.check('[0].zones', ['2'])
        ])

    @unittest.skip('Can\'t test due to no qualified subscription')
    @ResourceGroupPreparer(name_prefix='cli_test_vmss_zones', location='eastus2')
    @AllowLargeResponse(size_kb=99999)
    def test_vmss_create_x_zones(self, resource_group, resource_group_location):

        self.kwargs.update({
            'zones': '1 2 3',
            'vmss': 'vmss123',
            'lb': 'vmss123LB',  # default name chosen by the create
            'rule': 'LBRule',  # default name chosen by the create,
            'nsg': 'vmss123NSG',  # default name chosen by the create
            'probe': 'LBProbe'
        })
        self.cmd('vmss create -g {rg} -n {vmss}  --admin-username clitester --admin-password PasswordPassword1! --image debian --zones {zones} --vm-sku Standard_D1_V2')
        self.cmd('vmss show -g {rg} -n {vmss}',
                 checks=self.check('zones', ['1', '2', '3']))
        result = self.cmd('vmss show -g {rg} -n {vmss} -otable')
        table_output = set(result.output.splitlines()[2].split())
        self.assertTrue(set([resource_group_location, self.kwargs['vmss']] + self.kwargs['zones'].split()).issubset(table_output))

        self.cmd('network lb list -g {rg}', checks=[
            self.check('[0].sku.name', 'Standard')
        ])
        self.cmd('network public-ip list -g {rg}', checks=[
            self.check('[0].sku.name', 'Standard'),
            self.check('[0].zones', None)
        ])

        # Now provision a web server
        self.cmd('network lb probe create -g {rg} --lb-name {lb} -n {probe} --protocol http --port 80 --path /')
        self.cmd('network lb rule create -g {rg} --lb-name {lb} -n {rule} --protocol tcp --frontend-port 80 --backend-port 80 --probe-name {probe}')
        self.cmd('network nsg rule create -g {rg} --nsg-name {nsg} -n allowhttp --priority 4096 --destination-port-ranges 80 --protocol Tcp')

        self.cmd('vmss extension set -g {rg} --vmss-name {vmss} -n customScript --publisher Microsoft.Azure.Extensions --settings "{{\\"commandToExecute\\": \\"apt-get update && sudo apt-get install -y nginx\\"}}" --version 2.0')
        self.cmd('vmss update-instances -g {rg} -n {vmss} --instance-ids "*"')

        # verify the server works
        result = self.cmd('vmss list-instance-connection-info -g {rg} -n {vmss} -o tsv')
        time.sleep(15)  # 15 seconds should be enough for nginx started(Skipped under playback mode)
        import requests
        r = requests.get('http://' + result.output.split(':')[0])
        self.assertTrue('Welcome to nginx' in str(r.content))

    @ResourceGroupPreparer(name_prefix='cli_test_disk_zones', location='eastus2')
    def test_vm_disk_create_zones(self, resource_group, resource_group_location):

        self.kwargs.update({
            'zones': '2',
            'disk': 'disk123',
            'size': 1
        })
        self.cmd('disk create -g {rg} -n {disk} --size-gb {size} --zone {zones}', checks=[
            self.check('zones[0]', '{zones}')
        ])
        self.cmd('disk show -g {rg} -n {disk}',
                 checks=self.check('zones[0]', '{zones}'))
        result = self.cmd('disk show -g {rg} -n {disk} -otable')
        table_output = set(result.output.splitlines()[2].split())
        self.assertTrue(set([resource_group, resource_group_location, self.kwargs['disk'], self.kwargs['zones'], str(self.kwargs['size']), 'Premium_LRS']).issubset(table_output))
        result = self.cmd('disk list -g {rg} -otable')
        table_output = set(result.output.splitlines()[2].split())
        self.assertTrue(set([resource_group, resource_group_location, self.kwargs['disk'], self.kwargs['zones']]).issubset(table_output))


if __name__ == '__main__':
    unittest.main()