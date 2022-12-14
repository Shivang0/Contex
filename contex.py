import sys
import requests
from pathlib import Path
import json
import argparse
from colorama import init
from termcolor import colored

def print_usage():
    print(f''' Usage: 
* python3 {sys.argv[0]} -e [etherscan|bnbscan|snowtrace|fantom|polygonscan] <contract_address>
* python3 {sys.argv[0]} -e [etherscan|bnbscan|snowtrace|fantom|polygonscan] -f <filename.txt>

filename.txt must contain contract addresses, one on each line.
''')
print(colored("""\n
    CONTRACT EXTRACTOR v1.0\n""", 'green'))

print(colored("""Kindly set API_KEY in .env file.
    """, 'red'))


# Read the ETHERSCAN_API_KEY from .env
def get_api_key(endpoint):
    # Get the API key name
    if endpoint == ETHERSCAN_ENDPOINT:
        api_key_name = 'ETHERSCAN_API_KEY'
    elif endpoint == BNBSCAN_ENDPONT:
        api_key_name == 'BNBSCAN_API_KEY'
    elif endpoint == FANTOM_ENDPONT:
        api_key_name == 'FANTOM_API_KEY'
    elif endpoint == AVALANCHE_ENDPOINT:
        api_key_name = 'AVALANCHE_API_KEY'
    elif endpoint == POLYGON_ENDPOINT:
        api_key_name = 'POLYGONSCAN_API_KEY'
    
    with open('.env', 'r') as f:
        env_contents = f.read()
    
    variables = env_contents.split('\n')
    
    for v in variables:
        [name, value] = v.split('=')
        if name == api_key_name:
            return value

ETHERSCAN_ENDPOINT = "https://api.etherscan.io/api?module=contract&action=getsourcecode&address={}&apikey={}"
BNBSCAN_ENDPONT = "https://api.bscscan.com/api?module=contract&action=getsourcecode&address={}&apikey={}"
FANTOM_ENDPONT = "https://api.ftmscan.com/api?module=contract&action=getsourcecode&address={}&apikey={}"
AVALANCHE_ENDPOINT = "https://api.snowtrace.io/api?module=contract&action=getsourcecode&address={}&apikey={}"
POLYGON_ENDPOINT = "https://api.polygonscan.com/api?module=contract&action=getsourcecode&address={}&apikey={}"

def download_contract(endpoint, api_key, address):
    Path("extracted_contracts").mkdir(parents=True, exist_ok=True)
    data = requests.get(endpoint.format(address, api_key)).json()
    if data["status"] != '1':
        print(f"[ERROR] Failed to fetch contract for address {address}")
    else:
        # There might be one source file, or multiple. In the case of one file,
        # this json.loads() will fail
        try:
            sources = json.loads(data["result"][0]['SourceCode'][1:-1])['sources']

            # First, make a directory for this contract by using the first filename
            # we encounter, skipping the .sol extension
            # TODO: Handle directory name collisions here
            directory_name = list(sources.keys())[0].split('/')[-1][:-4]
            Path(f'extracted_contracts/{directory_name}').mkdir(parents=True, exist_ok=True)

            for key in sources.keys():
                filename = key.split('/')[-1]
                content = sources[key]['content']

                with open(f"extracted_contracts/{directory_name}/{filename}", 'w') as f:
                    f.write(content)
        except:
            source = data["result"][0]['SourceCode']
            
            # Ask the user what filename they want I guess
            filename = input("What do you want to name this contract? (add .sol extension): ")
            
            directory_name = filename[:-4]
            Path(f'extracted_contracts/{directory_name}').mkdir(parents=True, exist_ok=True)

            with open(f"extracted_contracts/{directory_name}/{filename}", 'w') as f:
                f.write(source)

        #source = source.replace('\\\\n', '\\n')
        #print(sources)
        print(colored(f"[SUCCESS] Fetched contract from address {address}",'green'))

def main():
    api_key = None
    addresses = None
    
    # Setup argument parser
    parser = argparse.ArgumentParser(description=' Download Verified Contracts from EVM Chains')
    parser.add_argument('-a', '--address', type=str, help='Address of verified contract')
    parser.add_argument('-e', '--endpoint', type=str, choices=['etherscan', 'bnbscan','fantom','snowtrace','polygonscan'], help='\'etherscan\' or \'bnbscan\' or \'fantom\' or \'snowtrace\' or \'polygonscan\'')
    parser.add_argument('-f', '--filename', type=str, help='file with list of contract addresses')

    args = parser.parse_args()

    # Endpoint is required
    if args.endpoint is None:
        print(colored(f"[ERROR] An endpoint is required",'red'))
        parser.print_help()
        exit(1)

    # Either an address or a file with addresses is required
    if args.address is None and args.filename is None:
        print(colored(f"[ERROR] Need a filename with addresses, or an address by itself",'red'))
        parser.print_help()
        exit(1)

    # If a file and an address are both provided, use file
    if args.filename is not None:
        with open(args[2], 'r') as f:
            addresses = f.read().split('\n') 
    else:
        addresses = [args.address]
    
    # The addresses array might have an empty string at the end
    if addresses[-1] == '':
        addresses = addresses[:-1]
    
    # Get the correct endpoint
    if args.endpoint == 'etherscan':
        endpoint = ETHERSCAN_ENDPOINT
    elif args.endpoint == 'bnbscan':
        endpoint = BNBSCAN_ENDPONT
    elif args.endpoint == 'fantom':
        endpoint = FANTOM_ENDPONT
    elif args.endpoint == 'snowtrace':
        endpoint = AVALANCHE_ENDPOINT
    elif args.endpoint == 'polygonscan':
        endpoint = POLYGON_ENDPOINT
    
    api_key = get_api_key(endpoint)

    for address in addresses:
        download_contract(endpoint, api_key, address)

if __name__ == '__main__':
    main()
