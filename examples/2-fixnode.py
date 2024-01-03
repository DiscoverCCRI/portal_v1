"""An example of constructing a profile with one physical node running the default OS.

Instructions:
Log into your PC and poke around. You have root access via `sudo`. Any work you do on your PC will be lost when it terminates."""

# Import the Portal object.
import geni.portal as portal

# Create a portal object,
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Node node1
node1 = request.RawPC("node1")
node1.hardware_type = "FixedNode"
node1.component_id = "CC1"
node1.disk_image = "UBUNTU20-64-STD"


node2 = request.RawPC("node2")
node2.hardware_type = "FixedNode"
node2.component_id = "CC2"
node2.disk_image = "UBUNTU20-64-STD"


# Create a link between them
link1 = request.Link(members=[node1, node2])

# Print the generated rspec
pc.printRequestRSpec(request)
