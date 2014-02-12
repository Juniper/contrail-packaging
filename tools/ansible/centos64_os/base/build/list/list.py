#!/usr/bin/python3
# coding: utf8

"""Šis ir testa skripts"""

def paradit_listi(liste, indent = False, limenis = 0):

	"""Funkcijas kaut ko dara, bet es aizmirsu ko"""

	for maz_liste in liste:
		if isinstance(maz_liste, list):
			paradit_listi(maz_liste, indent, limenis + 1)
		else:
			if indent:
				for tab in range(limenis):
					print("\t", end="")
			print(maz_liste)
