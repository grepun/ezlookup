import subprocess
import ipaddress
import argparse

def nslookup(ip):
    try:
        result = subprocess.run(['nslookup', ip], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return str(e)

def parse_hostname(nslookup_output):
    lines = nslookup_output.splitlines()
    for line in lines:
        if 'name = ' in line:
            return line.split('name = ')[1].strip()
    return 'N/A'

def nslookup_list(ips):
    results = {}
    for ip in ips:
        nslookup_output = nslookup(ip)
        hostname = parse_hostname(nslookup_output)
        results[ip] = hostname
    return results

def nslookup_cidr(cidr):
    network = ipaddress.ip_network(cidr, strict=False)
    results = {}
    for ip in network.hosts():
        nslookup_output = nslookup(str(ip))
        hostname = parse_hostname(nslookup_output)
        results[str(ip)] = hostname
    return results

def read_inputs_from_file(file_path):
    with open(file_path, 'r') as file:
        inputs = [line.strip() for line in file if line.strip()]
    return inputs

def write_results_to_file(results, output_file):
    with open(output_file, 'w') as file:
        for ip, hostname in results.items():
            file.write(f"{ip} : ({hostname})\n")

def main():
    parser = argparse.ArgumentParser(description='Perform nslookup on a list of IPs or CIDR ranges.')
    parser.add_argument('input_file', help='Path to the file containing a list of IPs or CIDR ranges')
    parser.add_argument('output_file', nargs='?', help='Path to the file to write the output')
    args = parser.parse_args()

    inputs = read_inputs_from_file(args.input_file)
    all_results = {}

    for input_value in inputs:
        try:
            if '/' in input_value:
                print(f"NSLOOKUP FOR CIDR RANGE: {input_value}")
                cidr_results = nslookup_cidr(input_value)
                all_results.update(cidr_results)
                for ip, hostname in cidr_results.items():
                    print(f"{ip} : ({hostname})")
            else:
                print(f"NSLOOKUP FOR IP: {input_value}")
                ip_result = nslookup_list([input_value])
                all_results.update(ip_result)
                for ip, hostname in ip_result.items():
                    print(f"{ip} : ({hostname})")
        except ValueError as e:
            print(f"Invalid input '{input_value}': {e}")

    if args.output_file:
        write_results_to_file(all_results, args.output_file)

if __name__ == '__main__':
    main()
