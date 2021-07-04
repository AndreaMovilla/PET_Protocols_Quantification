import numpy as np
import matplotlib
from numpy.core.fromnumeric import shape
matplotlib.use('Qt5Agg')
import nrrd
import cv2
from os import walk
from os.path import splitext
from os.path import join
from functions import *
import pandas as pd
import xlsxwriter

main_path = '/Users/andreamovilla/Desktop/TFM_Respiratory_NRRD/D01_NEMA/PET_analisis'
main_path_ref = '/Users/andreamovilla/Desktop/TFM_Respiratory_NRRD/D01_NEMA/M04_Static/Static' #Directorio a la carpeta de referencia
excelname='M01_sin1volumes.xlsx'
ad_time=[63811,62112] #Hora de estudio estático y estudio dinámico, en segundos
half_life=109.771*60 #Periodo de semidesintegración del radiotrzador, en segundos
time=ad_time[0]-ad_time[1] #Tiempo entre estudios
voxeldim =4# tamaño de los voxeles, en mm
voxeldimref =2# tamaño de los voxeles de la imagen de referencia, en mm


direct = directories(main_path + '/Reference_segmentations') #Directorio de las segmentaciones
seg = importnrrd(main_path + '/Reference_segmentations')  # Importamos segmentaciones de referencia
segref=importnrrd(main_path_ref + '/Reference_segmentations')  #  Segmentaciones de la imagen de referencia
imageref=nrrd.read(main_path_ref + '/PET/PET_Static.nrrd')[0]  #  Imagen de referencia
images = importnrrd(main_path + '/PET') # El que va bien
pets=names(main_path + '/PET') # Nombre de archivo de cada imagen PET


#Calculamos el volumen  de la imagen de referencia con Threshold segmentation
volumenesref = []

dicref = {}
dicref['Names'] = direct
imaxref=[]
i70ref=[]
for i in range(0, len(seg)):
	volumenref = thresholdseg(segref[i], imageref, voxeldimref)
	filename = 'TS_' + direct[i] + '_' + 'static.nrrd'
	nrrd.write(filename, volumenref[1])
	imaxref.append(volumenref[2])
	i70ref.append(volumenref[3])
	volumenesref.append(volumenref[0])
dicref['Estático'] = volumenesref
dicref['Estático I max'] = imaxref
dicref['Estático I 70 media'] = i70ref



#Calculamos el volumen  y el CR con Threshold segmentation y escribimos los valores en dos diccionarios
dic = {}
dic['Names'] = direct
dic2 = {}
dic2['Names'] = direct
for j in range(0, len(pets)):
	volumenes = []
	coordenadas = []
	RCtotal=[]
	imaxtotal = []
	i70total=[]
	for i in range(0, len(seg)):
		volumen = thresholdseg(seg[i], images[j], voxeldim)
		filename='TS_'+direct[i]+'_'+pets[j]
		nrrd.write(filename, volumen[1])
		RC=volumen[0]/volumenesref[i]
		imaxtotal.append(volumen[2]*np.exp(-np.log(2)*time/half_life))
		i70total.append(volumen[3]*np.exp(-np.log(2)*time/half_life))
		RCtotal.append(RC)
		volumenes.append(volumen[0])
	dic[pets[j]] = volumenes
	dic2[pets[j]] = RCtotal
	dic2['I70 media' + pets[j]] = i70total
	dic2['Imax'+pets[j]] = imaxtotal


# Guardamos valores del volumen y CR en un .xlxs
writer = pd.ExcelWriter(excelname)
dfref = pd.DataFrame(data=dicref)
dfref = (dfref.T)
dfref.to_excel(writer, sheet_name="Vol. estático")


df1 = pd.DataFrame(data=dic)
df1 = (df1.T)
df1.to_excel(writer, sheet_name="Volúmenes")


df2 = pd.DataFrame(data=dic2)
df2 = (df2.T)
df2.to_excel(writer, sheet_name="CR")
writer.save()



