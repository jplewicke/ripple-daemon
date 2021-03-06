import networkx as nx
import math
from heapq import heappush, heappop
from collections import deque

def shortest_path_weight(G,v1,v2):
    return nx.floyd_warshall(G)[0][v1][v2]

def process_all_bids(bids):


    G = nx.DiGraph()
    #G.add_nodes_from(range(1,16))
    output = []
    for bid in bids:

        #nx.draw_shell(G)
        #plt.draw()
        bid = bid.split(',')
        output.extend(process_bid(G,bid))
    return output

def get_pred_path(G,v1,v2):
    pred = nx.floyd_warshall(G)[1]
    edges = deque([])
    u = v2
    while u != v1:
        edges.appendleft((pred[v1][u],u,G[pred[v1][u]][u]['e']))
        u = pred[v1][u]

    return edges

def find_min_capacity(edges):
    min_cap = float(1e3000)
    
    #If gain_adj is equal to 1.0, the most recent bid gets the very best price
    #available in the graph of offers.  This is also dependent on the ordering passed in
    #from get_pred_path and transact_bid.  If the surplus value in the transaction that's
    #found should get shared amongst the various offers, this should be uncommented.
    
    #gain = 1.0
    #for e in edges:
    #    gain = gain * e[2][1]['gain']
    #gain_adj = gain ** (1.0 / len(edges))
  
    gain_adj = 1.0
    gain = 1.0

    #We find the level of gain needed to turn the original commodity into
    #the each of the other commodities in this cycle, and find out which offer
    #has the most constrained capacity.
    
    for e in edges:
        min_cap = min(min_cap,e[2][1]['capacity'] * gain)
        gain = gain * e[2][1]['gain'] / gain_adj

    #Once we have the minimum capacity, we carry it through the transaction to
    #figure out how much of each offer to use.  Each offer's max capacity and
    #minimum exchange ratio should be satisfied by the values used.
    
    #The format used here to pass the values around is a bit wonky.  It should
    #eventually be a Transaction object with keys referencing the datastore Offers
    #that make up the transaction.
    
    #I think the nontrans variable is just in there from old debugging, but am not sure.
    
    gain = 1.0
    transaction = deque([])
    nontrans = deque([])
    for e in edges:
        new_cap = min_cap / gain
        e[2][1]['capacity'] -= new_cap
        transaction.append((e[0],e[1],new_cap,e[2][1]['info']))
        nontrans.append((e[0],e[1],new_cap,e[2][1]['capacity'],e[2][1]['info']))
        gain = gain * e[2][1]['gain'] / gain_adj

    #print list(nontrans)

    return transaction

def transaction_announce(transaction):
    
    #Old output code.  Slightly fragile, should hopefully go away.
    output = []
    last_e = transaction[-1]
    for e in transaction:
        output.append("%s gives %0.3f %s to %s." % (e[3], e[2], e[0], last_e[3]))
        last_e = e
    return output

def bid_announce(edge,n1,n2,type):    
    #Old output code.  Slightly fragile, should hopefully go away.
    info = edge[1]['info']

    if len(info.split('|')) == 2:
        s = "%s has a %s bid" % (info.split('|')[1], type)
    else:
        s = "%s %s" % (type, info)


    return ['%s: %0.2f %s for at least %7.3f %s per %s' % (s, edge[1]['capacity'],
            n1, 1 / edge[1]['gain'], n2, n1)]


def transact_bid(G,n1,n2,edge):

    #print "Path from %s to %s to %s" % (n1, n2, n1)
    output = []
    edges = get_pred_path(G,n2,n1)
    edges.append((n1,n2,edge))


    transaction = find_min_capacity(edges)
    output.extend(transaction_announce(transaction))

    #Perform necessary cleanup.  Sometimes the capacity of an offer is completely
    #exhausted in the course of finding a transaction, and we have to take the proper
    #steps to return the offer graph to the proper state.
    
    for e in edges:
        if e[2][1]['capacity'] == 0:
            if e[2] == edge:
                #We won't continue adding it.
                pass
            else:
                #remove from graph

                if G[e[0]][e[1]]['q'] != []:
                    #Other edges remain in edge queue.

                    new_e = heappop(G[e[0]][e[1]]['q'])

                    G[e[0]][e[1]]['e'] = new_e

                    G[e[0]][e[1]]['weight'] = new_e[0]

                else:
                    #Delete this edge completely.
                    G.remove_edge(e[0], e[1])
                
    return output

def process_bid(G,bid):
    output = []
    info = bid[0]
    n1 = bid[2]
    n2 = bid[3]
    capacity = float(bid[4])
    gain = 1.0 / float(bid[5])
    weight= -1.0 * math.log10(gain)

    edge = (weight,{'capacity': capacity, 'gain': gain,'info': info})

    #Make sure nodes(commodities) already exist.
    G.add_node(n1)
    G.add_node(n2)

    #See whether this edge is already in the graph.
    #If it is, we only add this bid as an edge if it has
    #lower weight than the current edge.

    if G.has_edge(n1,n2):

        if G[n1][n2]['weight'] < weight:
            #Add it to the edge queue.
            output.extend(bid_announce(edge,n1,n2,'low'))
            heappush(G[n1][n2]['q'],edge)

            #print 'edge queue insert %f' % weight
        else:
            while ((shortest_path_weight(G,n2,n1) + weight < 0.0)
                    and (edge[1]['capacity'] > 0.0)):

                output.extend(bid_announce(edge,n1,n2,'high winning'))
                output.extend(transact_bid(G,n1,n2,edge))

            if edge[1]['capacity'] > 0.0:

                #Move the current edge to the edge queue and make this
                #the current edge.
                former_weight = G[n1][n2]['weight']

                heappush(G[n1][n2]['q'],G[n1][n2]['e'])
                G[n1][n2]['e'] = edge
                G[n1][n2]['weight'] = weight

                output.extend(bid_announce(edge,n1,n2,'high'))
    else:
        while not G.has_edge(n1,n2) and edge[1]['capacity'] > 0.0:
            if shortest_path_weight(G,n2,n1) + weight > 0.0:

                #Go ahead and add the edge.
                output.extend(bid_announce(edge,n1,n2,'new'))
                G.add_edge(n1,n2,weight=weight,e=edge,q=[])
            else:
                output.extend(bid_announce(edge,n1,n2,'new winning'))
                output.extend(transact_bid(G,n1,n2,edge))
    return output

if __name__ == "__main__": process_all_bids(sys.stdin.readlines())
#nx.draw_shell(G)
#time.sleep(8)