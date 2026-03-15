#!/usr/bin/env python3

import re
import os
import sys

# regex
email_regex = re.compile(r'[a-zA-Z0-9._%+=-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
domain_regex = re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b')
ip_regex = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

emails = set()
domains = set()
ips = set()
true_sender = set()


def clean_brackets(value):
    """
    <> を削除
    """
    return value.strip().strip("<>").strip()


def parse_file(file_path):

    received_lines = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:

        for line in f:

            # email
            for e in email_regex.findall(line):
                e = clean_brackets(e)
                emails.add(e)

                # domain
                domain = e.split("@")[1]
                domains.add(domain)

            # domain
            for d in domain_regex.findall(line):
                domains.add(d)

            # ip
            for ip in ip_regex.findall(line):
                ips.add(ip)

            # return path
            if line.lower().startswith("return-path:"):
                rp = clean_brackets(line.split(":",1)[1])
                true_sender.add(rp)

            # received
            if line.lower().startswith("received:"):
                received_lines.append(line)

    # 一番下のReceived → 最初の送信元
    if received_lines:

        first = received_lines[-1]

        for ip in ip_regex.findall(first):
            true_sender.add(ip)


def scan(target):

    if os.path.isdir(target):

        for root, dirs, files in os.walk(target):

            for file in files:

                path = os.path.join(root, file)

                try:
                    parse_file(path)
                except:
                    pass

    else:
        parse_file(target)


def save_results():

    with open("emails.txt","w") as f:
        for e in sorted(emails):
            f.write(e+"\n")

    with open("domains.txt","w") as f:
        for d in sorted(domains):
            f.write(d+"\n")

    with open("ips.txt","w") as f:
        for i in sorted(ips):
            f.write(i+"\n")

    with open("true_sender.txt","w") as f:
        for t in sorted(true_sender):
            f.write(t+"\n")


def main():

    if len(sys.argv) < 2:

        print("Usage:")
        print("python mail_ir_tool.py <header_file_or_directory>")
        sys.exit()

    target = sys.argv[1]

    scan(target)

    save_results()

    print("Extraction completed.")
    print("emails.txt")
    print("domains.txt")
    print("ips.txt")
    print("true_sender.txt")


if __name__ == "__main__":
    main()
