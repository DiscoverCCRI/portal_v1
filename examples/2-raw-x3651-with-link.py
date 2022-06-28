"""An example of constructing a profile with two physical nodes connected by a Link.

Instructions:
Wait for the profile instance to start, and then log in to either host.
"""

import geni.portal as portal
import geni.rspec.pg as rspec

request = portal.context.makeRequestRSpec()

# Create two raw "PC" nodes
node1 = request.RawPC("node1")
node2 = request.RawPC("node2")
node1.hardware_type = "x3651"
node2.hardware_type = "x3651"

# Create a link between them
link1 = request.Link(members = [node1, node2])

portal.context.printRequestRSpec()