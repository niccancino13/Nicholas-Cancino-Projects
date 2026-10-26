# Import libraries
import datetime
from argparse import ArgumentParser
import os
import pandas as pd
import re

# Check version of FalconPy installed
try:
    from falconpy import Hosts
except ImportError as no_falconpy:
    raise SystemExit(
        "FalconPy v1.3 or greater must be installed to run this program."
        ) from no_falconpy

# Define command line args
parser = ArgumentParser()
parser.add_argument("-i", "--client_id", dest="client_id", help="Client ID to authenticate with",
                    required=True)
parser.add_argument("-o", "--output", dest="output_dir", help="Output directory to save output to",
                    default=".\\", required=True)
parser.add_argument("-s", "--client_secret", dest="client_secret", help="Client Secret to authenticate "
                                                                        "with", required=True)
parser.add_argument("-f", "--file", dest="input_file", help="File with hostnames/IPs, 1 per line",
                    required=True)
args = parser.parse_args()

# Set/create output dir and file
if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir, exist_ok=True)

#Define lists
host_ids = []
lookup_ips = []
machine_domains = []
internal_ips = []
last_seen = []
first_seen = []
external_ips = []
last_login_time = []
ou = []
tags = []
connection_ip = []
os_product = []
site = []
last_user = []
hostname = []
CS_status = []
containment_Status = []

def status_check_hostname(device_to_check):

    # Find target device
    hosts = Hosts(client_id=args.client_id, client_secret=args.client_secret, base_url="YOUR_FALCON_REGION")

    #Query by Hostname
    target_host = hosts.query_devices_by_filter(filter=f"hostname:'{device_to_check}'")
    ip_results = target_host["body"]["resources"]
    for result in ip_results:
        # Get device details per aid
        device_details = hosts.get_device_details(ids=result)

        # Store details in lists
        host_ids.append(result)
        lookup_ips.append(device_to_check)
        try:
            machine_domains.append(device_details["body"]["resources"][0]["machine_domain"])
        except KeyError:
            machine_domains.append("Not Available")
        try:
            internal_ips.append(device_details["body"]["resources"][0]["local_ip"])
        except (KeyError, TypeError):
            internal_ips.append("Not Available")
        try:
            last_seen.append(device_details["body"]["resources"][0]["last_seen"])
        except (KeyError, TypeError):
            last_seen.append("Not Available")
        try:
            first_seen.append(device_details["body"]["resources"][0]["first_seen"])
        except(KeyError, TypeError):
            first_seen.append("Not Available")
        try:
            external_ips.append(device_details["body"]["resources"][0]["external_ip"])
        except(KeyError, TypeError):
            external_ips.append("Not Available")
        try:
            last_login_time.append(device_details["body"]["resources"][0]["last_login_timestamp"])
        except(KeyError, TypeError):
            last_login_time.append("Not Available")
        try:
            ou.append(device_details["body"]["resources"][0]["ou"])
        except(KeyError, TypeError):
            ou.append("Not Available")
        try:
            tags.append(device_details["body"]["resources"][0]["tags"])
        except(KeyError, TypeError):
            tags.append("Not Available")
        try:
            connection_ip.append(device_details["body"]["resources"][0]["connection_ip"])
        except(KeyError, TypeError):
            connection_ip.append("Not Available")
        try:
            os_product.append(device_details["body"]["resources"][0]["os_product_name"])
        except(KeyError, TypeError):
            os_product.append("Not Available")
        try:
            site.append(device_details["body"]["resources"][0]["site_name"])
        except(KeyError, TypeError):
            site.append("Not Available")
        try:
            last_user.append(device_details["body"]["resources"][0]["last_login_user"])
        except(KeyError, TypeError):
            last_user.append("Not Available")
        try:
            hostname.append(device_details["body"]["resources"][0]["hostname"])
        except(KeyError, TypeError):
            hostname.append("Not Available")
        try:
            if device_details["body"]["resources"][0]["status"] == 'normal':
                containment_Status.append("No")
            else:
                containment_Status.append("Yes")
        except(KeyError, TypeError):
            containment_Status.append("Not Available")
        CS_status.append("In CrowdStrike")
        print("CS Status: Installed on",device_to_check)

    # Machine is not in CS
    if not ip_results:
        host_ids.append("Not Available")
        lookup_ips.append(device_to_check)
        machine_domains.append("Not Available")
        internal_ips.append("Not Available")
        last_seen.append("Not Available")
        first_seen.append("Not Available")
        external_ips.append("Not Available")
        last_login_time.append("Not Available")
        ou.append("Not Available")
        tags.append("Not Available")
        connection_ip.append("Not Available")
        os_product.append("Not Available")
        site.append("Not Available")
        last_user.append("Not Available")
        hostname.append("Not Available")
        CS_status.append("Not in CrowdStrike")
        containment_Status.append("Not in CrowdStrike")
        print("CS Status: Not installed on", device_to_check)

def status_check_local(device_to_check):

    # Find target device
    hosts = Hosts(client_id=args.client_id, client_secret=args.client_secret)
    #Query by Hostname
    target_host = hosts.query_devices_by_filter(filter=f"local_ip:'{device_to_check}'")
    ip_results = target_host["body"]["resources"]
    for result in ip_results:
        # Get device details per aid
        device_details = hosts.get_device_details(ids=result)

        # Store details in lists
        host_ids.append(result)
        lookup_ips.append(device_to_check)
        try:
            machine_domains.append(device_details["body"]["resources"][0]["machine_domain"])
        except KeyError:
            machine_domains.append("Not Available")
        try:
            internal_ips.append(device_details["body"]["resources"][0]["local_ip"])
        except (KeyError, TypeError):
            internal_ips.append("Not Available")
        try:
            last_seen.append(device_details["body"]["resources"][0]["last_seen"])
        except (KeyError, TypeError):
            last_seen.append("Not Available")
        try:
            first_seen.append(device_details["body"]["resources"][0]["first_seen"])
        except(KeyError, TypeError):
            first_seen.append("Not Available")
        try:
            external_ips.append(device_details["body"]["resources"][0]["external_ip"])
        except(KeyError, TypeError):
            external_ips.append("Not Available")
        try:
            last_login_time.append(device_details["body"]["resources"][0]["last_login_timestamp"])
        except(KeyError, TypeError):
            last_login_time.append("Not Available")
        try:
            ou.append(device_details["body"]["resources"][0]["ou"])
        except(KeyError, TypeError):
            ou.append("Not Available")
        try:
            tags.append(device_details["body"]["resources"][0]["tags"])
        except(KeyError, TypeError):
            tags.append("Not Available")
        try:
            connection_ip.append(device_details["body"]["resources"][0]["connection_ip"])
        except(KeyError, TypeError):
            connection_ip.append("Not Available")
        try:
            os_product.append(device_details["body"]["resources"][0]["os_product_name"])
        except(KeyError, TypeError):
            os_product.append("Not Available")
        try:
            site.append(device_details["body"]["resources"][0]["site_name"])
        except(KeyError, TypeError):
            site.append("Not Available")
        try:
            last_user.append(device_details["body"]["resources"][0]["last_login_user"])
        except(KeyError, TypeError):
            last_user.append("Not Available")
        try:
            hostname.append(device_details["body"]["resources"][0]["hostname"])
        except(KeyError, TypeError):
            hostname.append("Not Available")
        try:
            if device_details["body"]["resources"][0]["status"] == 'normal':
                containment_Status.append("No")
            else:
                containment_Status.append("Yes")
        except(KeyError, TypeError):
            containment_Status.append("Not Available")
        CS_status.append("In CrowdStrike")
        print("CS Status: Installed on",device_to_check)

    # Machine is not in CS
    if not ip_results:
        host_ids.append("Not Available")
        lookup_ips.append(device_to_check)
        machine_domains.append("Not Available")
        internal_ips.append("Not Available")
        last_seen.append("Not Available")
        first_seen.append("Not Available")
        external_ips.append("Not Available")
        last_login_time.append("Not Available")
        ou.append("Not Available")
        tags.append("Not Available")
        connection_ip.append("Not Available")
        os_product.append("Not Available")
        site.append("Not Available")
        last_user.append("Not Available")
        hostname.append("Not Available")
        CS_status.append("Not in CrowdStrike")
        containment_Status.append("Not in CrowdStrike")
        print("CS Status: NOT installed on", device_to_check)

def status_check_external(device_to_check):

    # Find target device
    hosts = Hosts(client_id=args.client_id, client_secret=args.client_secret)
    #Query by Hostname
    target_host = hosts.query_devices_by_filter(filter=f"external_ip:'{device_to_check}'")
    ip_results = target_host["body"]["resources"]
    for result in ip_results:
        # Get device details per aid
        device_details = hosts.get_device_details(ids=result)

        # Store details in lists
        host_ids.append(result)
        lookup_ips.append(device_to_check)
        try:
            machine_domains.append(device_details["body"]["resources"][0]["machine_domain"])
        except KeyError:
            machine_domains.append("Not Available")
        try:
            internal_ips.append(device_details["body"]["resources"][0]["local_ip"])
        except (KeyError, TypeError):
            internal_ips.append("Not Available")
        try:
            last_seen.append(device_details["body"]["resources"][0]["last_seen"])
        except (KeyError, TypeError):
            last_seen.append("Not Available")
        try:
            first_seen.append(device_details["body"]["resources"][0]["first_seen"])
        except(KeyError, TypeError):
            first_seen.append("Not Available")
        try:
            external_ips.append(device_details["body"]["resources"][0]["external_ip"])
        except(KeyError, TypeError):
            external_ips.append("Not Available")
        try:
            last_login_time.append(device_details["body"]["resources"][0]["last_login_timestamp"])
        except(KeyError, TypeError):
            last_login_time.append("Not Available")
        try:
            ou.append(device_details["body"]["resources"][0]["ou"])
        except(KeyError, TypeError):
            ou.append("Not Available")
        try:
            tags.append(device_details["body"]["resources"][0]["tags"])
        except(KeyError, TypeError):
            tags.append("Not Available")
        try:
            connection_ip.append(device_details["body"]["resources"][0]["connection_ip"])
        except(KeyError, TypeError):
            connection_ip.append("Not Available")
        try:
            os_product.append(device_details["body"]["resources"][0]["os_product_name"])
        except(KeyError, TypeError):
            os_product.append("Not Available")
        try:
            site.append(device_details["body"]["resources"][0]["site_name"])
        except(KeyError, TypeError):
            site.append("Not Available")
        try:
            last_user.append(device_details["body"]["resources"][0]["last_login_user"])
        except(KeyError, TypeError):
            last_user.append("Not Available")
        try:
            hostname.append(device_details["body"]["resources"][0]["hostname"])
        except(KeyError, TypeError):
            hostname.append("Not Available")
        try:
            if device_details["body"]["resources"][0]["status"] == 'normal':
                containment_Status.append("No")
            else:
                containment_Status.append("Yes")
        except(KeyError, TypeError):
            containment_Status.append("Not Available")
        CS_status.append("In CrowdStrike")
        print("CS Status: Installed on",device_to_check)

    # Machine is not in CS
    if not ip_results:
        host_ids.append("Not Available")
        lookup_ips.append(device_to_check)
        machine_domains.append("Not Available")
        internal_ips.append("Not Available")
        last_seen.append("Not Available")
        first_seen.append("Not Available")
        external_ips.append("Not Available")
        last_login_time.append("Not Available")
        ou.append("Not Available")
        tags.append("Not Available")
        connection_ip.append("Not Available")
        os_product.append("Not Available")
        site.append("Not Available")
        last_user.append("Not Available")
        hostname.append("Not Available")
        CS_status.append("Not in CrowdStrike")
        containment_Status.append("Not in CrowdStrike")
        print("CS Status: NOT installed on", device_to_check)

#Ingest input from file
regex_query_local = re.compile(r"^127\.|^10\.|^172\.1[6-9]\.|^172\.2[0-9]\.|^172\.3[0-1]\.|^192\.168\.")
regex_query_external = re.compile(r"^([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))(?<!127)(?<!^10)(?<!^0)\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!192\.168)(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
with open(args.input_file, "r") as file:
    lines=file.readlines()
    for line in lines:
        line=line.strip()
        if re.search(regex_query_local, line):
            status_check_local(line)
        elif re.search(regex_query_external, line):
            status_check_external(line)
        else:
            status_check_hostname(line)

#Create dict from lists
output_ready_dict = {"Host ID": host_ids, "Lookup IP": lookup_ips, "Machine Domain": machine_domains, "Internal IP":
    internal_ips, "Last Seen": last_seen, "First Seen": first_seen, "External IP": external_ips, "Last Login Time":
                    last_login_time, "OU": ou, "Tags": tags, "Connection IP": connection_ip, "OS Product": os_product,
                    "Site": site, "Last Login User": last_user, "Hostname": hostname, "CrowdStrike Status": CS_status,"Contained in CrowdStrike?": containment_Status}
#Save dict to dataframe to convert to CSV
df = pd.DataFrame(output_ready_dict)
current_timestamp = datetime.datetime.now()
csv_path = args.output_dir+"\\CrowdStrike Status"+"_"+current_timestamp.strftime("%Y%m%d-%H%M%S")+".csv"
df.to_csv(csv_path, index=False)
