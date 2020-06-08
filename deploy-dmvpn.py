from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks.networking import netmiko_send_config
from nornir.plugins.tasks.data import load_yaml
from nornir.plugins.tasks.text import template_file

nr = InitNornir(config_file="config.yaml")

def load_vars(task):
    data = task.run(task=load_yaml,file=f'./host_vars/{task.host}.yaml')
    task.host["facts"] = data.result
    group_data = task.run(task=load_yaml,file=f'./group_vars/all.yaml')
    task.host["group_facts"] = group_data.result
    config_vrf(task)


def config_vrf(task):
    vrf_template = task.run(task=template_file,name="Buildling VRF Configuration",template="vrf.j2", path="./templates")
    task.host["vrf"] = vrf_template.result
    vrf_output = task.host["vrf"]
    vrf_send = vrf_output.splitlines()
    task.run(task=netmiko_send_config, name="Pushing VRF Commands", config_commands=vrf_send)
    config_dmvpn(task)

def config_dmvpn(task):
    dmvpn_template = task.run(task=template_file,name="Buildling DMVPN Configuration",template="dmvpn.j2", path="./templates")
    task.host["dmvpn"] = dmvpn_template.result
    dmvpn_output = task.host["dmvpn"]
    dmvpn_send = dmvpn_output.splitlines()
    task.run(task=netmiko_send_config, name="Pushing DMVPN Commands", config_commands=dmvpn_send)
    config_bgp(task)


def config_bgp(task):
    bgp_template = task.run(task=template_file,name="Buildling BGP Configuration",template="bgp.j2", path="./templates")
    task.host["bgp"] = bgp_template.result
    bgp_output = task.host["bgp"]
    bgp_send = bgp_output.splitlines()
    task.run(task=netmiko_send_config, name="Pushing BGP Commands", config_commands=bgp_send)



filtered = nr.filter(dmvpn="yes")
result=filtered.run(task=load_vars)
print_result(result)
