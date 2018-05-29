import utils
import os
import pytest
import testinfra.utils.ansible_runner


"""
ASC-230: Reboot the nova +log hosts and ensure configuration persistence
RPC 10+ manual test 3
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('compute-infra_hosts')[:1]

# attach the utility container:
attach_utility_container = "lxc-attach -n `lxc-ls -1 | grep utility | head -n 1` -- bash -c "


@pytest.mark.test_id('6f87ed59-5a04-11e8-80bf-6c96cfdb2e43')
@pytest.mark.jira('asc-230')
@pytest.mark.order1
@pytest.mark.testinfra_hosts(testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('nova_compute'))
def test_reboot_all_nova_hosts(host):
    """Reboot all nova compute host"""
    utils.reboot_server(host)


@pytest.mark.test_id('854ed66e-6038-11e8-9521-6c96cfdb2e43')
@pytest.mark.jira('asc-230')
@pytest.mark.order2
@pytest.mark.testinfra_hosts(testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('nova_compute')[:1])
def test_nova_compute_service_is_enabled(host):
    """Verify the compute service on the rebooted host is up and enabled """

    utils.verify_nova_compute_service_is_enabled(host)


@pytest.mark.test_id('ce5298e4-5fbd-11e8-a634-9cdc71d6c128')
@pytest.makr.jira('asc-230')
@pytest.mark.order3
@pytest.mark.testinfra_hosts(testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('logging_hosts'))
def test_reboot_log_hosts(host):
    """Reboot all logging hosts"""

    utils.reboot_server(host)

    # Verify the logging hosts are backup and running
    utils.verify_container_is_accessable('rsyslog', host)


@pytest.mark.test_id('c85e53b8-635c-11e8-a260-6c96cfdb2e43')
@pytest.makr.jira('asc-231')
@pytest.mark.order4
def test_reboot_infra_hosts(host):
    """Reboot all infra hosts in backward order"""

    for i in range(3, 1, -1):
        utils.reboot_server(host[:3])

        # Verify the host is backup and running
        container = "infra{}_utility_container".format(i)
        utils.verify_container_is_accessable(container, host)
