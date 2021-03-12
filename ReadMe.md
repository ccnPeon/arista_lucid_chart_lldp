# Arista LLDP Lucid Chart CSV Builder

## Prerequisites
1) It is advised to turn off LLDP Transmit/Receive on the MA1 Interface to prevent bloat
2) Install required Python packages: PyYAML
3) Ensure that eAPI is enabled on all of the switches and they have a common username and password

## Instructions

1) Insert list of all of the IP addresses in YAML format in 'device_list.yml'
2) Run the script
3) Enter Username
4) Enter Password
5) After file is generated ('lldp_lucid.csv'), create a new document in Lucid Chart
6) In Lucid Chart: Go to File > Import Data > Process Diagram
7) Select the .csv file that was generated and you should see a generic diagram created with your topology.
