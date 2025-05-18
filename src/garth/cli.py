import argparse
import getpass

import garth


def main():
    parser = argparse.ArgumentParser(prog="garth")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "login", help="Authenticate with Garmin Connect and print token"
    )

    args = parser.parse_args()

    match args.command:
        case "login":
            email = input("Email: ")
            password = getpass.getpass("Password: ")
            garth.login(email, password)
            token = garth.client.dumps()
            print(token)
        case _:
            parser.print_help()
