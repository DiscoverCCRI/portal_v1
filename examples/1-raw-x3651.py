"""An example of constructing a profile with one physical node running the default OS.

Instructions:
Log into your PC and poke around. You have root access via `sudo`. Any work you do on your PC will be lost when it terminates."""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Import the Emulab specific extensions.
import geni.rspec.emulab as emulab

# Create a portal object,
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Node node1
node1 = request.RawPC('node1')
node1.hardware_type = "x3651"

# Print the generated rspec
pc.printRequestRSpec(request)