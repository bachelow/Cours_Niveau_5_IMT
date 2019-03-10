###########################################
######                               ######
######    Algorithme génétique de:   ###### 
######       Matthieu BACHELOT       ###### 
######          Lucas MONTI          ######
######         Alexis MICHEL         ######
######       Florian TREGUILLY       ######  
######                               ######    
###########################################

import pandas as pd
import numpy as np 
import prufer, random
import networkx as nx
from operator import itemgetter
import matplotlib.pyplot as plt

###### Lire les données excel ###########################################################

def read_excel_data(filename, sheet_name):
    
	data = pd.read_excel(filename, sheet_name=sheet_name, header=None)  
	values = data.values
	    
	return values

###### Variables globales ###############################################################

total_node_number = 30
path_to_data = 'InputDataHubLargeInstance.xlsx'
fixCost = read_excel_data(path_to_data,'fixCost')
varCost = read_excel_data(path_to_data,"varCost")
flow = read_excel_data(path_to_data,"flow")
capacity = read_excel_data(path_to_data,"Cap")
alpha = 0.65

###### Passer d'une séquence de Prufer à une liste ######################################

def prufer_to_list(sequence): 

	tree = prufer.build_tree(sequence)

	# On créer une matrice binaire qui indique si le node i est lié au node j (alors Mij=1, sinon 0)
	# C'est la matrice regroupant les Zij ainsi que les Yij du papier scientifique 
	shape = (total_node_number,total_node_number)
	z_matrix = np.zeros(shape)

	# On créer d'abord les Zij
	for node in tree:
		node_i,node_j = node[0],node[1]
		z_matrix[node_i][node_j] = 1
		z_matrix[node_j][node_i] = 1

	# Maintenant les Yij
	for i in range(total_node_number):
		connection_list = z_matrix[i]
		if np.sum(connection_list) > 1: 
			z_matrix[i][i] = 1
		else:
			pass

	return tree, z_matrix

###### Calcul de la fitness + prise en compte de la contrainte de la capacité ###########

def individualFitness(hub_config):    
    
    Tree_Edges,z_matrix = prufer_to_list(hub_config)
    Graph = nx.Graph(Tree_Edges)
    All_Pairs_Path = dict(nx.all_pairs_shortest_path(Graph))
    
    Hubs = np.unique(hub_config)
    FixedCost = fixCost[Hubs].sum()
    
    VarCost = 0
    FlowToHub = np.zeros(total_node_number)
    for i in range(total_node_number):
        for j in range(total_node_number):
            if j > i:
                for x in range(len(All_Pairs_Path[i][j])-1):
                    Route = All_Pairs_Path[i][j]
                    if Route[x] in Hubs and Route[x+1] in Hubs:
                        VarCost = VarCost + alpha * varCost[Route[x],Route[x+1]]*(flow[i,j]+flow[j,i])
                    else:
                        VarCost = VarCost + varCost[Route[x],Route[x+1]] * (flow[i,j]+flow[j,i])
        Fitness = FixedCost + VarCost

    # On calcule les flow entrants et sortants
    Origin,Destination =  {},{}
    for i in range(len(Tree_Edges)+1):

    	Origin[i],Destination[i] = 0,0 
    	for j in range(len(Tree_Edges)):
    		Origin[i] += flow[i,j]*z_matrix[i][j]
    		Destination[i] += flow[j,i]*z_matrix[i][j]

    # Calculating the Entering flow to Each Hub #
    for i in range(len(Tree_Edges)):
        if Tree_Edges[i][0] not in Hubs:
            FlowToHub[Tree_Edges[i][1]] = FlowToHub[Tree_Edges[i][1]] + (Origin[Tree_Edges[i][0]]+Destination[Tree_Edges[i][0]])
        elif Tree_Edges[i][1] not in Hubs:
            FlowToHub[Tree_Edges[i][0]] = FlowToHub[Tree_Edges[i][0]] + (Origin[Tree_Edges[i][1]]+Destination[Tree_Edges[i][1]])
    for i in range(len(Hubs)):
        FlowToHub[Hubs[i]] = FlowToHub[Hubs[i]] + (Origin[Hubs[i]]+Destination[Hubs[i]])

    # On modélise la contrainte de capacité par une augmentation importante de la fitness 
    exceed = np.subtract(capacity,FlowToHub)
    exceed_capacity = exceed[Hubs,Hubs]
    if min(exceed_capacity) < 0:
    	Fitness += 1000000000000

    return Fitness



if __name__ == '__main__':

	
	config_pop = []

	for j in range(5):
		
		hub_config = []
		for i in range(total_node_number-2):
			hub_config.append(random.randint(1,total_node_number-2))
		
		fitness = individualFitness(hub_config)
		config_pop.append([fitness,hub_config])

	sorted_fitness_dict = sorted(config_pop, key=lambda t: t[0])
	
	print('\nfinal list\n',sorted_fitness_dict)


