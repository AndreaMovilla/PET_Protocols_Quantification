import numpy as np
import nrrd
from os import walk
from os.path import splitext
from os.path import join


def importnrrd(path):
	foodir = path
	barlist = list()

	for root, dirs, files in walk(foodir):
		for f in files:
			if splitext(f)[1].lower() == ".nrrd":
				barlist.append(join(root, f))

	imagenes_nrrd = []
	barlist_sorted = sorted(barlist)
	for i in range(0, len(barlist_sorted)):
		imagenes_nrrd.append(nrrd.read(barlist_sorted[i], index_order='F')[0])

	return imagenes_nrrd

def importheader(path):
	foodir = path
	barlist = list()

	for root, dirs, files in walk(foodir):
		for f in files:
			if splitext(f)[1].lower() == ".nrrd":
				barlist.append(join(root, f))

	imagenes_nrrd = []
	barlist_sorted = sorted(barlist)
	for i in range(0, len(barlist_sorted)):
		imagenes_nrrd.append(nrrd.read(barlist_sorted[i], index_order='F')[1])

	return imagenes_nrrd

def directories(path):
	foodir = path
	barlist = list()

	for root, dirs, files in walk(foodir):
		for f in files:
			if splitext(f)[1].lower() == ".nrrd":
				barlist.append(join(root, f))
	nombres = []
	barlist_sorted = sorted(barlist)
	for i in range(0, len(barlist_sorted)):
		nombres.append(barlist_sorted[i][-9:-5])
	return nombres


def names(path):
	foodir = path
	names = list()
	for root, dirs, files in walk(foodir):
		for f in files:
			if splitext(f)[1].lower() == ".nrrd":
				f.replace(".nrrd","")
				names.append(f)
	names_sorted=sorted(names)
	return names_sorted


def get_nbhd(pt, checked, dims):
    nbhd = []

    if (pt[0] > 0) and not checked[pt[0]-1, pt[1], pt[2]]:
        nbhd.append((pt[0]-1, pt[1], pt[2]))
    if (pt[1] > 0) and not checked[pt[0], pt[1]-1, pt[2]]:
        nbhd.append((pt[0], pt[1]-1, pt[2]))
    if (pt[2] > 0) and not checked[pt[0], pt[1], pt[2]-1]:
        nbhd.append((pt[0], pt[1], pt[2]-1))

    if (pt[0] < dims[0]-1) and not checked[pt[0]+1, pt[1], pt[2]]:
        nbhd.append((pt[0]+1, pt[1], pt[2]))
    if (pt[1] < dims[1]-1) and not checked[pt[0], pt[1]+1, pt[2]]:
        nbhd.append((pt[0], pt[1]+1, pt[2]))
    if (pt[2] < dims[2]-1) and not checked[pt[0], pt[1], pt[2]+1]:
        nbhd.append((pt[0], pt[1], pt[2]+1))

    return nbhd


def grow(img, seed, t, value):
	"""
    img: ndarray, ndim=3
        An image volume.

    seed: tuple, len=3
        Region growing starts from this point.

    t: int
        The image neighborhood radius for the inclusion criteria.
    """
	seg = np.zeros(img.shape, dtype=np.bool)
	checked = np.zeros_like(seg)

	seg[seed] = True
	checked[seed] = True
	needs_check = get_nbhd(seed, checked, img.shape)

	while len(needs_check) > 0:
		pt = needs_check.pop()

		# Its possible that the point was already checked and was
		# put in the needs_check stack multiple times.
		if checked[pt]: continue

		checked[pt] = True

		# Handle borders.
		imin = max(pt[0] - t, 0)
		imax = min(pt[0] + t, img.shape[0] - 1)
		jmin = max(pt[1] - t, 0)
		jmax = min(pt[1] + t, img.shape[1] - 1)
		kmin = max(pt[2] - t, 0)
		kmax = min(pt[2] + t, img.shape[2] - 1)

		if img[pt] >= value:
			# Include the voxel in the segmentation and
			# add its neighbors to be checked.
			seg[pt] = True
			needs_check += get_nbhd(pt, checked, img.shape)
	imageseg2=np.copy(img)*0
	imageseg2[~seg] = 0
	imageseg2[seg] = 1
	return imageseg2




def thresholdseg(seg, image, voxeldim):
	segmentbool = seg.astype('bool')
	imageseg = np.copy(image)
	imageseg[~segmentbool] = np.nan
	vmax = np.nanmax(imageseg)
	coord = np.where(imageseg == vmax)
	coordinates=(coord[0][0], coord[1][0], coord[2][0])
	# Calculamos la intensidad media de todos los puntos obtenidos
	v70 = np.mean(imageseg[imageseg >= 0.7 * vmax])
	v40 = 0.4 * v70
	# Calculamos segmentacion con region growing
	imageseg3=grow(image,coordinates,3,v40)
	## calculamos hasta que punto en el eje z tenemos valores superiores al 40% de la media del 70%
	#testz_down = 0
	#testz_up = 0
	#while valor40 < image[coord[0][0]][coord[1][0]][coord[2][0] + testz_down]:
	#	testz_down = testz_down - 1
	#testz_down = testz_down + 1
	#
	#while valor40 < image[coord[0][0]][coord[1][0]][coord[2][0] + testz_up]:
	#	testz_up = testz_up + 1
	#testz_up = testz_up - 1
	#
	## calculamos hasta que punto en el eje y tenemos valores superiores al 40% de la media del 70%
	#testy_down = 0
	#testy_up = 0
	#while valor40 < image[coord[0][0]][coord[1][0] + testy_up][coord[2][0]]:
	#	testy_up = testy_up + 1
	#testy_up = testy_up - 1
	#
	#while valor40 < image[coord[0][0]][coord[1][0] + testy_down][coord[2][0]]:
	#	testy_down = testy_down - 1
	#testy_down = testy_down + 1
	#
	## calculamos hasta que punto en el eje x tenemos valores superiores al 40% de la media del 70% ligado a los ejes z e y. obtenemos las coordenadas de todos los puntos
	#coord2 = []
	#for j in range(testz_down, testz_up):
	#	for i in range(testy_down, testy_up):
	#		testx_up = 0
	#		testx_down = -1
	#		while valor40 < image[coord[0][0] + testx_up][coord[1][0] + i][coord[2][0] + j]:
	#			coord2.append((coord[0][0] + testx_up, coord[1][0] + i, coord[2][0] + j))
	#			testx_up = testx_up + 1
	#		while valor40 < image[coord[0][0] + testx_down][coord[1][0] + i][coord[2][0] + j]:
	#			coord2.append((coord[0][0] + testx_down, coord[1][0] + i, coord[2][0] + j))
	#			testx_down = testx_down - 1
	#
	##con las coordenadas obtenemos la segmentación
	#imageseg2=np.copy(image)*0
	#for i in range(0,len(coord2)-1):
	#	imageseg2[coord2[i][0]][coord2[i][1]][coord2[i][2]]=1
	##obtenemos el volumen de la segmentación
	#numerovoxels = len(coord2)
	# Calculamos volumen
	numerovoxels=len(imageseg3[imageseg3 == 1])
	volumen = numerovoxels * (voxeldim**3) / 1000
	return volumen, imageseg3, vmax, v70


def repeatseg(image):
	image1= np.roll(image, 6, axis=1)
	image2=np.roll(image, 6, axis=1)
	finalimage=image+image1+image2
	return finalimage