# ADM_HW5

![graph](https://ieee-dataport.org/sites/default/files/network-1911678_1280.png)

In this assignment we perform an analysis of the Wikipedia Hyperlink graph. In particular, given extra information about the categories to which an article belongs to, we are curious to rank the articles according to some criteria.
For this purpose we use the Wikipedia graph released by the SNAP group.

This homework is divided in two research questions, the  **first research question** consists in building a graph , where V is the set of articles and E the hyperlinks among them, and provide its basic information:

-If it is direct or not

-The number of nodes

-The number of edges

-The average node degree. Is the graph dense?


In the **second research question**, given a category  as input we want to rank all of the nodes in V according to requested criteria and we obtain a block-ranking, where the blocks are represented by the categories. Then we sort the articles that are contained in the categories by a score.

Both the research questions are in the following HW5.ipynb file. Some of the cells in the notebook file aren't run. This is induced by our usage of a server to run some functions. Doing the calculation this way spared us leaving our computers over night or the computers being blockt by the calculation of e.g. the shortest path. The functions we used are contained in the functs.py file. 


## Group members: Ziba Khani, Hannes Engelhardt, Giulia Maslov  


