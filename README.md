# Role Based Inventory

This is a POC of the idea: 

* each role should be more object like and know things about itself
* it can have inventory that's applicable to all deployments


##  Implementation

* a new class of inventory is created thats *per role*
* the role inventory can be a single file or directories but are named by inventory groups
* the inventory is loaded during startup so all the data is available when the play begins
* then at the role level, the inventory vars are combined to assemble the different sets of data
* combination happens using varnames

   *  Combining lists
   
    ```
        pl: "{{ [ q('vars', *(q('varnames', '^pl_') )) ] | sum(start=[]) | flatten | default({}) }}"
    ```

   * Combining a dictionaries

    ```
        pd:  "{{ q('vars', *(q('varnames', '^pd_') | sort)) | combine(recursive=True) | default({}) }}"
    ```

* this is designed to be OVERLOADED by regular ansible inventory, as thats loaded in directory structure order

## Use Cases

* preventing calling modules over and over with separate data, combine them and call once
* enabling single calls for data that must be consistent on first implementation


```
 % ap ./play.yml

PLAY [test] ****************************************************************************************************************

TASK [global/packages : install packages] **********************************************************************************
ok: [localhost] => {
    "_packages": [
        "oracle_all_package-1",
        "zsh_all_package",
        "inventory_package",
        "inventory_base-1",
        "inventory_base-2",
        "inventory_base-3"
    ]
}

TASK [global/firewall : configure firewall rules] **************************************************************************
ok: [localhost] => {
    "_firewall_rules": [
        {
            "name": "ssh access",
            "port": 22,
            "protocol": "tcp",
            "state": "present"
        },
        {
            "name": "icmp",
            "protocol": "icmp",
            "state": "present"
        }
    ]
}

PLAY [oracle test] *********************************************************************************************************

TASK [global/packages : install packages] **********************************************************************************
ok: [foohost] => {
    "_packages": [
        "oracle_all_package-1",
        "zsh_all_package",
        "inventory_package",
        "oracle_oracle_package-1",
        "oracle_oracle_package-2",
        "inventory_base-1",
        "inventory_base-2",
        "inventory_base-3"
    ]
}

TASK [global/firewall : configure firewall rules] **************************************************************************
ok: [foohost] => {
    "_firewall_rules": [
        {
            "name": "oracle access",
            "port": 1569,
            "protocol": "tcp",
            "state": "present"
        },
        {
            "name": "ssh access",
            "port": 22,
            "protocol": "tcp",
            "state": "present"
        },
        {
            "name": "icmp",
            "protocol": "icmp",
            "state": "present"
        }
    ]
}

```