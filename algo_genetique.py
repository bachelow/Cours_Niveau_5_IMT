###########################################
######                               ######
######    Algorithme génétique de:   ###### 
######       Matthieu BACHELOT       ###### 
######          Lucas MONTI          ######
######         Alexis MICHEL         ######
######       Florian TREGUILLY       ######  
######                               ######    
###########################################

import prufer,random, os, time, math, csv, copy
import pandas as pd 
import numpy as np 
import networkx as nx
import matplotlib.pyplot as plt
from utils import * 

###### Paramètres ###############################

mutation_rate = 0.2 
generation_number = 10
population_size = 100
tournament_size = 8
path_to_data = 'InputDataHubLargeInstance.xlsx'

###### Variables gobales ########################

total_node_number = 30 
alpha = 0.65
node_list = [i for i in range(1,total_node_number+1)]
capacity = read_excel_data(path_to_data,"Cap")
fixCost = read_excel_data(path_to_data,"fixCost")
varCost = read_excel_data(path_to_data,"varCost")
flow = read_excel_data(path_to_data,"flow")

###### Classes ##################################

class Configuration(object):
	"""Classe définissant les configurations de Hub (ie individus) sous la forme de séquence de prufer"""
	
	def __init__(self):
		
		# On génère une séquence de Prufer via une liste d'entiers naturels aléatoires de taille total_node_number-2 
		self.hub_config = []
		for i in range(total_node_number-2):
			self.hub_config.append(random.randint(1,total_node_number-2))
		self.calculate_cost()

	def calculate_cost(self):

		self.total_cost = individualFitness(self.hub_config)

	def print_hub_config(self):
		
		print(self.hub_config, 'with a fitness of ', self.total_cost)

		

class Population(object):
	"""Classe définissant la Population pour une génération i"""
	
	def __init__(self, size, initialise):
		self.config_pop = []
		self.size = size

		# si nous voulons initialiser nous même la population 
		if initialise:
			for i in range(size):
				new_config = Configuration()
				fitness = new_config.total_cost
				self.config_pop.append([fitness,new_config]) 
      
	def get_fittest(self):

		# On trie la liste pour avoir le meilleur élément (coût minimal) en premier
		sorted_fitness_list = sorted(self.config_pop, key=lambda t: t[0])
		self.fittest = sorted_fitness_list[0]
		return self.fittest


class Algo_genetique(object):
	"""Classe définissant l'algorithme génétique, contient uniquement les méthodes de selection / XO / mutations / nouvelles génération """
	
	def crossover(self, configA, configB):

		# Child config 
		new_config = Configuration()
		crossover_cut = len(configA.hub_config)//2 

		for i in range(crossover_cut):

			# La première moitié de new_config sera égale à celle de configA
			new_config.hub_config[i] = configA.hub_config[i]

		for i in range(crossover_cut):

			# La deuxième sera égale à configB
			new_config.hub_config[i+crossover_cut] = configB.hub_config[i+crossover_cut]

		return new_config


	def mutation(self, config):

		if random.random() < mutation_rate:

			# On prend un indice et un numéro de node aléatoire
			index_mut = random.randint(0,len(config.hub_config)-1)
			node_mut = random.randint(1,total_node_number-2)

			# On s'assure que config[index_mut] != de node_mut
			if config.hub_config[index_mut] == node_mut:
				while config.hub_config[index_mut] == node_mut:
					node_mut = random.randint(1,total_node_number-2)

			# Maintenant on change la valeure de config[index_mut] par node_mut
			config.hub_config[index_mut] = node_mut

		return config


	def tournament_selection(self, population):

		# On génère une nouvelle population vide 
		# On ne l'initialise pas, parce qu'elle va être remplis par des individus de la génération actuelle
		tournament_pop = Population(size=tournament_size,initialise=False)

		# On l'a remplis d'individus aléatoires venant de population
		for i in range(tournament_size-1):

			chosen_config = random.choice(population.config_pop)
			# fitness = chosen_config.total_cost
			tournament_pop.config_pop.append(chosen_config) 

		# On renvoie la configuration avec la meilleure fitness 
		winner = tournament_pop.get_fittest()
		
		return winner[1]


	def population_evolution(self, current_gen):

		# On commence avec une population vide
		next_gen = Population(size=current_gen.size,initialise=True)

		# for i in range(len(current_gen.config_pop)):
		# 	print(current_gen.config_pop[i])

		# On selectionne la meilleure config de la current_gen
		next_gen.config_pop[0] = current_gen.fittest
		elitism_offset = 1

		# On remplit le reste de la génération par des crossovers de deux gagnants de deux tournois 
		for i in range(elitism_offset,next_gen.size):

			tournament_parent_1 = self.tournament_selection(current_gen)
			tournament_parent_2 = self.tournament_selection(current_gen)
			
			# On créer un enfant par cross over
			tournament_child = self.crossover(tournament_parent_1,tournament_parent_2)
			fitness = tournament_child.total_cost

			next_gen.config_pop[i] = [fitness,tournament_child]

		# Maintenant on fait muter de manière aléatoire les individus (on fait gaffe à ne selectionner que config[1])
		# Parce que config = [fitness,configuration]
		for config in next_gen.config_pop:
			self.mutation(config[1])

		# On met à jour la meilleure configuration 
		next_gen.get_fittest()

		return next_gen


class Main(object):
	"""Fait tourner l'algorithme et résout le problème"""
	
	def __init__(self,generation_number,population_size):

		self.generation_number = generation_number
		self.population_size = population_size

		print("Calculating GA loop")
		self.GA_loop(generation_number,population_size)


	# def update_canvas(self,current_canvas,current_config,color):


	def GA_loop(self,generation_number,population_size):

		# On note le temps de début de l'expérience
		start_time = time.time()

		# On créer une population 
		print("Creating population...")
		current_population = Population(population_size, True)
		print ("Done")

		# Pour voir comment le coût évolue, on stocke le coût du meilleur élément
		fittest_config = current_population.get_fittest()
		initial_cost = fittest_config[0]

		# On stocke la meilleure configuration dans une variable 
		best_config = Configuration()
		best_gen = 1

		# Boucle principale 
		for i in range(generation_number):

			# On évolue la population
			current_population = Algo_genetique().population_evolution(current_population)

			# Si l'on a trouvé une meilleure configuration on la sauvegarde dans la variable best_config
			if current_population.fittest[0] < best_config.total_cost:
				best_config = copy.deepcopy(current_population.fittest[1])

				# On imprime dans le terminal cette meilleure configuration 
				print('Generation number: ',i+1)
				best_config.print_hub_config()
				best_gen = i+1

		# On note le temps écoulé 
		end_time = time.time()

		# On sauvegarde la meilleure fitness dans un dictionnaire
		data_path = 'fitness_for_'+str(population_size)+'pop'
		data_path = os.path.join('data_pop',data_path)
		time_elapsed = end_time - start_time
		data = [initial_cost,best_config.total_cost,time_elapsed,best_gen]
		np.savez_compressed(data_path,a=data)

		# On imprime les informations dans le terminal 
		self.clear_term()
		print('Finished evolving {0} generations.'.format(generation_number))
		print("Elapsed time was {0:.1f} seconds.".format(end_time - start_time))
		print('Best generation: ',best_gen)
		print('Initial best config: {0:.2f}'.format(initial_cost))
		print('Final best config:   {0:.2f}'.format(best_config.total_cost))
		print('The best config is:')
		best_config.print_hub_config()


	def clear_term(self):
		os.system('cls' if os.name=='nt' else 'clear')


if __name__ == '__main__':
	Main(generation_number=generation_number,population_size=population_size)