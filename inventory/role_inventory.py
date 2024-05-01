#! /usr/bin/env python3
# coding: utf8
"""
read role inventory and export into global inventory
"""
import argparse
import os
import logging
import sys
import yaml
import json
import pprint

# use program name to store cache/data dirs
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stderr))
logging.basicConfig()
DEBUG = False
VERBOSE = False

# env vars
ANSIBLE_HOME = os.environ.get("ANSIBLE_HOME") or os.path.dirname(os.path.realpath(__file__)) + '/..'

def unique_list(seq):
    """return a unique list"""
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]


class AnsibleInventory:
    ANSIBLE_INVENTORY_STRUCT = {
        "_meta": {"hostvars": {}},
        "all": {"children": [], "hosts": [], "vars": {}},
    }

    def __init__(self):
        self.ansible_inventory = self.ANSIBLE_INVENTORY_STRUCT

    def dump_ansible_inventory(self):
        print(json.dumps(self.ansible_inventory))

    def add_group(self, groupname):
        """create a group in inventory"""
        if groupname not in self.ansible_inventory:
            logger.debug("adding group %s " % groupname)
            self.ansible_inventory[groupname] = {
                "hosts": [],
                "vars": {},
                "children": [],
            }

    def add_group_vars(self, groupname, vars):
        """append vars to groupvars"""
        for k, v in vars.items():
            self.ansible_inventory[groupname]["vars"][k] = v

   

class RoleInventory(AnsibleInventory):
    """
    read inventory from roles and extend
    """

    def __init__(self, ansible_home=ANSIBLE_HOME):

        super().__init__()
        self.ansible_home = ansible_home
        self.role_inventory = self.get_role_inventory()

    def get_role_inventory(self):
        roles_path = f"{self.ansible_home}/roles"
        for role_dir in os.listdir(roles_path):
            role_inventory_path = f"{roles_path}/{role_dir}/inventory"
            if os.path.exists(role_inventory_path) and os.path.isdir(role_inventory_path):
                self.get_role_vars(role_inventory_path)

    def get_role_vars(self, role_inventory_path):
        logger.debug(f"  reading inventory {role_inventory_path}")
        role_vars = {}
        for entry in os.listdir(role_inventory_path):
            logger.debug(f"   - inventory {role_inventory_path}/{entry}")
            if os.path.isdir(f"{role_inventory_path}/{entry}"):
                group = entry
                self.add_group(group)
                for f in os.listdir(f"{role_inventory_path}/{entry}"):
                    group_vars = self.get_vars(f"{role_inventory_path}/{entry}/{f}")
                    self.add_group_vars(group, group_vars)
            else:
                group = entry.split(".")[0]
                self.add_group(group)
                group_vars = self.get_vars(f"{role_inventory_path}/{entry}")
                self.add_group_vars(group, group_vars)

    def get_vars(self, path):
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error reading {path}: {e}")
            return {}


def setup_logging(args):
    """setup logging"""
    global debug, verbose
    llevel = logging.ERROR
    if args.debug:
        llevel = logging.DEBUG
        print("logging debug")
    elif args.verbose:
        llevel = logging.INFO

    if args.logfile:
        if not os.access(args.logfile, os.W_OK):
            print("ERROR: Unable to write to %s")
            sys.exit(1)
        logging.basicConfig(
            format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d:%H:%M:%S",
            filename=args.logfile,
            level=llevel,
        )
    else:
        logging.basicConfig(
            format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d:%H:%M:%S",
            level=llevel,
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Read pod Inventory and export to ansible inventory",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.set_defaults(verbose=False)
    parser.set_defaults(debug=False)
    parser.set_defaults(list=True)
    parser.set_defaults(flush_cache=False)
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Set verbose output."
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Set Debug output.")
    parser.add_argument("--list", action="store_true", help="Send Output to the Screen")
    parser.add_argument("--logfile", help="Send output to a file.")

    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging(args)
    role_inventory = RoleInventory()
    role_inventory.dump_ansible_inventory()


if __name__ == "__main__":
    main()

