#!/usr/bin/env python3

#change above if your python 3 environment has a different name

#usage:
#species2taxid.py list-of-species.txt outputfile.txt localdbfile.txt
#if not using local file leave blank


import sys
from Bio import Entrez
import re
Entrez.email = "theodore.allnutt@rbg.vic.gov.au"

Entrez.api_key = "8c29872371a4c4de3fdc0c6570e15625ba08"


def tokenize(filename):
	digits = re.compile(r'(\d+)')
	return tuple(int(token) if match else token for token, match in ((fragment, digits.search(fragment)) for fragment in digits.split(filename)))


def get_taxid(species,extraterm):
	"""to get data from ncbi taxomomy, we need to have the taxid.  we can
	get that by passing the species name to esearch, which will return
	the tax id"""
	if len(species.split(" "))>2:
		species = species.split(" ")[0]+" "+species.split(" ")[1] #remove extra names
	
	if len(species.split(" "))==2:
		species = species.replace(" ", "+").strip()
		
		try:
			search = Entrez.esearch(term = extraterm+"[Orgn] AND "+species, db = "taxonomy", retmode = "xml")
	
			record = Entrez.read(search)
		
			return record['IdList'][0]
			
		except:
			return "failed"
			'''
			try: #this led to wrong taxons
				species = species.split("+")[0] #try just the genus
				search = Entrez.esearch(term = species, db = "taxonomy", retmode = "xml")
				record = Entrez.read(search)
				return record['IdList'][0]
				
			except:
				return "failed"
			'''
	if len(species.split(" "))==1:
		species=species.rstrip("\n")
		try:
			search = Entrez.esearch(term = extraterm+"[Orgn] AND "+species, db = "taxonomy", retmode = "xml")
	
			record = Entrez.read(search)
		
			return record['IdList'][0]
			
		except:
			return "failed"
		

def get_tax_data(taxid):
	"""once we have the taxid, we can fetch the record"""
	try:
		search = Entrez.efetch(id = taxid, db = "taxonomy", retmode = "xml")
		return Entrez.read(search)
	except:
		return "failed"

def getlocaldata(localdbfile):

	#open tax2lin.txt
	species2taxid={}
	taxid2lin={}
	
	t1=open(localdbfile,'r')
	
	for x in t1:
		#print(x)
		tax1=x.split("\t")[0]
		spec1=x.split("\t")[1].split(";")[-1].rstrip("\n")
		lin1=x.split("\t")[1].rstrip("\n")
		species2taxid[spec1]=tax1
		taxid2lin[tax1]=lin1
		
	t1.close()

	return(species2taxid,taxid2lin)
		

if __name__ == '__main__':



	Entrez.email = "theodore.allnutt@rbg.vic.gov.au"
	
	f = open(sys.argv[1],'r')
	
	localdbfile = sys.argv[3] #localdbfile
	extraterm=sys.argv[4] #Viridiplantae
	species2taxid,taxid2lin = getlocaldata(localdbfile)
	
	sppnames=set()
	for x in species2taxid.keys():
		sppnames.add(x)
	
	
	added=[]
	
	speciestoget=set() #settify the list of species names to get - did not do this in prev version.
	print("setifying input list")
	for x in f:
		k=x.rstrip("\n")
		if "." not in k:
			speciestoget.add(k)
		
	spptogetlist=[]
	for x in speciestoget:
		spptogetlist.append(x)
	spptogetlist.sort(key=tokenize)
		
	print("set",len(speciestoget))
	for i in spptogetlist:
		species_name = i
		
		#if species_name in added:#if already seen, then get from local db saved version, not online
			#t1.close()
			#species2taxid,taxid2lin = getlocaldata(localdbfile)
			#t1=open(localdbfile,'a')
		
		if species_name in sppnames:
		
			taxid = species2taxid[species_name]
			lineage = taxid2lin[taxid]
			print('localdb',species_name,taxid,lineage)
			g = open(sys.argv[2],'a')
			g.write(species_name+"\t"+taxid+"\t"+lineage+"\n")
			g.close()
			
		else:
		
			taxid = get_taxid(species_name,extraterm)
			
			taxid=taxid.split(",")[-1]
			
			if taxid!="failed":
				data = get_tax_data(taxid)
				lineage=""
				#lineage = data[0]['LineageEx']['ScientificName']
				try:
					for j in data[0]['LineageEx']:
						if j['Rank']=='superkingdom':
							lineage=lineage+j['ScientificName']
						if j['Rank']=='kingdom':
							lineage=lineage+";"+j['ScientificName']
						if j['Rank']=='phylum':
							lineage=lineage+";"+j['ScientificName']
						if j['Rank']=='class':
							lineage=lineage+";"+j['ScientificName']
						if j['Rank']=='order':
							lineage=lineage+";"+j['ScientificName']
						if j['Rank']=='family':
							lineage=lineage+";"+j['ScientificName']
						if j['Rank']=='genus':
							lineage=lineage+";"+j['ScientificName']
					lineage=lineage+";"+species_name
					g = open(sys.argv[2],'a')
					g.write(species_name+"\t"+taxid+"\t"+lineage+"\n")
					g.close()
					print(species_name,taxid,lineage)
					if species_name not in added:#only add new names once
						added.append(species_name)
						t1=open(localdbfile,'a')
						t1.write(taxid+"\t"+lineage+"\n")
						t1.close()
						
						#update dicts
						
						species2taxid[species_name]=taxid
						taxid2lin[taxid]=lineage
						
						
						
						
				except:
					print(species_name,taxid,lineage,"fault")
			else:
				g = open(sys.argv[2],'a')
				g.write(species_name+"\tno_taxid_found\n")
				print(species_name,"failed")
				g.close()
			
			
		