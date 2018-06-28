import pytest_rpc as helpers
import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]

utility_container = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
                     "-- bash -c '. /root/openrc ; ")

random_str = helpers.generate_random_string(6)
instance_name = "test_instance_{}".format(random_str)
image_name = 'Cirros-0.3.5'
getway_net = 'GATEWAY_NET'
private_net = 'PRIVATE_NET'
flavor = 'm1.tiny'
floating_ip_name = None


@pytest.mark.test_id('bea6da62-7968-11e8-a634-9cdc71d6c128')
@pytest.mark.jira('asc-254')
@pytest.mark.run(order=1)
def test_create_instance_from_image(host):
    """Create a test instance from image"""
    image_id = helpers.get_id_by_name('image', image_name, host)
    assert image_id is not None

    network_id = helpers.get_id_by_name('network', private_net, host)
    assert network_id is not None

    cmd = "{} openstack server create --image {} --flavor {} --nic net-id={} {}'".format(utility_container, image_id,
                                                                                         flavor, network_id,
                                                                                         instance_name)
    host.run_expect([0], cmd)

    assert (helpers.verify_asset_in_list('server', instance_name, host))
    assert (helpers.get_expected_value('server', instance_name, 'status', 'ACTIVE', host))
    assert (helpers.get_expected_value('server', instance_name, 'OS-EXT-STS:power_state', 'Running', host))


@pytest.mark.test_id('a97e1202-796a-11e8-ba13-525400bd8005')
@pytest.mark.jira('asc-254')
@pytest.mark.run(order=2)
def test_create_floating_ip(host):
    """Create floating IP"""

    global floating_ip_name
    floating_ip_name = helpers.create_floating_ip(getway_net, host)
    assert (floating_ip_name is not None)

    # Before being assigned, the floating IP status should be 'DOWN'
    assert (helpers.get_expected_value('floating ip', floating_ip_name, 'status', 'DOWN', host))


@pytest.mark.test_id('ab24ffbd-798b-11e8-a2b2-6c96cfdb2e43')
@pytest.mark.jira('asc-254')
@pytest.mark.run(order=3)
def test_assign_floating_ip_to_instance(host):
    """Assign floating IP to an instance/server"""
    assert (floating_ip_name is not None)  # floating_ip_name is same as the floating IP address

    instance_id = helpers.get_id_by_name('server', instance_name, host)
    assert (instance_id is not None)

    cmd = "{} openstack server add floating ip {} {}'".format(utility_container, instance_id, floating_ip_name)

    host.run_expect([0], cmd)

    # After being assigned, the floating IP status should be 'ACTIVE'
    assert (helpers.get_expected_value('floating ip', floating_ip_name, 'status', 'ACTIVE', host))


@pytest.mark.test_id('e3985ee1-798b-11e8-ad0e-6c96cfdb2e43')
@pytest.mark.jira('asc-254')
@pytest.mark.run(order=4)
def test_ping_floating_ip(host):
    """Verify the newly created and assigned floating IP address can be pinged"""
    assert (floating_ip_name is not None)  # floating_ip_name is same as the floating IP address

    cmd = "{} ping -c1 {}'".format(utility_container, floating_ip_name)
    host.run_expect([0], cmd)

    # Tear down:
    helpers.delete_it('server', instance_name, host)
    helpers.delete_floating_ip(floating_ip_name, host)
