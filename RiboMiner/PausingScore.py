#!/usr/bin/env python
# -*- coding:UTF-8 -*-
'''
the input are just the same as MetageneAnalysis.py but with longest.transcripts.cds.sequence.fa file input also which could be generated by GetProteinCodingSequence.py
output: pausing score files like this:
motif   si_3e_1_80S
MAA     0.0
AAT     0.0
ATA     0.0
TAL     0.0
ALL     0.0
LLE     0.0
LEA     0.0

each file has two columns:
col0: motifs
col1: pausing score.
'''

from .FunctionDefinition import *
from itertools import groupby
from collections import defaultdict
from functools import reduce
import re



def pausing_score(in_bamFile,in_selectTrans,in_transLengthDict,in_startCodonCoorDict,in_stopCodonCoorDict,in_readLengths,in_readOffset,inCDS_countsFilterParma,inCDS_lengthFilterParma,transcriptFasta,left_pos,right_pos,mode,bamLegend,table,output_prefix):
	'''calculate the pausing score of all tri-peptide motif'''
	if left_pos and (not right_pos):
		raise IOError("Please input the right position match with the left position!")
	if (not left_pos) and right_pos:
		raise IOError("Please input the left position match with the right position!")
	transcript_sequence=fastaIter(transcriptFasta)
	pysamFile=pysam.AlignmentFile(in_bamFile,'rb')
	pysamFile_trans=pysamFile.references
	in_selectTrans=set(pysamFile_trans).intersection(in_selectTrans)
	in_selectTrans=in_selectTrans.intersection(transcript_sequence.keys()).intersection(in_startCodonCoorDict.keys())
	fout=open(output_prefix+"_"+bamLegend+"_pausing_score.txt",'w+')
	fout.write("%s\t%s" %("motif",bamLegend))
	transcript_used=0
	all_counts=0
	motif_num=0
	for trans in in_startCodonCoorDict.keys():
		leftCoor =int(in_startCodonCoorDict[trans])-1
		rightCoor=int(in_stopCodonCoorDict[trans])-3
		(trans_counts,read_counts_frameSum,total_reads,cds_reads)=get_trans_frame_counts(pysamFile, trans, in_readLengths, in_readOffset, in_transLengthDict[trans], leftCoor, rightCoor)
		all_counts+=total_reads

	for trans in in_selectTrans:
		leftCoor =int(in_startCodonCoorDict[trans])-1 #the first base of start codon 0-base
		rightCoor=int(in_stopCodonCoorDict[trans])-3 #the first base of stop codon 0-base
		CDS_seq=transcript_sequence[trans][:-3]
		AA_seq=translation(CDS_seq,table=table,cds=False)
		(read_counts,read_counts_frameSum,trans_reads,cds_reads)=get_trans_frame_counts(pysamFile, trans, in_readLengths, in_readOffset, in_transLengthDict[trans], leftCoor, rightCoor)
		read_counts_frameSum_normed=10**6*(read_counts_frameSum/all_counts)
		sumValue=np.sum(read_counts_frameSum_normed)
		if left_pos and right_pos:
			if right_pos <= left_pos:
				raise IOError("The right position must be larger than the left position!")
			AA_seq_to_use=AA_seq[int(left_pos-1):right_pos] ## 25-75-----> [24:75]
			read_counts_frame=np.array(read_counts_frameSum_normed[int(left_pos-1):right_pos])
		else:
			AA_seq_to_use=AA_seq
			read_counts_frame=np.array(read_counts_frameSum_normed)
		if len(read_counts_frame) != len(AA_seq_to_use):
			# print("the lenght of density and AA are: "+ str(len(read_counts_frame))+"\t" + str(len(AA_seq_to_use)))
			continue
			# raise EOFError('The lenght of AA_seq is not equal to the lenght of read counts density')
		for i in np.arange(0,len(read_counts_frame),1):
			tmpScore=np.sum(read_counts_frame[i:i+3])/sumValue
			tmpMotif=''.join(AA_seq_to_use[i:i+3])
			fout.write("\n%s\t%s" %(tmpMotif,tmpScore))
			motif_num+=1
		transcript_used+=1
	fout.close()
	pysamFile.close()
	print("Start processing the sample " + str(in_bamFile),file=sys.stderr)
	print("The number of transcripts used for pausing score calulation is :" +str(transcript_used),file=sys.stderr)
	print("The number of motifs used for pausing score calculation is :" +str(motif_num),file=sys.stderr)


def filter_transcripts(in_bamFile,in_selectTrans,in_transLengthDict,in_startCodonCoorDict,in_stopCodonCoorDict,in_readLengths,in_readOffset,inCDS_countsFilterParma,inCDS_lengthFilterParma,transcriptFasta,left_pos,right_pos,mode,table):
	'''
	filters:

	'''
	transcript_sequence=fastaIter(transcriptFasta)
	pysamFile=pysam.AlignmentFile(in_bamFile,'rb')
	pysamFile_trans=pysamFile.references
	in_selectTrans=set(pysamFile_trans).intersection(in_selectTrans)
	in_selectTrans=in_selectTrans.intersection(transcript_sequence.keys()).intersection(in_startCodonCoorDict.keys())
	filter_1=0
	filter_2=0
	filter_3=0
	filter_4=0
	filter_5=0
	passTransSet=set()
	all_counts=0
	for trans in in_startCodonCoorDict.keys():
		leftCoor =int(in_startCodonCoorDict[trans])-1
		rightCoor=int(in_stopCodonCoorDict[trans])-3
		(trans_counts,read_counts_frameSum,total_reads,cds_reads)=get_trans_frame_counts(pysamFile, trans, in_readLengths, in_readOffset, in_transLengthDict[trans], leftCoor, rightCoor)
		all_counts+=total_reads

	for trans in in_selectTrans:
		leftCoor =int(in_startCodonCoorDict[trans])-1 #the first base of start codon 0-base
		rightCoor=int(in_stopCodonCoorDict[trans])-3 #the first base of stop codon 0-base
		CDS_seq=transcript_sequence[trans][:-3]## do not contain the stop codon
		AA_seq=translation(CDS_seq,table=table,cds=False)
		if len(CDS_seq) % 3 !=0:
			filter_1+=1
			continue
		if len(CDS_seq) < inCDS_lengthFilterParma:
			filter_2+=1
			continue
		(read_counts,read_counts_frameSum,trans_reads,cds_reads)=get_trans_frame_counts(pysamFile, trans, in_readLengths, in_readOffset, in_transLengthDict[trans], leftCoor, rightCoor)
		cds_reads_normed=10**9*(cds_reads/(all_counts*len(read_counts_frameSum)*3))
		if mode == 'RPKM':
			if cds_reads_normed < inCDS_countsFilterParma:
				filter_3+=1
				continue
		if mode == 'counts':
			if cds_reads < inCDS_countsFilterParma:
				filter_3+=1
				continue

		sumValue=np.sum(read_counts_frameSum)
		sumValue_normed=10**9*(sumValue/(all_counts*len(read_counts_frameSum)*3))
		if sumValue_normed==0:
			filter_4+=1
			continue
		if len(read_counts_frameSum) != len(AA_seq):
			filter_5+=1
			# print("the lenght of density and AA are: "+ str(len(read_counts_frameSum))+"\t" + str(len(AA_seq)))
			continue
			# raise EOFError('The lenght of AA_seq is not equal to the lenght of read counts density')
		passTransSet.add(trans)
	pysamFile.close()
	print("The number of transcripts filtered by filter1 (len(CDS_seq)%3!=0) is : " + str(filter_1),file=sys.stderr)
	print("The number of transcripts filtered by filter2 (len(CDS_seq)<inCDS_lengthFilterParma) is :" + str(filter_2),file=sys.stderr)
	print("The number of transcripts filtered by filter3 (cds_reads < inCDS_countsFilterParma(RPKM)) is : "+str(filter_3),file=sys.stderr)
	print("The number of transcripts filtered by filter4 (sum(cds_reads)==0) is : " + str(filter_4),file=sys.stderr)
	print("The number of transcripts filtered by filter5 (annotated imcomplete) is : " + str(filter_5),file=sys.stderr)
	print("The number of transcripts used for pausing score calulation in " + str(in_bamFile) + "is: "+str(len(passTransSet)),file=sys.stderr)
	return passTransSet


def parse_args_for_pausing_score_calculation():
	parsed=create_parse_for_pausing_score_calculation()
	(options,args)=parsed.parse_args()
	(output_prefix, min_cds_codon,min_cds_counts,left_position, right_position, transcript_fasta,mode,table) = (
	options.output_prefix,options.min_cds_codon,options.min_cds_counts,options.left_position,options.right_position,
	options.transcript_fasta,options.mode,options.geneticCode)

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
	selectTrans,transLengthDict,startCodonCoorDict,stopCodonCoorDict,transID2geneID,transID2geneName,cdsLengthDict,transID2ChromDict=reload_transcripts_information(options.coorFile)
	geneID2transID={v:k for k,v in transID2geneID.items()}
	geneName2transID={v:k for k,v in transID2geneName.items()}
	if options.in_selectTrans:
		select_trans=pd.read_csv(options.in_selectTrans,sep="\t")
		select_trans=set(select_trans.iloc[:,0].values)
		if options.id_type == 'transcript_id':
			select_trans=select_trans.intersection(selectTrans)
			print("There are " + str(len(select_trans)) + " transcripts from "+options.in_selectTrans+" used for following analysis.",file=sys.stderr)
		elif options.id_type == 'gene_id':
			tmp=[geneID2transID[gene_id] for gene_id in select_trans if gene_id in geneID2transID]
			select_trans=set(tmp)
			select_trans=select_trans.intersection(selectTrans)
			print("There are " + str(len(select_trans))+" gene id could be transformed into transcript id and used for following analysis.",file=sys.stderr)
		elif options.id_type == 'gene_name' or options.id_type=='gene_symbol':
			tmp=[geneName2transID[gene_name] for gene_name in select_trans if gene_name in geneName2transID]
			select_trans=set(tmp)
			select_trans=select_trans.intersection(selectTrans)
			print("There are " + str(len(select_trans))+" gene symbol could be transformed into transcript id and used for following analysis.",file=sys.stderr)
		else:
			raise IOError("Please input a approproate id_type parameters.[transcript_id/gene_id/gene_name/]")
	else:
		select_trans=selectTrans
	## get the common genes among all samples
	select_trans_list=[]
	for bamfs in bam_attr:
		passTransSet=filter_transcripts(bamfs.bamName,select_trans,transLengthDict,startCodonCoorDict,
		stopCodonCoorDict,bamfs.bamLen,bamfs.bamOffset,min_cds_counts,min_cds_codon,transcript_fasta,left_position,right_position,mode,table)
		select_trans_list.append(passTransSet)
	select_trans=reduce(set.intersection,select_trans_list) ## common transcripts among all samples which are all filtered.
	select_trans_out=pd.DataFrame(list(select_trans),columns=['transcript_id'])
	select_trans_out.to_csv(output_prefix+"_passed_transcripts.txt",index=0)
	print("Finish the transcripts filtering...",file=sys.stderr)
	print("The number of transcripts used for final pausing score calculaiton is : " + str(len(select_trans)),file=sys.stderr)
	for bamfs in bam_attr:
		pausing_score(bamfs.bamName,select_trans,transLengthDict,startCodonCoorDict,
		stopCodonCoorDict,bamfs.bamLen,bamfs.bamOffset,min_cds_counts,min_cds_codon,transcript_fasta,left_position,right_position,mode,bamfs.bamLegend,table,output_prefix)
	print("Finish the step of pausing score calculation",file=sys.stderr)


def main():
	parse_args_for_pausing_score_calculation()

if __name__ == "__main__":
	main()