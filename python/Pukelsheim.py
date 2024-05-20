import copy
from transpose_dict import TD
import csv
import os
import numpy as np

debug = True

def importCSV(ff):
    """
    import a csv an return seats and votes
    """
    if not os.path.exists(ff):
        print("Cannot find {0}".format(ff))
        exit()

    Constituencies = []
    Seats = {}
    Votes = {}
    
    with open(ff) as fcsv:
        rfcsv = csv.reader(fcsv)
        for row in fcsv:
            rr = row.split(',')
            if debug: print(rr)            
            if not Constituencies: Constituencies =  [ r.replace('\n','') for r in rr[1:] ]
            elif not Seats:
                for i in range(len(Constituencies)): Seats[ Constituencies[i] ] = int(rr[i+1])
            else:
                Votes[ rr[0] ] = {}
                for i in range(len(Constituencies)):
                    Votes[ rr[0] ][ Constituencies[i] ] = float( rr[i+1] )
    fcsv.close()
    if debug: print("Votes: {0},\n Seats: {1}".format(Votes,Seats))
                                                                 
    return Seats, Votes    

#########################################################################################################
def wikipediaExample():
    """
    from https://de.wikipedia.org/wiki/Doppeltproportionales_Zuteilungsverfahren
    """
    ff = "wikipedia/wiki_de.csv"
    return importCSV(ff)

#########################################################################################################
def webster():
    """
    Following SainteLaguë/Webster
    """
    
#########################################################################################################
def hagenbach(Seats, Votes):
    """
    Distribution in a single constituency following Hagenbach-Bischoff
    """
    if debug: print("Entring Hagenbach with {0} seats and {1} votes".format(Seats,Votes))
    nSeat = 0
    SeatsPerParty = {}
    Quotient = {}
    divisor = sum(list(Votes.values()))/(Seats+1.)
    
    # 1st round
    for p,s in Votes.items():
        Seat_1 = int(s/divisor)
        SeatsPerParty[p] = Seat_1
        Quotient[p] = s/(Seat_1+1)    # weight

    nSeat = sum( list(SeatsPerParty.values()))
    if debug: print("Hagenbach: After 1st distribution {0}/{1} seats attributed: {2}".format(nSeat,Seats,SeatsPerParty))
    if debug: print("Hagenbach:          Quotient: {0}".format(Quotient))
    
    while nSeat<Seats:
        p = max(Quotient, key=Quotient.get)
        SeatsPerParty[p]+=1
        Quotient[p] = Votes[p]/(SeatsPerParty[p]+1)
        # print("Updated {0} to {1}, Q={2}".format(p, SeatsPerParty[p],Quotient[p]))
        nSeat+=1

    if debug: print("Hagenbach: After 2nd dsitribution {0}/{1} seats attributed: {2}".format(nSeat,Seats,SeatsPerParty))

    return SeatsPerParty, divisor

#########################################################################################################
def hagenbach_overall(Seats, Votes):
    """
    Distribution in all constituencies following Hagenbach-Bischoff
    """
    TotalSeatsPerParty = {}
    R_Votes = TD(Votes,1)  # transpose
    for k in Seats.keys():
        SeatsPerParty,d = hagenbach(Seats[k], R_Votes[k])
        if debug: print("In {0} the parties have votes {1}".format(k, R_Votes[k]))
        if debug: print("    The attribution is {0}".format(SeatsPerParty))
        for p in SeatsPerParty.keys(): # loop over parties
            if p not in TotalSeatsPerParty.keys() :TotalSeatsPerParty[p] = SeatsPerParty[p]
            else: TotalSeatsPerParty[p] = TotalSeatsPerParty[p]+SeatsPerParty[p]

    return TotalSeatsPerParty

#########################################################################################################
def pukelsheim_step1(Seats, R_Votes, TotalSeatsPerParty):
    """
    First step of iterative procedure following Pukelsheim
    """
    if debug : print("Pukelsheim 1st: {0}, {1}, {2}".format(Seats, R_Votes, TotalSeatsPerParty))
    #
    # Loop over constituencies
    #
    for c,v in R_Votes.items():   # c is a constituency
        divided,divisor = hagenbach(Seats[c],v)   # get seats repartition by hagenbach
        if debug : print("Pukelsheim 1st: In {0} divisor is {1:.1f} and divided {2}".format(c,divisor,divided))

#########################################################################################################
def pukelsheim_step3(Seats, R_Votes, TotalSeatsPerParty):
    """
    @ NOT YET RUN

    Third step of iterative procedure following Pukelsheim. 
    That's when Hagenbach no longer works
    """
    if debug : print("Pukelsheim 3rd: {0}, {1}, {2}".format(Seats, R_Votes, TotalSeatsPerParty))
    #
    # Loop over constituencies
    #
    for c,v in R_Votes.items():   # c is a constituency
        noff = 1
        sumS = 0
        while sumS!=Seats[c]:
            divisor = sum(list(v.values()))/(Seats[c]+noff) # why not a straight hagenbach in 1st step?
            sumS = sum( [ int(d) for d in divided] )
            if debug : print("Pukelsheim 3rd: In {0} divisor is {1:.1f} and divided {2} -> total {3} of {4}".format(c,divisor,[float("{0:.1f}".format(d)) for d in divided],sumS,Seats[c]))
            # if my guess is bad, randomly try other guesses. I could use the Newton method.
            if sumS<Seats[c]:
                if 1==noff: noff=0.
                else: noff = Seats[c]*np.random.uniform()
            elif sumS>Seats[c]:
                noff = -Seats[c]*np.random.uniform()           
    
    
#########################################################################################################
def pukelsheim(Seats, Votes, TotalSeatsPerParty):
    """
    Iterative procedure following Pukelsheim
    """
    R_Votes = TD(Votes,1)  # transpose
    if debug : print("Pukelsheim: The seats per constituency are {0}".format(Seats))
    if debug : print("Pukelsheim: The seats per party are        {0}".format(TotalSeatsPerParty))
    if debug : print("Pukelsheim: The votes are                  {0}".format(R_Votes))

    # I'll need to split that in multiple methods
    # step1
    RealSeats = pukelsheim_step1(Seats, R_Votes, TotalSeatsPerParty)
        
    
#####################################################################
"""
Test wikipedia example
"""
Seats, Votes = wikipediaExample()
if debug: print("Example: Votes {0}".format(Votes))
if debug: print("Example: Seats {0}".format(Seats))

# Hagenbach
TotalSeatsPerParty_HAG = hagenbach_overall(Seats, Votes)
print("The attribution following Hagenbach  is {0}".format(TotalSeatsPerParty_HAG))

# Pukelsheim
SumOfVotes = {}
for k in Votes.keys():
    SumOfVotes[k] = sum(list(Votes[k].values()))
# first distribute over all parties
TotalSeatsPerParty_PUK,d = hagenbach(sum(list(Seats.values())), SumOfVotes)
print("The attribution following Pukelsheim is {0}".format(TotalSeatsPerParty_PUK))

pukelsheim(Seats, Votes, TotalSeatsPerParty_PUK)
