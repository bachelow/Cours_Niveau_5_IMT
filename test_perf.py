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
import seaborn as sns
import networkx as nx
from tqdm import tqdm 
import matplotlib.pyplot as plt
from utils import * 
from algo_genetique_final import * 

###### Variables gobales ########################

# Les différents paramètres à faire varier
liste_pop_a_tester = [str(10*i) for i in range(3,11)]
liste_gen_a_tester = [str(10*i) for i in range(1,11)]
liste_mut_a_tester_2 = ['0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9']
liste_mut_a_tester = [str(0.1*i) for i in range(1,10)]
liste_tournois_a_tester = [str(2*i) for i in range(1,11)]
liste_a_tester = [liste_pop_a_tester,liste_gen_a_tester,liste_mut_a_tester,liste_tournois_a_tester]
data_to_store = ''

# Les listes de noms pour sauvegarder / charger les données 
data_folder_list = ['data_pop','data_gen','data_mut','data_tournois']
liste_parametre = ['Taille de la population','Nombre de générations','Mutation rate','Taille des tournois']
liste_label = ['Fitness minimale','Gain de fitness total','Rapport générations sur générations utiles']
plot_results_sub_folders = ['Etude pop','Etude gen','Etude mut','Etude tournois']
plot_result_folder = 'C:/Users/mbach/Desktop/TELECOM Bretagne/Cours/ISA/Niveau 5/CaseStudy/GA/plot_results'
tests_result_folder = 'C:/Users/mbach/Desktop/TELECOM Bretagne/Cours/ISA/Niveau 5/CaseStudy/GA/Tests'
test_serial_list = ['Serie_1','Serie_2','Serie_3','Serie_4','Serie_5','Serie_6','Serie_7','Serie_8','Serie_9','Serie_10']

# Les paramètres de références 
mutation_rate = 0.2
generation_number = 50
population_size = 50
tournament_size = 8

###### Fonctions de tests #######################

def test_impact_population_number(serial_number): 

	for i in range(len(liste_pop_a_tester)):
		print('Test for a population of size ',liste_pop_a_tester[i])
		Main(generation_number=generation_number, population_size=liste_pop_a_tester[i], mutation_rate=mutation_rate, 
			tournament_size=tournament_size, data_to_store=data_folder_list[0], serial_number=serial_number)

def test_impact_generation_number(serial_number): 

	for i in range(len(liste_gen_a_tester)):
		print('Test for a number of generation of ',liste_gen_a_tester[i])
		Main(generation_number=liste_gen_a_tester[i], population_size=population_size, mutation_rate=mutation_rate, 
			tournament_size=tournament_size, data_to_store=data_folder_list[1], serial_number=serial_number)

def test_impact_mutation_rate(serial_number): 

	for i in range(len(liste_mut_a_tester)):
		print('Test for a mutation rate of ',liste_mut_a_tester[i])
		Main(generation_number=generation_number, population_size=population_size, mutation_rate=liste_mut_a_tester[i], 
			tournament_size=tournament_size, data_to_store=data_folder_list[2], serial_number=serial_number)

def test_impact_tournament_size(serial_number): 

	for i in range(len(liste_tournois_a_tester)):
		print('Test for tournaments of size ',liste_tournois_a_tester[i])
		Main(generation_number=generation_number, population_size=population_size, mutation_rate=mutation_rate, 
			tournament_size=liste_tournois_a_tester[i], data_to_store=data_folder_list[3], serial_number=serial_number)

###### Fonctions d'interprétation ###############

def plot_results(data_folder,parametre,liste_a_tester,sub_folder,data_str):

	perf_list, diff_list, result_list = [],[],[]

	# On crée le dossier de sauvegarde
	saving_path = os.path.join(plot_result_folder,sub_folder) 
	if not os.path.exists(saving_path):
		os.makedirs(saving_path)

	# On extrait les données et on remplit les dictionnaires 
	for i in range(10):

		# On regarde où sont stockées les données 
		data_access_path = os.path.join(tests_result_folder,test_serial_list[i])
		perf_list_tempo,diff_list_tempo,result_list_tempo = [],[],[]

		for elem in liste_a_tester:

			file_title = 'fitness_for_'+ elem + data_str + test_serial_list[i] + '.npz'
			data_path = os.path.join(data_access_path,data_folder,file_title)
			data = np.load(data_path)
			[initial_cost,final_cost,time_elapsed,best_gen] = data['a']
			result_list_tempo.append(final_cost)
			diff_list_tempo.append(initial_cost-final_cost)
			perf_list_tempo.append(generation_number/best_gen)

		result_list.append(result_list_tempo)
		diff_list.append(diff_list_tempo)
		perf_list.append(perf_list_tempo)	

	# On crée les dataframes
	df_result = pd.DataFrame(result_list)	
	df_diff = pd.DataFrame(diff_list)	
	df_perf = pd.DataFrame(perf_list)	
	liste_df = [df_result,df_diff,df_perf]

	# On met les parametre en index de notre dataframe 
	for i in range(3):
		df = liste_df[i]
		if liste_a_tester == liste_mut_a_tester:
			df.columns =  liste_mut_a_tester_2
		else:	
			df.columns = liste_a_tester	
		df.index = test_serial_list
	
	
	# On génère les figures, d'abord les régressions logarithmiques puis les régressions linéraires
	for j in range(2):
		for i in range(len(liste_df)):

			# On stocke le nom des colonnes dans des listes pour les arguments des fonctions seaborn 
			col_names = liste_df[i].columns.values.tolist()
			palette_lp = (sns.color_palette("hls",len(col_names)))
			sns.set()

			if j == 0: 
				# sns.lineplot(data=liste_df[i].T,dashes=False,estimator=None)
				sns.swarmplot(data=liste_df[i])
				save_name_lp = os.path.join(saving_path,'regplot '+ liste_label[i] + '.png')
				plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
				plt.tight_layout()
			else:
				sns.boxplot(data=liste_df[i])
				save_name_lp = os.path.join(saving_path,'boxplot '+ liste_label[i]+ '.png')
			
			# On nomme les axes et on sauvegarde la figure
			plt.xlabel(parametre)
			plt.ylabel(liste_label[i])
			plt.savefig(save_name_lp)
			plt.close()

###### Main #####################################

def main_test_function():
	"""Automatise les tests"""

	for j in range(len(test_serial_list)):

		current_serie = test_serial_list[j]
		print('################# BEGINNING SERIE NUMBER ' + str(j+1) + ' #################')
		print('')

		for i in range(len(liste_a_tester)):
			if i == 0:
				print('################# TEST POPULATION SIZE IMPACT #################')
				test_impact_population_number(current_serie)
			elif i == 1:
				print('################# TEST GENERATION NUMBER IMPACT #################')
				test_impact_generation_number(current_serie)
			elif i == 2:
				print('################# TEST MUTATION RATE IMPACT #################')
				test_impact_mutation_rate(current_serie)
			else:
				print('################# TEST TOURNAMENT SIZE IMPACT #################')
				test_impact_tournament_size(current_serie)


def main_plot_function():
	"""Automatise les créations des figures"""

	for i in tqdm(range(len(liste_a_tester))):
		if i == 0:
			data_str = 'pop'
		elif i == 1:
			data_str = 'gen'
		elif i == 2:
			data_str = 'mut'
		else:
			data_str = 'tournois'
	
		plot_results(data_folder_list[i],liste_parametre[i],liste_a_tester[i],plot_results_sub_folders[i],data_str)
		

if __name__ == '__main__':
	
	# main_test_function()

	main_plot_function()