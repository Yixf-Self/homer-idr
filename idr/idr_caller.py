'''
Created on Aug 7, 2014

@author: karmel
'''
import itertools
import os
import subprocess

class IdrCaller(object):
    '''
    Dispatches prepped files to the IDR R package code.
    '''
    
    def compare_replicates(self, replicates, output_dir, 
                           ranking_measure='signal.value'):
        '''
        Do all pairwise comparisons for passed files.
        '''
        pairs = itertools.combinations_with_replacement(replicates,2)

        prefixes = []
        for file_1, file_2 in pairs:
            # Skip self-comparisons
            if file_1 == file_2: continue

            file_1_name = os.path.splitext(os.path.basename(file_1))[0]
            file_2_name = os.path.splitext(os.path.basename(file_2))[0]
            filename = '{}-{}'.format(file_1_name, file_2_name)
            output_prefix = os.path.join(output_dir, filename)
            self.run_batch_analysis(file_1, file_2, output_prefix, 
                                    ranking_measure=ranking_measure)
            prefixes.append(output_prefix)
        return prefixes
        
    def compare_pseudoreps(self, pseudoreps, output_dir,
                           ranking_measure='signal.value'):
        '''
        Compare each pseudoreplicate to its mate.
        
        Warning:: 
            Assumes files are named such that pseudoreps are paired
            and have names that differ only by the digit "1" or "2"
            such that sorting alphabetically will list mates one after
            the other.
        '''
        
        # Sort our sets of pseudoreps so that we can find pairs
        sorted_reps = sorted(pseudoreps)
        prefixes = []
        for file_1, file_2 in zip(sorted_reps[::2],sorted_reps[1::2]):
            file_1_name = os.path.splitext(os.path.basename(file_1))[0]
            filename = file_1_name + '-pair'
            output_prefix = os.path.join(output_dir, filename)
            self.run_batch_analysis(file_1, file_2, output_prefix, 
                                    ranking_measure=ranking_measure)
            prefixes.append(output_prefix)
            
        return prefixes
        
    def run_batch_analysis(self, file_1, file_2, output_prefix, 
                           ranking_measure='signalValue'):
        '''
        Rscript batch-consistency-analysis.r [peakfile1] [peakfile2] 
            [peak.half.width] [outfile.prefix] 
            [min.overlap.ratio] [is.broadpeak] [ranking.measure]
            
        '''
        # Make sure to cd into idrCode dir, as the r scripts call other scripts
        # assuming they are in the same directory.
        
        cmd = 'cd {}'.format(os.path.join(os.path.dirname(
                            os.path.realpath(__file__)), 'idrCode'))\
                    + ' && Rscript batch-consistency-analysis.r'\
                    + ' {} {} {} {} {} {} {}'.format(
                                file_1, file_2, -1,
                                output_prefix, 0, 'F', ranking_measure)
        print('Running command:')
        print(cmd)
        subprocess.check_call(cmd, shell=True)
        
    def plot_comparisons(self, comparison_files, output_dir, output_prefix):
        '''
        Given the output files generated by a pairwise 
        batch-consistency-analysis, plot the peaks.
        
        Rscript batch-consistency-plot.r [npairs] [output.prefix] 
            [input.file.prefix1] [input.file.prefix2] [input.file.prefix3] ...
        '''
        # Make sure to cd into idrCode dir, as the r scripts call other scripts
        # assuming they are in the same directory.
        cmd = 'cd {}'.format(os.path.join(os.path.dirname(
                            os.path.realpath(__file__)), 'idrCode'))\
                    + ' && Rscript batch-consistency-plot.r'\
                              + ' {} {} {}'.format(
                                len(comparison_files),
                                os.path.join(output_dir,output_prefix),
                                ' '.join(comparison_files))
        print('Running command:')
        print(cmd)
        subprocess.check_call(cmd, shell=True)
        
    