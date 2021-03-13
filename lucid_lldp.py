import csv
import requests
from getpass import getpass
import json
import urllib3
import yaml
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


####################Global Variables####################
# Get Username and Password
username = input("Please enter your username: ")
password = getpass("Please enter your password: ")

with open('device_list.yml') as device_file:
    device_list = yaml.safe_load(device_file.read())

write_data = [{'Id': '1', 'type': 'page', 'Name': 'Page', 'Shape Library': '',
 'Page ID': '', 'Contained By': '', 'Group': '', 'Line Source': '',
  'Line Destination': '', 'Source Arrow': '', 'Destination Arrow': '',
  'Text Area 1': 'lldp_map'}]

csv_columns = ['Id', 'Name', 'Shape Library', 'Page ID', 'Contained By', 'Group', 'Line Source', 'Line Destination', 'Source Arrow', 'Destination Arrow', 'Text Area 1']
csv_file = "lldp_lucid.csv"
#########################################

def send_arista_commands_api(username,password,device):

    url = 'https://{0}:{1}@{2}/command-api'.format(username,password,device)

    commands = ['enable', 'show hostname', 'show lldp neighbors']

    '''Declare api request variables'''
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache"
    }

    # Define payload with commands
    payload = '''{
      "jsonrpc": "2.0",
      "method": "runCmds",
      "params": {
        "format": "json",
        "timestamps": false,
        "autoComplete": false,
        "expandAliases": false,
        "cmds": ''' + json.dumps(commands) + ''',
        "version": 1
      },
      "id": "EapiExplorer-1"
    }'''
    
    try:
        response = requests.request("POST", url, data=payload, headers=headers, verify=False)        
        return (json.loads((response.content))['result'][1], json.loads((response.content))['result'][2]['lldpNeighbors'])
    except:
        print('Error Connecting to {0}. Please ensure device is reachable and eAPI is enabled.'.format(device))


def main():

    print('Gathering Device Data...')
    device_count = 2
    for device in device_list:

        prep_device = {'Id': str(device_count),'type': 'device', 'Name': 'Text', 'Shape Library': 'Standard',
        'Page ID': '1', 'Contained By': '', 'Group': '', 'Line Source': '',
        'Line Destination': '', 'Source Arrow': '', 'Destination Arrow': '',
        'Text Area 1': ''}

        hostname, lldp_neighbors = send_arista_commands_api(username,password,device)

        prep_device['Text Area 1'] = hostname['fqdn']
        prep_device['lldp_neighbors'] = []
        for neighbor in lldp_neighbors:
            prep_device['lldp_neighbors'].append({'port': hostname['fqdn'] + '_' + neighbor['port'], 'neighbor_device': neighbor['neighborDevice']})
        write_data.append(prep_device)
        device_count += 1

    line_pairs = []
    for line_item in write_data:
        if line_item['type'] == 'device':
            for neighbor in line_item['lldp_neighbors']:
                for search_line_item in write_data:
                    if search_line_item['type'] == 'device':
                        if neighbor['neighbor_device'] == search_line_item['Text Area 1']:
                            prep_line = {'Id': str(device_count), 'type': 'line', 'Name': 'Line', 'Shape Library': '',
                            'Page ID': '1', 'Contained By': '', 'Group': '', 'Line Source': '',
                            'Line Destination': '', 'Source Arrow': 'None', 'Destination Arrow': 'None',
                            'Text Area 1': ''}
                            if [search_line_item['Id'],line_item['Id']] not in line_pairs:
                                line_pairs.append([line_item['Id'],search_line_item['Id']])
                                prep_line['Line Source'] = line_item['Id']
                                prep_line['Line Destination'] = search_line_item['Id']
                                write_data.append(prep_line)
                                device_count += 1

    for item in write_data:
        item.pop('type')
        if 'lldp_neighbors' in item:
            item.pop('lldp_neighbors')

    print('Writing to CSV...')
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in write_data:
            writer.writerow(data) 

if __name__ == '__main__':
    main()