#!/usr/bin/env python
# -*- coding:UTF-8 -*-
'''
@Author: Li Fajin
@Date: 2020-01-07 10:26:31
LastEditors: Li Fajin
LastEditTime: 2020-12-27 17:09:09
@Description: This script is used for statistic of coverage for each transcript.
'''



import pysam
import pysamstats
import numpy as np
from .FunctionDefinition import *
from .__init__ import __version__



def create_parser_for_coverage():
	'''argument parser.'''
	usage="usage: python %prog [options]" + '\n' + __doc__ + "\n"
	parser=OptionParser(usage=usage,version=__version__)
	parser.add_option("-f","--bamListFile",action="store",type="string",default=None,dest="bamListFile",
			help="Bam file list, containing 4 columns.Namely bamFiles,readLength, offSet, bamLegend. '-f' and '-i, -r, -s, -t' parameters are mutually exclusive.default=%default.")
	parser.add_option("-i","--input", action="store",type="string",default=None,dest="bam_files",
			help="Input file(s) in bam format. All files should be split by comma e.g. 1.bam,2.bam,3.bam[required]. '-i' and '-f' are mutually exclusive. default=%default")
	parser.add_option("-c","--coordinateFile",action="store",type="string",dest="coorFile",
			help="The file should contain the coordinate of start and stop codon. Generated by OutputTranscriptInfo.py.[required]")
	parser.add_option("-o","--otput_prefix",action="store",type="string",dest="output_prefix",default=None,
			help="Prefix of output files.[required],default=%default")
	parser.add_option("-r","--specific_reads_length",action="store",type="string",dest="read_length",
			help="Specific the lenght to do analysis, comma split. e.g. '28,29,30'.If use all length set 'All'. Bam files diff length select split by '_' e.g. '28,29,30_ALL_27,28' [required]. '-r' and '-f' are mutually exclusive.")
	parser.add_option("-s","--offset",action="store",type="string",dest="read_offset",
			help="Specific the offset corresponding to read length, comma split. e.g. '12,13,13'. No offset set 0. Bam files diff offset select split by '_' e.g. '12,13,13_0_12,12' [required]. '-s' and '-f' are mutually exclusive.")
	parser.add_option("-t","--bam_file_legend",action="store",type="string",dest="bam_file_legend",
			help="The legend of each bam files, comma split. e.g. 'condition1,condition2,condition3' [required]. '-t' and '-f' are mutually exclusive.")
	parser.add_option('-S','--select_trans_list',action="store",type='string',dest='in_selectTrans',default=None,
			help="Selected transcript list used for metagene analysis.This files requires the first column must be the transcript ID  with a column name.")
	parser.add_option('--id-type',action="store",type="string",dest="id_type",default="transcript_id",
			help="define the id type users input. the default is transcript id, if not, will be transformed into transcript id. default=%default")
	parser.add_option('--mode',action="store",type="string",dest="mode",default="coverage",
			help="Mode of calculation. Either coverage or density of a transcript or transcripts. default=%default")
	return parser

def CalculateCoverage(in_bamFile,in_bamLegend,in_selectTrans,in_transLengthDict,in_startCodonCoorDict,in_stopCodonCoorDict,in_readLengths,in_readOffset,output_prefix):
	pysamFile=pysam.AlignmentFile(in_bamFile,"rb")
	pysamFile_trans=pysamFile.references
	in_selectTrans=set(pysamFile_trans).intersection(in_selectTrans)
	trans_set=set()
	all_counts=0
	if output_prefix:
		outputFileName=output_prefix+"_"+in_bamLegend
	else:
		outputFileName=in_bamLegend
	for trans in in_startCodonCoorDict.keys():
		leftCoor =int(in_startCodonCoorDict[trans])-1
		rightCoor=int(in_stopCodonCoorDict[trans])-3
		(trans_counts,read_counts_frameSum,total_reads,cds_reads)=get_trans_frame_counts(pysamFile, trans, in_readLengths, in_readOffset, in_transLengthDict[trans], leftCoor, rightCoor)
		all_counts+=total_reads ## total_reads for transcript level

	with open(outputFileName+"_raw_depth.txt",'w') as f1, open(outputFileName+"_RPM_depth.txt",'w') as f2:
		for trans in in_selectTrans:
			# print(trans)
			tmpTrans=pysamstats.load_coverage(pysamFile,chrom=trans,pad=True)
			tmpTransRaw=np.array([i[2] for i in tmpTrans])
			tmpTransRPM=10**6*(tmpTransRaw/all_counts)
			trans_set.add(trans)
			f1.write("%s\t" %(trans))
			f2.write("%s\t" %(trans))
			for i in range(len(tmpTrans)):
				f1.write("%s\t" %(str(tmpTransRaw[i])))
				f2.write("%s\t" %(str(tmpTransRPM[i])))
			f1.write("\n")
			f2.write("\n")
		print("There are about " + str(len(trans_set)) +" transcripts used for coverage calculation!", file=sys.stderr)

def CalculateDensity(in_bamFile,in_bamLegend,in_selectTrans,in_transLengthDict,in_startCodonCoorDict,in_stopCodonCoorDict,in_readLengths,in_readOffset,output_prefix):
	pysamFile=pysam.AlignmentFile(in_bamFile,"rb")
	pysamFile_trans=pysamFile.references
	in_selectTrans=set(pysamFile_trans).intersection(in_selectTrans)
	trans_set=set()
	all_counts=0
	if output_prefix:
		outputFileName=output_prefix+"_"+in_bamLegend
	else:
		outputFileName=in_bamLegend
	for trans in in_startCodonCoorDict.keys():
		leftCoor =int(in_startCodonCoorDict[trans])-1
		rightCoor=int(in_stopCodonCoorDict[trans])-3
		(trans_counts,read_counts_frameSum,total_reads,cds_reads)=get_trans_frame_counts(pysamFile, trans, in_readLengths, in_readOffset, in_transLengthDict[trans], leftCoor, rightCoor)
		all_counts+=total_reads ## total_reads for transcript level

	with open(outputFileName+"_raw_density.txt",'w') as f1, open(outputFileName+"_RPM_density.txt",'w') as f2:
		for trans in in_selectTrans:
			leftCoor =int(in_startCodonCoorDict[trans])-1
			rightCoor=int(in_stopCodonCoorDict[trans])-3
			# print(trans)
			(trans_counts,read_counts_frameSum,total_reads,cds_reads)=get_trans_frame_counts(pysamFile, trans, in_readLengths, in_readOffset, in_transLengthDict[trans], leftCoor, rightCoor)
			tmpTransRaw=np.array(trans_counts)
			tmpTransRPM=10**6*(tmpTransRaw/all_counts)
			trans_set.add(trans)
			f1.write("%s\t" %(trans))
			f2.write("%s\t" %(trans))
			for i in range(len(trans_counts)):
				f1.write("%s\t" %(str(tmpTransRaw[i])))
				f2.write("%s\t" %(str(tmpTransRPM[i])))
			f1.write("\n")
			f2.write("\n")
		print("There are about " + str(len(trans_set)) +" transcripts used for ribosome density calculation!", file=sys.stderr)

def IDtransForm(in_selectTrans,coorFile,id_type):
	selectTrans,transLengthDict,startCodonCoorDict,stopCodonCoorDict,transID2geneID,transID2geneName,cdsLengthDict,transID2ChromDict=reload_transcripts_information(coorFile)
	geneID2transID={v:k for k,v in transID2geneID.items()}
	geneName2transID={v:k for k,v in transID2geneName.items()}
	if in_selectTrans:
		select_trans=pd.read_csv(in_selectTrans,sep="\t")
		select_trans=set(select_trans.iloc[:,0].values)
		if id_type == 'transcript_id':
			select_trans=select_trans.intersection(selectTrans)
			print("There are " + str(len(select_trans)) + " transcripts from "+in_selectTrans+" used for following analysis.",file=sys.stderr)
		elif id_type == 'gene_id':
			tmp=[geneID2transID[gene_id] for gene_id in select_trans if gene_id in geneID2transID]
			select_trans=set(tmp)
			select_trans=select_trans.intersection(selectTrans)
			print("There are " + str(len(select_trans))+" gene id could be transformed into transcript id and used for following analysis.",file=sys.stderr)
		elif id_type == 'gene_name' or id_type=='gene_symbol':
			tmp=[geneName2transID[gene_name] for gene_name in select_trans if gene_name in geneName2transID]
			select_trans=set(tmp)
			select_trans=select_trans.intersection(selectTrans)
			print("There are " + str(len(select_trans))+" gene symbol could be transformed into transcript id and used for following analysis.",file=sys.stderr)
		else:
			raise IOError("Please input a approproate id_type parameters.[transcript_id/gene_id/gene_name/]")
	else:
		select_trans=selectTrans

	return select_trans,transLengthDict,startCodonCoorDict,stopCodonCoorDict

def main():
	parser=create_parser_for_coverage()
	(options,args)=parser.parse_args()
	if options.bamListFile and (options.bam_files or options.read_length or options.read_offset or options.bam_file_legend):
		raise IOError("'-f' parameter and '-i -r -s -t' are mutually exclusive.")
	if options.bamListFile:
		bamFiles,readLengths,Offsets,bamLegends=parse_bamListFile(options.bamListFile)
	elif options.bam_files:
		bamFiles,readLengths,Offsets,bamLegends=options.bam_files.split(","),options.read_length.split("_"),options.read_offset.split("_"),options.bam_file_legend.split(",")
	else:
		raise IOError("Please check you input files!")

	print("your input : "+ str(len(bamFiles))+" bam files",file=sys.stderr)
	bam_attr=[]
	for ii,jj,mm,nn in zip(bamFiles,readLengths,Offsets,bamLegends):
		bam=bam_file_attr(ii,jj,mm,nn)
		bam_attr.append(bam)
	select_trans,transLengthDict,startCodonCoorDict,stopCodonCoorDict=IDtransForm(options.in_selectTrans,options.coorFile,options.id_type)
	for bamfs in bam_attr:
		if options.mode.strip().upper() in ["COVERAGE","C"]:
			CalculateCoverage(bamfs.bamName,bamfs.bamLegend,select_trans,transLengthDict,startCodonCoorDict,stopCodonCoorDict,bamfs.bamLen,bamfs.bamOffset,options.output_prefix)
		elif options.mode.strip().upper() in ["DENSITY","COUNTS","COUNT","D"]:
			CalculateDensity(bamfs.bamName,bamfs.bamLegend,select_trans,transLengthDict,startCodonCoorDict,stopCodonCoorDict,bamfs.bamLen,bamfs.bamOffset,options.output_prefix)
		else:
			raise IOError("Please reset your --mode parameter! [coverage/c or density/d]")


if __name__=="__main__":
    main()