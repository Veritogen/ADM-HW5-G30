
import numpy as np
import pandas as pd
import math
import networkx as nx
import csv
from statistics import median, mean
import queue as Q
import threading
from numba import autojit





# function to open dicts we saved
def open_dict(vocabularyFile):
        cats = open(vocabularyFile, 'r', encoding = "utf8").readlines()
        cats2 = {}
        for cat in cats:    
            templ = []
            for x in cat.split():
                    templ.append(x.strip("[").strip("]").strip("'").strip(",").rstrip("''").rstrip('\n'))
            try:
                int(templ[1])                
                cats2[templ[0]] = templ[1:]
            except:
                cats2[templ[0]] = " ".join(templ[1:])
        return cats2

# function to save our vocabulary file to disk        
def save_dict(vocabulary,fileName="output.csv"):
    with open(fileName,'wb') as vfile:
        for i in vocabulary.keys():
            vfile.write(str(i).encode())
            vfile.write(str('\t').encode())
            vfile.write(str(vocabulary[i]).encode())
            vfile.write('\n'.encode())
        vfile.close()



# function to look for the shortest path
def bfs(graph, inp_cat, inp_node, dest_cat, out_q):
    # creating a queue
    queue = Q.Queue()    
    #putting the current node in the queue
    queue.put([inp_node, 0])    
    # defining a dictionary to check if we already visited the nodes of graph 
    visited = {}    
    # setting the distance of the current node to infinity as a default
    sh_path = np.inf    
    # setting visited to False for every node in the graph
    for x in graph.nodes:
        visited[x] = False        
    # check for shortest paths as long as the queue is not empty
    while queue.empty() != True:        
        # get the node we put in first 
        current = queue.get()        
        # check if the entry we got from the queue is in the destinatino category and not in the input category
        if graph.node[current[0]][dest_cat] == True and graph.node[current[0]][inp_cat] != True:
            # if its true, set visited #uneccessary step as well break after anyway
            visited[current[0]]= True
            # update the shortest path if we found one, else will stay infinitive
            sh_path = current[1]
            #print('shortest path from ', inp_node, ' to ', current[0], ' found (dist = ', current[1], ')')
            queue.queue.clear()
        else:
            # get the successors of our current node (as its a directed graph)
            for i in graph.successors(current[0]):
                # check if the successor is not visited
                if visited[i] != True:
                    # if its not visited, put the found node in the queue, 
                    # together with the information about the distance it has from the starting node                                    
                    queue.put([i, current[1]+1])
            # set the current node to visited
            visited[current[0]]= True 
    # put the result we found 
    out_q.put([inp_node, sh_path])
    
# function to execute the bfs
def run_bfs(start_cat, graph, categories):
    #creating a list of nodes of our starting category 
    inp_nodes = [cat_nodes for cat_nodes in graph.nodes if graph.node[cat_nodes][start_cat]== True]
    # create a dictionary we want to save the medians and other information to
    medians = {}
    #iterate over all categories in the list of categories
    for cat in categories:
        # creating a dictionary we save the information for every node the bfs returnd
        sh_paths = {}
        # iterate only over the categories that aren't our C0
        if cat != start_cat:
            # setting the destination category to be passed to our bfs
            dest_cat = cat
            # creating a queue that contains the nodes we want to pass to the bfs
            start_q = Q.Queue()
            # creating a queue that we'll pass the results of our bfs to
            out_q = Q.Queue()
            # adding the nodes of our C0 to the start_q. every node will be passed to our bfs
            for start_node in inp_nodes:
                start_q.put(start_node)
            # while we didn't calculate the shortest distance for every node in our C0, do things    
            while not start_q.empty(): 
                # as long as the number of running threads is at most 50, add threads
                if threading.active_count() <= 50:
                    # get the current node from our start_q
                    current_t = start_q.get()
                    # start a thread with our bfs and the aforementioned parameters
                    t = threading.Thread(target=bfs, args=(graph, start_cat, current_t, dest_cat, out_q), daemon= True).start()
                    # tell the start_q that the task with current_t is done
                    start_q.task_done()
            # while we didn't retrieve all values the bfs calculated, keep running
            while not out_q.empty():
                # get the first result in the queue
                out_p = out_q.get()
                # add the information to our shortest paths dictionary. the key is the node, the value the distance
                sh_paths[out_p[0]] = out_p[1]
                # tell the out_q that the job is finished
                out_q.task_done()
            # tell the start_q that all threads shall be joined
            start_q.join()
            # setting up variables for the calculation of avererage and counting the infitives in our result
            sum_vals = 0
            i = 0
            inf_count = 0
            # iterate over the values we retrieved for the distances from c0 to ci in order to sum the values and count the infinitives
            for x in sh_paths.values():
                if x != np.inf:
                    i+=1
                    sum_vals += x  
                else:
                    inf_count += 1
            # saving median, mean and infinity count as values in a dictionary. The key is the category to which we calculated the distance from c0
            medians[cat] = [median(sh_paths.values()), sum_vals/i, inf_count]
    return medians
    
'''
Functions for scoring:
'''
#function to assign every node only to one category
#@autojit
def key_substraction(cat_dict, org_cat, list_smallest):
    return_dict = {}
    # Get a list of categorys, sorted by the ascending distance from our C0
    # (doesn't include our starting category so we don't have to iterate over it
    keys = []
    for key in list_smallest:
        keys.append(key[0])
    # iterating over the categories in a list we sorted by the ascending distance from our C0
    for i in range(len(keys)):
        if i == 0:
            # getting the nodes of our starting category
            org_nodes = cat_dict[org_cat]
            # iterating over all categories in our list of sorted categories
            for key in keys:
                # assigning only the values of the current key minus the intersection 
                # of the values of the current category and our starting category
                temp = []
                for node in cat_dict[key]:
                    if node not in org_nodes:
                        temp.append(node)
                return_dict[key] = temp
        else:
            # iterating over all categories again. but now we're only using the keys of the categories we didn't 
            # clean up yet. Same as before we're only assigning the values of Ci to Cn minus the intersection Ci-1 and Ci.
            for x in range(i,len(keys)):
                temp = []
                for node in cat_dict[keys[x]]:
                    if node not in cat_dict[keys[i-1]]:
                        temp.append(node)
                return_dict[keys[x]] = temp
    return return_dict

#function to create the score for a node by the in edges
def no_in_edges(node, cat):
    x = 0
    # getting the number of in edges by counting all predecessors 
    # (nodes with edges pointing towards the node we're looking at) of a node.
    for i in graph.predecessors(node):
        # 
        if graph.node[i][cat] == True:
            x +=1
    return x

#create the score for every node in a category
def article_score_cat(graph, cat):
    #get all the nodes of the current category in a defined graph
    nodes = [nodes for nodes in graph.nodes if graph.node[nodes][cat]== True]
    for node in nodes:
        # set the score to the existing score (in the beginning 0) + the number of in edges of the current node
        graph.node[node]['score'] = graph.node[node]['score'] + no_in_edges(node, cat)
    
def article_score(graph, cat_list):
    for i in range(len(cat_list)):
        if i == 0:
            nodes = [nodes for nodes in graph.nodes if graph.node[nodes][cat_list[i]]== True]
            sub_g = graph.subgraph(nodes)
            article_score_cat(sub_g, cat_list[i])
        else:
            cat_nodes = [nodes for nodes in graph.nodes if graph.node[nodes][cat_list[i]]== True]
            # sub_g_cat = graph.subgraph(cat_nodes)
            # article_score_cat(sub_g_cat, cat_list[i])
            for node in cat_nodes:
                nodes.append(node)
            sub_g = graph.subgraph(nodes)
            article_score_cat(sub_g, cat_list[i])
            for node in cat_nodes:
                for pred in sub_g.predecessors(node):
                    if graph.node[pred][cat_list[i-1]] == True:
                        graph.node[node]['score'] = graph.node[node]['score'] + graph.node[pred]['score']
    return sub_g

