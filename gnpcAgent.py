#!/usr/bin/python

# This piece of software can be optionally installed on to any
# system.  At the moment, this provides a service for sending a
# system inventory to some collection of management servers.

import gnpcInventory

my_inventory = gnpcInventory.InventoryOfSystem(unpickling=0)
