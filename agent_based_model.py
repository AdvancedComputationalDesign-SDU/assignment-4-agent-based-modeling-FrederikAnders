"""
Assignment 4: Agent-Based Model for Structural Tessellation Generation

Author: Frederik Andersen

Description:
This script implements an agent-based model using Object-Oriented Programming (OOP) principles.
It simulates the behavior of agents to generate structural patterns, exploring how changes in
rules and parameters affect the resulting form.

Note: This script is intended to be used within Grasshopper's Python scripting component or as a standalone Python script.
"""

# AGENT BUILDER:

# Import necessary libraries
import random
import math
import Rhino
import Rhino.Geometry as rg

# Define the Agent class
class Agent:

    # Initialize agent object with speciffic attributes. Parameters: self, srf, position, and velocity
    def __init__ (self, srf, position, velocity=[0,0,0]):
        self.position = position
        self.velocity = velocity
        self.srf = srf
        self.local_curvature = 1.

    # Calculate the distance between agent and another agent, taking into account local surface curvature at the other agents location
    def dist(self, agent): 
        curvature_factor = np.interp(agent.local_curvature, [-0.015, 0.015], [1, 5])
        return rs.Distance(self.position, agent.position)

    # Create a list of other agents sorted by their adjusted distance (from dist)
    def sorted_neighbors(self, agents):        #loops through entire list of agents and picks them one-by-one
        return sorted(agents, key=self.dist)   #the sorted list gets returned
    
    # Apply "seperation force" to agents to avoid overlapping with neighbours. 
    def seperation(self, agents, force_intensity, n):
        self.velocity = [0,0,0]                                            # reset agents velocity so that only the updated velocity gets applied
        sorted_neighbors = self.sorted_neighbors(agents)                   # call the sorted neighbours list
        for i in range(n):                                                 # pick how many agents you want to influence the the current agents behaviour
            agent = sorted_neighbors[i]                                    # skip current agent
            if (agent == self):
                continue
            distance_vec = rs.VectorCreate(self.position, agent.position)  # calculate vector from current agent's to neighboring agent's position
            if rs.VectorLength(distance_vec) == 0:                         # if vector = 0, randomize seperation direction to insure seperation
                distance_vec = [random.uniform(-1,1), random.uniform(-1,1), 0]
            inverse_dist = np.interp(rs.VectorLength(distance_vec), [0,1], [force_intensity, 0])  # linearly interpolate the seperation force based on distance. The closer the agents, the higher the seperation force
            inverse_distance_vec = rs.VectorUnitize(distance_vec) * inverse_dist                  # normalize the distance_vec and scale it proportinally to the distance
            self.velocity = rs.VectorAdd(self.velocity, inverse_distance_vec)                     # add the vector to the agent's velocity

    # move agent by updating its position based on its velocity and recalculating its local curvature on the surface 
    def update(self): 
        self.position = rs.VectorAdd(self.position, self.velocity)         # vectoradd is a bit like move
        self.position = np.clip(list(self.position), 0, 1).tolist()        # First update agents position by adding current velocity. Afterwards, the vector is clipped to avoid going out of bounds
        scaled_u = rs.SurfaceDomain(self.srf, 0)[0] + self.position[0] * rs.SurfaceDomain(self.srf, 0)[1]   # tranforms the normalized position (self.position) into the surface's actual domain
        scaled_v = rs.SurfaceDomain(self.srf, 1)[0] + self.position[1] * rs.SurfaceDomain(self.srf, 1)[1]
        self.local_curvature = rs.SurfaceCurvature(self.srf, (scaled_u, scaled_v))                          # scaled_u and scaled_v represent the actual parameter-space coordinates of the agents on the surface

# create and initialize a collection og agent objects randomly distributed over a surface
def build_agents(srf, n_agents):           # parameters (the surface and the number of agents)
    agents = []                            # list to store the agent objects
    for _ in range(n_agents):              # generate random positions for the agents. The loob runs n_agents times
        u = random.uniform(0, 1)           # generate random float between 0 and 1 representing normalized uv positions on the srf
        v = random.uniform(0, 1)
        point = [u, v, 0]                  # create a 3D point
        agents.append(Agent(srf, point))   # create and append agent based on surface and position, and add it to the agents list
    return agents

# define a custom GH component (MyComponent) which manages the initialization of agents and provides them to the rest of the simulation
class MyComponent(Grasshopper.Kernel.GH_ScriptInstance):  # make it a GH script component
    import Rhino
    def RunScript(self, srf: Rhino.Geometry.Surface, N: int):
        self.agents = build_agents(srf, N) # store agents as an attribute of MyComponent
        return self.agents                 # return the list of agents



# AGENT SIMULATOR:

import rhinoscriptsyntax as rs
import numpy as np

# integrates numpy and rhino to dynamically update the positions, velocities and curvatures of the agents
for agent in x:
    print(agent.position, agent.velocity, agent.local_curvature)

# Access the agents list directly
agents = x

# Update each agent's behavior
for agent in agents:
    agent.seperation(agents, force, N)                           
    agent.update()

# Collect UV coordinates, velocities, and curvatures
uv_coords = [rs.AddPoint(agent.position) for agent in agents]    # Fixed position
velocity = [rs.AddPoint(agent.velocity) for agent in agents]     # Fixed velocity
curvature = [agent.local_curvature for agent in agents]          # Fixed attribute access

# Clip curvature values and convert to a list
curvature = np.clip(curvature, -0.5, 0.5).tolist()








# After simulation, process results
# TODO: Generate geometry or visualization based on agent data

# Visualization code (if using Rhino/Grasshopper)
# For example, create points or lines based on agent positions

# Output variables (connect to Grasshopper outputs if applicable)
# agent_positions = [agent.position for agent in agents]
