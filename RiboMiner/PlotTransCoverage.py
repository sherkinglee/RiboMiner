#!/usr/bin/env python
# -*- coding:UTF-8 -*-
'''
@Author: Li Fajin
@Date: 2020-01-07 15:21:12
LastEditors: Li Fajin
LastEditTime: 2020-12-29 11:20:28
@Description: The script is used for plot position depth for each longest transcript.
Usage: python PlotTransCoverage.py -i coverage.txt -o output_prefix -c coorFile -t [transcript_id|gene_id|gene_name] -m [single-gene|gene-list] --id-type [transcript_id|gene_id|gene_name] --color [lightskyblue]
'''

from .FunctionDefinition import *
from .__init__ import __version__
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
import seaborn as sns
from optparse import OptionParser



def create_parse_for_trans_coverage():
	'''argument parser'''
	usage="usage: python %prog [options]"
	parser=OptionParser(usage=usage,version=__version__)
	parser.add_option('-i','--input',action="store",type="string",dest="InputFile",help="Coverage file generated by CoverageOfEachTrans.py.[required]")
	parser.add_option('-o',"--otput_prefix",action="store",type="string",dest="output_prefix",help="Prefix of output files.[required]")
	parser.add_option("-c","--coordinateFile",action="store",type="string",dest="coorFile",
			help="The file should contain the coordinate of start and stop codon. Generated by OutputTranscriptInfo.py.[required]")
	parser.add_option("-t","--target-gene",action="store",type="string",dest="targetGene",
			help="Target genes for plot. If '-m single-gene', '-t' is a gene name or gene id or transcript id; elif '-m gene-list', '-t' is a file containing some gene names or gene ids or transcript ids with a column name.")
	parser.add_option('--id-type',action="store",type="string",dest="id_type",default="transcript_id",
			help="define the id type users input. the default is transcript id, if not, will be transformed into transcript id. default=%default")
	parser.add_option('--color',action="store",type="string",dest="color",default="lightskyblue",
			help="Color for plot. default=%default")
	parser.add_option("--ymax",action="store",type="float",dest="ymax",default=None,help="The max of ylim. default=%default")
	parser.add_option("--ymin",action="store",type="float",dest="ymin",default=None,help="The min of ylim. default=%default")
	parser.add_option("--type",action="store",type="string",dest="Type",default='single-gene',
			help="Type for input. Either 'single-gene' or 'gene-list'. default=%default.")
	parser.add_option('--mode',action="store",type="string",dest="mode",default="coverage",
			help="Mode of calculation. Either coverage or density of a transcript or transcripts. default=%default")
	return parser

def PlotForSingeGeneCoverage(Coverage,targetTrans,startCoor,stopCoor,trans2GeneDict,color,output_prefix,ymin,ymax):
	singleTransCoverage=Coverage[targetTrans]
	targetTransLength=len(singleTransCoverage)
	label=trans2GeneDict[targetTrans]+":"+targetTrans
	plt.rc("font",family="Arial",weight="bold")
	fig=plt.subplots(figsize=(8,4))
	gs = gridspec.GridSpec(2,1,height_ratios=[11,1],hspace=0.6,left=0.2,right=0.95)
	ax1=plt.subplot(gs[0])
	color=color
	ax1.bar(np.arange(targetTransLength),singleTransCoverage,width=1,facecolor=color)
	# ax1.vlines(np.arange(targetTransLength),ymin=0,ymax=singleTransCoverage,colors=color)
	ax1.spines["top"].set_visible(False)
	ax1.spines["right"].set_visible(False)
	ax1.spines["bottom"].set_linewidth(2)
	ax1.spines["left"].set_linewidth(2)
	ax1.axvline(startCoor-1,color="gray",dashes=(3,2),alpha=0.5)
	ax1.axvline(stopCoor-1,color="gray",dashes=(3,2),alpha=0.5)
	ax1.tick_params(which="both",width=2,labelsize=18)
	ax1.set_ylabel("Relative Depth",fontsize=18,fontdict={"size":18,"family":"Arial","weight":"bold"})
	ax1.set_xlim(0,targetTransLength)
	if not ymin and not ymax:
		pass
	elif not ymin and ymax:
		ax1.set_ylim(0,ymax)
	elif ymin and not ymax:
		raise IOError("Please offer the ymax parameter as well!")
	elif ymin and ymax:
		ax1.set_ylim(ymin,ymax)
	else:
		raise IOError("Please enter correct ymin and ymax parameters!")
	plt.title(label,fontdict={"size":18,"family":"Arial","weight":"bold"},loc="center")

	width=0.15
	ax2=plt.subplot(gs[1])
	ax2.set_xlim(0,targetTransLength)
	ax2.fill((startCoor-1,stopCoor,stopCoor,startCoor-1),(1+width/2,1+width/2,1-width/2,1-width/2),color=color,lw=0.5,zorder=20)
	ax2.axhline(1,color='gray',lw=2)
	ax2.set_frame_on(False)
	ax2.xaxis.set_ticks_position("none")
	ax2.yaxis.set_ticks_position("none")
	ax2.set_xticks([])
	ax2.set_yticks([])
	ax2.set_ylim((1-width/2,1+width/2))
	plt.savefig(output_prefix+"_coverage.pdf")

def PlotForSingeGeneDensity(Density,targetTrans,startCoor,stopCoor,trans2GeneDict,color,output_prefix,ymin,ymax):
	singleTransDensity=Density[targetTrans]
	targetTransLength=len(singleTransDensity)
	label=trans2GeneDict[targetTrans]+":"+targetTrans
	# colors = sns.color_palette('husl',3)*(1+targetTransLength//3)
	# colors = ["red","blue","green"]*targetTransLength
	if targetTransLength%3==0:
		colors = sns.color_palette('husl',3)*(targetTransLength//3)
	elif targetTransLength%3==1:
		colors = sns.color_palette('husl',3)*(1+targetTransLength//3)
		colors=colors[:-2]
	elif targetTransLength%3==2:
		colors = sns.color_palette('husl',3)*(1+targetTransLength//3)
		colors=colors[:-1]
	plt.rc("font",family="Arial",weight="bold")
	fig=plt.subplots(figsize=(8,4))
	gs = gridspec.GridSpec(2,1,height_ratios=[11,1],hspace=0.6,left=0.2,right=0.95)
	ax1=plt.subplot(gs[0])
	ax1.vlines(np.arange(targetTransLength),ymin=np.zeros(targetTransLength),ymax=singleTransDensity,colors=colors,linewidth=2)
	# ax1.bar(np.arange(targetTransLength),singleTransDensity,width=1,facecolor=color)
	# ax1.vlines(np.arange(targetTransLength),ymin=0,ymax=singleTransDensity,colors=color)
	ax1.spines["top"].set_visible(False)
	ax1.spines["right"].set_visible(False)
	ax1.spines["bottom"].set_linewidth(2)
	ax1.spines["left"].set_linewidth(2)
	ax1.axvline(startCoor-1,color="gray",dashes=(3,2),alpha=0.5)
	ax1.axvline(stopCoor-1,color="gray",dashes=(3,2),alpha=0.5)
	ax1.tick_params(which="both",width=2,labelsize=18)
	ax1.set_ylabel("Relative Density",fontsize=18,fontdict={"size":18,"family":"Arial","weight":"bold"})
	ax1.set_xlim(0,targetTransLength)
	if not ymin and not ymax:
		pass
	elif not ymin and ymax:
		ax1.set_ylim(0,ymax)
	elif ymin and not ymax:
		raise IOError("Please offer the ymax parameter as well!")
	elif ymin and ymax:
		ax1.set_ylim(ymin,ymax)
	else:
		raise IOError("Please enter correct ymin and ymax parameters!")
	legend_elements=[Line2D([0],[0],color=colors[startCoor-1],lw=2,label="Frame 0"),
					 Line2D([0],[0],color=colors[startCoor],lw=2,label="Frame 1"),
					 Line2D([0],[0],color=colors[startCoor+1],lw=2,label="Frame 2")]
	ax1.legend(handles=legend_elements,loc="best")
	plt.title(label,fontdict={"size":18,"family":"Arial","weight":"bold"},loc="center")

	width=0.15
	ax2=plt.subplot(gs[1])
	ax2.set_xlim(0,targetTransLength)
	ax2.fill((startCoor-1,stopCoor,stopCoor,startCoor-1),(1+width/2,1+width/2,1-width/2,1-width/2),color=color,lw=0.5,zorder=20)
	ax2.axhline(1,color='gray',lw=2)
	ax2.set_frame_on(False)
	ax2.xaxis.set_ticks_position("none")
	ax2.yaxis.set_ticks_position("none")
	ax2.set_xticks([])
	ax2.set_yticks([])
	ax2.set_ylim((1-width/2,1+width/2))
	plt.savefig(output_prefix+"_density.pdf")

def PlotForGeneListsCoverage(Coverage,targetTrans,startCoorDict,stopCoorDict,trans2GeneDict,color,output_prefix,ymin,ymax):
	with PdfPages(output_prefix + "_coverage.pdf") as pdf:
		for trans in targetTrans:
			if trans not in Coverage:
				continue
			plt.rc("font",family="Arial",weight="bold")
			fig=plt.subplots(figsize=(8,4))
			singleTransCoverage=Coverage[trans]
			targetTransLength=len(singleTransCoverage)
			label=trans2GeneDict[trans]+":"+trans
			gs = gridspec.GridSpec(2,1,height_ratios=[11,1],hspace=0.6,left=0.2,right=0.95)
			ax1=plt.subplot(gs[0])
			color=color
			ax1.bar(np.arange(targetTransLength),singleTransCoverage,width=1,facecolor=color)
			# ax1.vlines(np.arange(targetTransLength),ymin=0,ymax=singleTransCoverage,colors=color)
			ax1.spines["top"].set_visible(False)
			ax1.spines["right"].set_visible(False)
			ax1.spines["bottom"].set_linewidth(2)
			ax1.spines["left"].set_linewidth(2)
			ax1.axvline(startCoorDict[trans]-1,color="gray",dashes=(3,2),alpha=0.5)
			ax1.axvline(stopCoorDict[trans]-1,color="gray",dashes=(3,2),alpha=0.5)
			ax1.tick_params(which="both",width=2,labelsize=18)
			ax1.set_ylabel("Relative Depth",fontsize=18,fontdict={"size":18,"family":"Arial","weight":"bold"})
			ax1.set_xlim(0,targetTransLength)
			if not ymin and not ymax:
				pass
			elif not ymin and ymax:
				ax1.set_ylim(0,ymax)
			elif ymin and not ymax:
				raise IOError("Please offer the ymax parameter as well!")
			elif ymin and ymax:
				ax1.set_ylim(ymin,ymax)
			else:
				raise IOError("Please enter correct ymin and ymax parameters!")
			plt.title(label,fontdict={"size":18,"family":"Arial","weight":"bold"},loc="center")

			width=0.15
			ax2=plt.subplot(gs[1])
			ax2.set_xlim(0,targetTransLength)
			ax2.fill((startCoorDict[trans]-1,stopCoorDict[trans],stopCoorDict[trans],startCoorDict[trans]-1),(1+width/2,1+width/2,1-width/2,1-width/2),color=color,lw=0.5,zorder=20)
			ax2.axhline(1,color='gray',lw=2)
			ax2.set_frame_on(False)
			ax2.xaxis.set_ticks_position("none")
			ax2.yaxis.set_ticks_position("none")
			ax2.set_xticks([])
			ax2.set_yticks([])
			ax2.set_ylim((1-width/2,1+width/2))
			pdf.savefig()
		plt.close()

def PlotForGeneListsDensity(Density,targetTrans,startCoorDict,stopCoorDict,trans2GeneDict,color,output_prefix,ymin,ymax):
	with PdfPages(output_prefix + "_density.pdf") as pdf:
		for trans in targetTrans:
			if trans not in Density:
				continue
			plt.rc("font",family="Arial",weight="bold")
			fig=plt.subplots(figsize=(8,4))
			singleTransDensity=Density[trans]
			targetTransLength=len(singleTransDensity)
			label=trans2GeneDict[trans]+":"+trans
			gs = gridspec.GridSpec(2,1,height_ratios=[11,1],hspace=0.6,left=0.2,right=0.95)
			ax1=plt.subplot(gs[0])
			# colors = sns.color_palette('husl',3)*(1+targetTransLength//3)
			# colors = ["red","blue","green"]*targetTransLength
			if targetTransLength%3==0:
				colors = sns.color_palette('husl',3)*(targetTransLength//3)
			elif targetTransLength%3==1:
				colors = sns.color_palette('husl',3)*(1+targetTransLength//3)
				colors=colors[:-2]
			elif targetTransLength%3==2:
				colors = sns.color_palette('husl',3)*(1+targetTransLength//3)
				colors=colors[:-1]
			ax1.vlines(np.arange(targetTransLength),ymin=np.zeros(targetTransLength),ymax=singleTransDensity,colors=colors,linewidth=2)
			# ax1.vlines(np.arange(targetTransLength),ymin=0,ymax=singleTransDensity,colors=color)
			ax1.spines["top"].set_visible(False)
			ax1.spines["right"].set_visible(False)
			ax1.spines["bottom"].set_linewidth(2)
			ax1.spines["left"].set_linewidth(2)
			ax1.axvline(startCoorDict[trans]-1,color="gray",dashes=(3,2),alpha=0.5)
			ax1.axvline(stopCoorDict[trans]-1,color="gray",dashes=(3,2),alpha=0.5)
			ax1.tick_params(which="both",width=2,labelsize=18)
			ax1.set_ylabel("Relative Density",fontsize=18,fontdict={"size":18,"family":"Arial","weight":"bold"})
			ax1.set_xlim(0,targetTransLength)
			if not ymin and not ymax:
				pass
			elif not ymin and ymax:
				ax1.set_ylim(0,ymax)
			elif ymin and not ymax:
				raise IOError("Please offer the ymax parameter as well!")
			elif ymin and ymax:
				ax1.set_ylim(ymin,ymax)
			else:
				raise IOError("Please enter correct ymin and ymax parameters!")
			legend_elements=[Line2D([0],[0],color=colors[startCoorDict[trans]-1],lw=2,label="Frame 0"),
							Line2D([0],[0],color=colors[startCoorDict[trans]],lw=2,label="Frame 1"),
							Line2D([0],[0],color=colors[startCoorDict[trans]+1],lw=2,label="Frame 2")]
			ax1.legend(handles=legend_elements,loc="best")
			plt.title(label,fontdict={"size":18,"family":"Arial","weight":"bold"},loc="center")

			width=0.15
			ax2=plt.subplot(gs[1])
			ax2.set_xlim(0,targetTransLength)
			ax2.fill((startCoorDict[trans]-1,stopCoorDict[trans],stopCoorDict[trans],startCoorDict[trans]-1),(1+width/2,1+width/2,1-width/2,1-width/2),color=color,lw=0.5,zorder=20)
			ax2.axhline(1,color='gray',lw=2)
			ax2.set_frame_on(False)
			ax2.xaxis.set_ticks_position("none")
			ax2.yaxis.set_ticks_position("none")
			ax2.set_xticks([])
			ax2.set_yticks([])
			ax2.set_ylim((1-width/2,1+width/2))
			pdf.savefig()
		plt.close()

def read_coverage(Coverage):
	coverageDict={}
	with open(Coverage,'r') as f:
		for line in f:
			trans_id=line.strip().split("\t")[0]
			depth=np.array([float(i) for i in line.strip().split("\t")[1:]])
			coverageDict[trans_id]=depth
	return coverageDict

def parse_for_trans_coverage():
	parser=create_parse_for_trans_coverage()
	(options,args)=parser.parse_args()
	(InputFile,output_prefix,coorFile,Type,targetGene,id_type,color,ymin,ymax)=(options.InputFile,options.output_prefix,options.coorFile,options.Type,
    options.targetGene,options.id_type,options.color,options.ymin,options.ymax)
	CoverageDict=read_coverage(InputFile)
	selectTrans,transLengthDict,startCodonCoorDict,stopCodonCoorDict,transID2geneID,transID2geneName,cdsLengthDict,transID2ChromDict=reload_transcripts_information(coorFile)
	geneID2transID={v:k for k,v in transID2geneID.items()}
	geneName2transID={v:k for k,v in transID2geneName.items()}
	if Type == 'single-gene':
		if id_type=='transcript_id':
			targetTrans=targetGene
		elif id_type=='gene_id':
			try:
				targetTrans=geneID2transID[targetGene]
			except IOError:
				print("There is no such target gene in annotation file!")
		elif id_type=='gene_name':
			try:
				targetTrans=geneName2transID[targetGene]
			except IOError:
				print("There is no such target gene in annotation file!")
		else:
			raise IOError("Please input a approproate id_type parameters.[transcript_id/gene_id/gene_name/]")
		if targetTrans  not in CoverageDict:
			raise IOError("There is no such "+targetGene +" in input file.")
		print("Start plot...",file=sys.stderr)
		if options.mode.strip().upper() in ["COVERAGE","C"]:
			PlotForSingeGeneCoverage(CoverageDict,targetTrans,startCodonCoorDict[targetTrans],stopCodonCoorDict[targetTrans],transID2geneName,color,output_prefix,ymin,ymax)
		elif options.mode.strip().upper() in ["DENSITY","COUNTS","COUNT","D"]:
			PlotForSingeGeneDensity(CoverageDict,targetTrans,startCodonCoorDict[targetTrans],stopCodonCoorDict[targetTrans],transID2geneName,color,output_prefix,ymin,ymax)
		else:
			raise IOError("Please reset your --mode parameter! [coverage/c or density/d]")
		print("Finish!",file=sys.stderr)
	elif Type == 'gene-list':
		targetTrans=pd.read_csv(targetGene,sep="\t")
		targetTrans=set(targetTrans.iloc[:,0].values)
		if id_type=='transcript_id':
			pass
		elif id_type=='gene_id':
			targetTrans=set([geneID2transID[gene] for gene in targetTrans if gene in geneID2transID.keys()])
		elif id_type=='gene_name':
			targetTrans=set([geneName2transID[gene] for gene in targetTrans if gene in geneName2transID.keys()])
		else:
			raise IOError("Please input a approproate id_type parameters.[transcript_id/gene_id/gene_name/]")
		print("Start plot...",file=sys.stderr)
		if options.mode.strip().upper() in ["COVERAGE","C"]:
			PlotForGeneListsCoverage(CoverageDict,targetTrans,startCodonCoorDict,stopCodonCoorDict,transID2geneName,color,output_prefix,ymin,ymax)
		elif options.mode.strip().upper() in ["DENSITY","COUNTS","COUNT","D"]:
			PlotForGeneListsDensity(CoverageDict,targetTrans,startCodonCoorDict,stopCodonCoorDict,transID2geneName,color,output_prefix,ymin,ymax)
		else:
			raise IOError("Please reset your --mode parameter! [coverage/c or density/d]")
		print("Finish!",file=sys.stderr)
	else:
		raise IOError("Please enter a correct mode [single-gene or gene-list]")

def main():
	parse_for_trans_coverage()


if __name__=="__main__":
	main()