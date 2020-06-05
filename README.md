# AODV
This is a source code for AODV Ad-Hoc routing algorithm for a bttlefield
## Introduction
A wireless ad-hoc network (WANET) is a distributed type of wireless network. The
network is ad-hoc because it does not rely on preexisting network infrastructures,
such as routers in wired networks or access points in managed wireless networks.
Sometimes it is also referred to as Mobile Ad-hoc Network. This network is
continuously self-configuring and infrastructure-less. Devices may move from
their position, replace their neighborhoods, and consequently can change their
links with other devices in the network dynamically. Furthermore, An ad-hoc
network is a local area network (LAN) that is built spontaneously as devices
connect. Instead of relying on a base station to coordinate the flow of messages
to each node in the network, the individual network nodes forward ​packets​ to
and from each other. In the Windows operating system, ad-hoc is a
communication mode (setting) that allows nodes to directly communicate with
each other without a router.
## Implementation
Reactive or on-demand routing protocols in WANET create routes only when they
are needed. Reactive protocols use two different operations to find and maintain
routes: the route discovery process operation and the route maintenance
operation. When a node requires a route to the destination, it initiates a route
discovery process within the network. This process completed once a route
found, or all possible route permutations are examined. Route maintenance is
the process of responding to changes in the topology that happens after a route
has initially been created. When the link is broken, the nodes in the network try
to detect link breaks on the established routes. AODV (Ad-hoc On-demand
Distance Vector) is a reactive routing protocol that is a simple, efficient
on-demand MANET routing. This algorithm was motivated by the limited
bandwidth that is available in the media that are used for wireless
communications. Obtaining the routes purely on-demand makes AODV a very
useful and desired algorithm for WANETs. Each mobile node in the network acts
as a specialized router and routes are obtained as needed, thus making the
network self-starting
### Design
The battlefield is a rectangle with a given width and length. These specifications
will be part of the inputs to your simulation model. Note that nodes can always
move inside the battleground and no communication network is available for a
vehicle outside the field so the vehicles should not traverse the boundaries of the
rectangular field.
### Vehicles
You need to establish a vehicle model (both vehicle and node are used
interchangeably through this project) in order to design your simulation
environment properly. Each vehicle is an object with the following properties.
1. IP; Set to localhost for tests in your computer.
2. Port; Pick an available port for the vehicle.
3. UID; ID of each vehicle which should be a unique positive integer.
4. Location in the field; A pair of (x, y) which point to the current position of a
node within the field.
5. Module operational diameter; a constant integer same for all vehicles.
### Communication Server
Though in the real world you do not have the address of your neighbors, to
implement a practical model, you need to implement a server. All
communications are going through the server. The server must be capable of
transmitting messages considering the distance between the nodes. Each vehicle
knows about the address of the server and can only send and receive messages
via its link with the server. Note that the server is only a simulator for real word
situation so there is no need for it in a real scenario.
### Scenario
Scenarios are input commands which are used to instruct the server how to
behave. For example, if you want a node to start sending a message after 2
seconds, you have to write it down in the scenario section like the following
example.
