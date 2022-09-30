# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 11:46:34 2022

@author: elias
"""
from igraph import *
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap



def process_graph(sfile, UOfile):


    with open(UOfile) as nodesf:
        
        df1=pd.read_csv(UOfile)
        df1.index=df1['EquipmentID']
        
        #print(df1.head())
    
    with open(sfile) as edgesf:
        
        df=pd.read_csv(sfile)
        
        #print(df.head())
        
        edges=df['StreamIDs'].to_list()
        sources=df['Source'].to_list()
        targets=df['Target'].to_list()
        weights=df['Weight'].to_list()
        stype=df['Type'].to_list()
        sprice=df['Price'].to_list()

    pgraph=read_graph(sources, targets, weights)
    
    
    pgraph.es["Type"]=stype
    pgraph.es["Price"]=sprice
    pgraph.es["VOP"]=sprice
    pgraph.es["curved"] = False
    
    for node in pgraph.vs():

        node['Cost']=df1.loc[node['label'],'Annual_cost']
        node['Impact']=df1.loc[node['label'],'Annual_emissions']
        node['Type']=df1.loc[node['label'],'Type']

       
    pgraph_mod=get_modResultLeiden(sources, targets, weights)
    process_modularity=pgraph_mod.modularity
    process_modules=pgraph_mod.membership
    pgraph.vs['membership']=process_modules
    nmodules=max(process_modules)+1

    #print(process_modularity)
    #print(process_modules)
    
    colors = get_cmap('Set1')
    minw=min(weights)
    
    glayout = pgraph.layout("rt")
    visual_style = {}
    visual_style["vertex_size"] = 10
    visual_style["vertex_color"] = [colors(community) for community in pgraph.vs["membership"]]
    visual_style["vertex_label"] = pgraph.vs["name"]
    visual_style["edge_width"] = [((int(weights)-minw)*0.5/minw + 1) for weights in pgraph.es["weight"]]
    visual_style["edge_label"] = pgraph.es["weight"]
    visual_style["layout"] = glayout
    visual_style["bbox"] = (500, 500)
    visual_style["margin"] = 20
    
    plot(pgraph, **visual_style).show()
    
    headers=[]
    result=[]
    result.append(process_modularity)
    result.append(process_modules)
    f=open('modularity_results.csv', 'w', newline='')
    headers.append('Modularity')
    headers.append('Module memberships')
    write = csv.writer(f) 
    write.writerow(headers)
    
    write.writerow(result)
    
    return process_modularity, process_modules
    
def parse_string(x, max_len=100):
    out = 'NONE'
    try:
        out = str(x.encode('ascii'))[:max_len]
    except:
        pass
    return out

def read_graph(sources,targets,weights):
    edgelist = []
    names = UniqueIdGenerator()
    if type(sources) == int:
        sources=[sources];
    if type(targets) == int:
        targets=[targets];
    if type(weights) != list and type(weights) != str:
        weights=[weights];

    for n in range(len(sources)):
        n1=names[sources[n]]
        n2=names[targets[n]]
        edgelist.append((n1, n2))
        #print(edgelist)
    g = Graph(edgelist, directed=False)
    g.vs['name'] = [names.reverse_dict()[vid.index] for vid in g.vs]
    g.vs['label'] = [v for v in g.vs['name']]
    for m in range(len(weights)):
        w=weights[m]
        g.es[m]['weight']=float(w)
    return g


def runcomm_Leiden(gtest):
    z=gtest.community_leiden('modularity',gtest.es["weight"]);
    return z

def get_modResultLeiden(s,t,w):
    sources=s;
    targets=t;
    weights=w;
    gtest=read_graph(sources,targets,weights);
    gcomm=runcomm_Leiden(gtest);
    
    #if result=="modularity":
    #    modres=gcomm.modularity
    #else:
        #modres=gcomm.membership
    return gcomm