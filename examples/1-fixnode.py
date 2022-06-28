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
node1 = request.RawPC('node1')
node1.hardware_type = "FixedNode"
node1.component_id= "CC1"
node1.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD"

# Print the generated rspec
pc.printRequestRSpec(request)

