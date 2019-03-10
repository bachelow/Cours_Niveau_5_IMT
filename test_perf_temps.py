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

###### Variables gobales ########################

# Les listes de noms pour sauvegarder / charger les données 
data_folder_list = ['data_gen','data_pop']
liste_parametre = ['Nombre de générations','Taille de la population']
liste_label = ['Temps total écoulé','Temps total écoulé']
plot_results_sub_folders = ['Etude temps gen','Etude temps pop']
plot_result_folder = 'C:/Users/mbach/Desktop/TELECOM Bretagne/Cours/ISA/Niveau 5/CaseStudy/GA/Cours_Niveau_5_IMT/plot_results'
tests_result_folder = 'C:/Users/mbach/Desktop/TELECOM Bretagne/Cours/ISA/Niveau 5/CaseStudy/GA/Tests'
test_serial_list = ['Serie_1','Serie_2','Serie_3','Serie_4','Serie_5','Serie_6','Serie_7','Serie_8','Serie_9','Serie_10']

# On va étudier le temps que en fonction du nombre de génération et en fonction de la taille de la population 
# On n'a pas besoin des autres données tournois et mutations
data_str_list = ['gen','pop']
liste_gen_a_tester = [str(10*i) for i in range(1,11)]
liste_pop_a_tester = [str(10*i) for i in range(3,11)]
liste_a_tester = [liste_gen_a_tester,liste_pop_a_tester]

###### Fonctions d'interprétation ###############

def plot_results(data_folder,parametre,liste_a_tester,sub_folder,data_str):

	liste_temps = []

	# On créer le dossier de sauvegarde
	saving_path = os.path.join(plot_result_folder,sub_folder) 
	if not os.path.exists(saving_path):
		os.makedirs(saving_path)

	# On extrait les données et on remplit les dictionnaires 
	for i in range(10):

		# On regarde où sont stockées les données 
		data_access_path = os.path.join(tests_result_folder,test_serial_list[i])
		liste_temps_tempo = []

		for elem in liste_a_tester:

			file_title = 'fitness_for_'+ elem + data_str + test_serial_list[i] + '.npz'
			data_path = os.path.join(data_access_path,data_folder,file_title)
			data = np.load(data_path)
			[initial_cost,final_cost,time_elapsed,best_gen] = data['a']
			liste_temps_tempo.append(time_elapsed)

		liste_temps.append(liste_temps_tempo)	

	# On créer les dataframes
	df_temps = pd.DataFrame(liste_temps)	
	liste_df = [df_temps]

	# On met les parametre en index de notre dataframe 
	df_temps.columns = liste_a_tester	
	df_temps.index = test_serial_list
	
	
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
				save_name_lp = os.path.join(saving_path,'swarmplot '+ liste_label[i] + '.png')
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


if __name__ == '__main__':
	
	for i in tqdm(range(2)):
		plot_results(data_folder_list[i],liste_parametre[i],liste_a_tester[i],plot_results_sub_folders[i],data_str_list[i])