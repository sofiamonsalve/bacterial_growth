import re
from prettytable import PrettyTable
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.legend import Legend

import db_functions as db
from user_inputs import *
from utils import getMatchingList, getIntersectionColumns, getMeanStd

abundance_options = ['od', 'counts', 'qpcr', 'rnaseq']
od_regex = re.compile(r'.*time.* | .*OD.*', flags=re.I | re.X)
counts_regex = re.compile(r'.*time.* | .*count.*', flags=re.I | re.X)
qpcr_regex = re.compile(r'.*time.* | .*qpcr.*', flags=re.I | re.X)
rnaseq_regex = re.compile(r'.*time.* | .*rna.*', flags=re.I | re.X)

def plot(option):
    '''
    This function takes the user plot choice, makes the user choose the data to plot (form the args dictionary) and call the corresponding functions
    '''
    fields = ['abundance', 'metabolites', 'ph']
    if option == '1':
        # Only one replicate
        # --------------------------------------------------------------------------------------------------------
        study_id = chooseStudy()
        experiment_id = chooseExperiment(study_id)
        perturbation_id = choosePerturbation(experiment_id)
        replicate_id = chooseReplicate(experiment_id=experiment_id, perturbation_id=perturbation_id)

        args = {'replicateId': replicate_id}
        
    
    if option == '2':
        # Several replicates from same perturbation
        # --------------------------------------------------------------------------------------------------------
        study_id = chooseStudy()
        experiment_id = chooseExperiment(study_id)
        perturbation_id = choosePerturbation(experiment_id)

        args = {'perturbationId': perturbation_id}

    
    if option == '3':
        # Several replicates from same experiment and different perturbations
        # --------------------------------------------------------------------------------------------------------
        study_id = chooseStudy()
        experiment_id = chooseExperiment(study_id)

        args = {'experimentId': experiment_id}
        
    
    if 'abundance' in fields:
        files = db.getFiles('abundanceFile', args)
        plotAbundances(files, args)
    
    if 'metabolites' in fields:
        files = db.getFiles('metabolitesFile', args)
        plotMetabolites(files, args)

    if 'ph' in fields:
        files = db.getFiles('phFile', args)
        plotPh(files, args)
    

def plotAbundances(files, args):
    '''
    Plot abundances.
    As there are different measurements, it plots them separately
    '''
    if len(files) == 1:
        for opt in abundance_options:
            regex = globals()['%s_regex' % opt]
            plot = plotOneReplicate(files, regex)
            
    elif len(files) > 1:
        for opt in abundance_options:
            regex = globals()['%s_regex' % opt]
            plotExperimentPerturbation(args, regex, 'abundanceFile')
                
    
def plotMetabolites(files, args):
    '''
    Plot metabolites
    '''
    if len(files) == 1:
        plotOneReplicate(files, '')
            
    elif len(files) > 1:
        plotExperimentPerturbation(args, '', 'metabolitesFile')
    
    
def plotPh(files, args):
    '''
    Plot ph
    '''
    if len(files) == 1:
        plotOneReplicate(files, '')
            
    elif len(files) > 1:
        plotExperimentPerturbation(args, '', 'phFile')


def plotExperimentPerturbation(args, regex='', db_field=''):
    '''
    Plot if there are several replicates
    Analyzes the data. It can be only from experiment, only from perturbations, or both
    '''
    
    label_ids = []
    
    if 'experimentId' in args:
        exp_with_null = db.countRecords('TechnicalReplicate', {'experimentId': args['experimentId']})[0][0]
        exp_without_null = db.countRecords('TechnicalReplicate', {'experimentId': args['experimentId'], 'perturbationId': 'null'})[0][0]
    else:
        exp_with_null = 0
        exp_without_null = 0
    
    if exp_with_null != exp_without_null and exp_with_null > 0 and exp_without_null > 0:
        perturbation_ids = db.getRecords('Perturbation', 'perturbationId', args)
        
        cnt = 0
        # Plot: ==================================================================================================================
        fig = plt.figure()
        ax = fig.add_subplot()
        
        # Experiment data
        args2 = args.copy()
        args2['perturbationId'] = 'null'
        files = db.getFiles(db_field, args2)
        plot, vec = plotSetReplicates(files, regex, ax, cnt)
        cnt = cnt + 1
        label = 'Experiment id ' + args['experimentId']
        label_ids.append(label)
        
         # Perturbation data
        for perturbation_id in perturbation_ids:
            files = db.getFiles(db_field, {'perturbationId': perturbation_id[0]})
            plot, vec = plotSetReplicates(files, regex, ax, cnt)
            cnt = cnt + 1
            label = 'Perturbation id ' + perturbation_id[0]
            label_ids.append(label)
            
        # Legend: =========================================================
        if plot != None:
            handles, labels = ax.get_legend_handles_labels()
            legend1 = ax.legend(labels[0:len([*vec])], loc='upper right')
            legend2 = getExperimentLegend(ax, handles, label_ids, vec)
            ax.add_artist(legend2)
        # =================================================================
        
        ax.set_xlabel('time')
        ax.set_ylabel(db_field[:-4])
        plt.show()
        # ========================================================================================================================
        
    else:
        perturbation_ids = db.getRecords('Perturbation', 'perturbationId', args)
        
        if len(perturbation_ids) == 0:
            files = db.getFiles(db_field, args)
            
            cnt = 0
            # Plot: ==================================================================================================================
            fig = plt.figure()
            ax = fig.add_subplot()
            
            # Experiment data
            plot, vec = plotSetReplicates(files, regex, ax, cnt)
            cnt = cnt + 1
            label = 'Experiment id ' + args['experimentId']
            label_ids.append(label)
            
            # Legend: =========================================================
            if plot != None:
                handles, labels = ax.get_legend_handles_labels()
                legend1 = ax.legend(labels[0:len([*vec])], loc='upper right')
                legend2 = getExperimentLegend(ax, handles, label_ids, vec)
                ax.add_artist(legend2)
            # =================================================================
            
            ax.set_xlabel('time')
            ax.set_ylabel(db_field[:-4])
            plt.show()
            # ========================================================================================================================
            
        else:
            cnt = 0
            # Plot: ==================================================================================================================
            fig = plt.figure()
            ax = fig.add_subplot()
            
            # Perturbation data
            for perturbation_id in perturbation_ids:
                files = db.getFiles(db_field, {'perturbationId': perturbation_id[0]})
                plot, vec = plotSetReplicates(files, regex, ax, cnt)
                cnt = cnt + 1
                label = 'Perturbation id ' + perturbation_id[0]
                label_ids.append(label)
            
            # Legend: =========================================================
            if plot != None:
                handles, labels = ax.get_legend_handles_labels()
                legend1 = ax.legend(labels[0:len([*vec])], loc='upper right')
                legend2 = getExperimentLegend(ax, handles, label_ids, vec)
                ax.add_artist(legend2)
            # =================================================================
            
            ax.set_xlabel('time')
            ax.set_ylabel(db_field[:-4])
            plt.show()
            # ========================================================================================================================

def plotOneReplicate(files, regex='', db_field=''):
    df = pd.read_csv(files[0][0], sep=" ")
    
    if regex != '': headers = getMatchingList(regex, df)
    else: headers = df.columns
    
    data = getIntersectionColumns(df, headers)
            
    # plot
    fig = plt.figure()
    ax = fig.add_subplot()
    if len(data.columns)>1: 
        plot, vec = plotDf(data, ax)
    else: 
        plot = plt.close()
        vec = range(0,0,1)
    
    # Legend: =========================================================
    if plot != None:
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(labels, loc='upper right')
    # =================================================================
    
    ax.set_xlabel('time')
    ax.set_ylabel(db_field[:-4])
    plt.show()
    
    return plot, vec

def plotSetReplicates(files, regex, ax, count):
    data = getMeanStd(files, regex)
        
    if len(data.columns)>1: 
        plot, vec = plotDf(data, ax, count)
    else: 
        plot = plt.close()
        vec = range(0,0,1)
    
    return plot, vec

def plotDf(df, ax, style_count=0):
    cmap = plt.get_cmap(name='tab10')
    styles = ['-', '--', '-.', ':', '-x', '-o', '-<', '->']
    
    msd_regex = re.compile(r'.*mean.* | .*std.*', flags=re.I | re.X)
    
    if len(getMatchingList(msd_regex, df)) > 0:
        vec = range(1,len(df.columns),2)
        for i in vec:
            plot = ax.errorbar(df.iloc[:,0], df.iloc[:,i], yerr = df.iloc[:,i+1], fmt=styles[style_count], color = cmap(i-1), label=df.columns[i][:-5])
            #plot.set_linestyle(styles[style_count])
    else:
        vec = range(1,len(df.columns))
        for i in vec:
            plot = ax.plot(df.iloc[:,0], df.iloc[:,i], linestyle=styles[style_count], color = cmap(i-1), label=df.columns[i])
    return plot, vec


def getExperimentLegend(ax, handles, labels, vec):
    vec1 = [*range(0,len(labels))]
    vec2 = [x * len(vec) for x in vec1]
    new_handles = [handles[i] for i in vec2]
    leg = Legend(ax, new_handles, labels, frameon=False, bbox_to_anchor=(1.04, 1), loc='lower right')
    return leg