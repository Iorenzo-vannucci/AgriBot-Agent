import sys
import os
# Aggiunge la cartella aima al path (assumendo che sia nella stessa directory dello script)
sys.path.append(os.path.abspath("aima"))
import numpy as np
import time
from search import Problem, astar_search, uniform_cost_search,Node
from cropping import crop

MAGENTA = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
NORMAL = '\033[0m'

class AgriBotProblem(Problem):
    move_cost=1
    cut_cost=1
    water_cost=1
    spray_cost=3
    refill_cost=1
    def __init__(self, grid, max_water=3,max_energy=30):
        self.grid = grid 
        self.n=len(grid)
        self.max_water=max_water
        #self.max_energy=max_energy
        
        
        self.start_position= None
        self.finish_position= None
        
        #weeds = set()
        dry = set()
        self.rocks = set() #per memorizzare la posizione delle rocce uso un set per evitare duplicati
        self.station = set() #per memorizzare la posizione della stazione uso un set per evitare duplicati
        #pests= set()

        for i in range(self.n):
            for j in range(self.n):
                cell=grid[i][j]
                index = i*self.n+j   ##tipo (0,0) di una matrice 3*3 --> 0*3+0=0, (0,1) --> 0*3+1=1 ecc...
                if cell=="R":
                    self.rocks.add(index)
                elif cell=="S":
                    self.start_position=index
                elif cell=="F":
                    self.finish_position=index
                #elif cell == "W": #come memorizzare quando ho un erba infestante da tagliare, 
                    #weeds.add(index)  
                elif cell == "D":
                    dry.add(index)
                #elif cell == "P":
                    #pests.add(index)
                elif cell == "T":
                    self.station.add(index)
        initial= (self.start_position,self.max_water,frozenset(dry))#ho usato i set, invece che usare una griglia intera quindi
        #initial= (self.start_position,self.max_water,self.max_energy,frozenset(weeds),frozenset(dry),frozenset(pests),)#ho usato i set, invece che usare una griglia intera quindi
        #devo usare frozenset per rendere il set hasable sennò non poso usarlo su state di AIMA 
        super().__init__(initial=initial, goal=None)

    def actions(self, state):
        position, water, dry = state
        #position, water, energy, weeds, dry, pests = state
        r= position // self.n #riga
        c= position % self.n #colonna

        possible_action = [] 
     
        #if energy>=self.move_cost: non controllo energia
        
        #--- AZIONI MOVIMENTO ---#
        #muoversi in su 
        if r >0:
            up_index = (r-1)*self.n+c 
            if up_index not in self.rocks:
                possible_action.append("UP")
        #muoversi in giù 
        if r < self.n - 1:
            down_index = (r+1)*self.n+c 
            if down_index not in self.rocks:
                possible_action.append("DOWN")
        #muoversi a destra 
        if c < self.n - 1:
            right_index = (r)*self.n+(c+1)
            if right_index not in self.rocks:
                possible_action.append("RIGHT")
        #muoversi a sinista
        if c > 0:
            left_index = (r)*self.n+(c-1)
            if left_index not in self.rocks:
                possible_action.append("LEFT")
        
        #if position in weeds and energy>self.cut_cost:
            #possible_action.append("CUT")
        if position in dry and water>0:
            possible_action.append("WATER")
        #if position in pests and energy>=self.spray_cost:
            #possible_action.append("SPRAY")

        if position in self.station and water < self.max_water: #se il serbatoio o l'energia non sono al max ha senso permettergli un refill 
            possible_action.append("REFILL")
        return possible_action

        
    def result(self, state, action):
        position, water, dry = state
        #position, water, energy, weeds, dry, pests = state
        delta = {'UP': -self.n, 'DOWN': self.n, 'LEFT': -1, 'RIGHT': 1}
        #if action == "CUT": 
        #    new_weeds=weeds.difference({position})
        #    new_energy=energy-self.cut_cost
        #    return (position, water, new_energy, new_weeds, dry, pests)
       
        if action == "WATER":
            new_dry=dry.difference({position})
            new_water=water-1
            #new_energy=energy-self.water_cost
            return (position, new_water, new_dry)
       
        #if action == "SPRAY":
        #    new_pests=pests.difference({position})
        #    new_energy=energy-self.spray_cost
        #    return (position, water, new_energy, weeds, dry, new_pests)
       
        if action == "REFILL": 
            #new_energy=energy-self.refill_cost
            return (position, self.max_water, dry)

        new_position= position + delta[action]
        #new_energy= energy - self.move_cost
        return (new_position,water,dry)
        

    def goal_test(self, state):
        position, water, dry = state
        if (len(dry)==0) and position == self.finish_position:
            return True
        else:
            return False
    
    
    def rc(self,index):
            return index // self.n, index % self.n 
        
    def cal_manhattan(self,A,B):
        A_r, A_c = self.rc(A)
        B_r,B_c= self.rc(B)
        return abs(A_r - B_r)+abs(A_c-B_c)
#euristica 
    def h_manhattan(self,node):
       
        
        position, water, dry = node.state
        #se ho finito le dry 
        if len(dry)==0:
            return self.cal_manhattan(position,self.finish_position)
        if len(dry)>0 and water>0:
            dry_dist=[]
            for index in dry:
                dry_dist.append(self.cal_manhattan(position,index))
            return min(dry_dist)
        if len(dry)>0 and water==0:
            station_dist=[]
            for index in self.station:
                station_dist.append(self.cal_manhattan(position,index))
            return min(station_dist)
        


    def h_max_pairwaise_Distance(self,node):
        position, water, dry = node.state
        if len(dry)==0:
            return self.cal_manhattan(position,self.finish_position)
        max_internal_distance = 0
        dry_list=list(dry) #ho convertito il set in una lista in modo tale da usare gli indici e calcolare ogni coppia una volta sola. 
        for i in range(len(dry_list)):
            for j in range(i + 1, len(dry_list)):
                dist = self.cal_manhattan(dry_list[i], dry_list[j])
                if dist > max_internal_distance:
                    max_internal_distance = dist
        if(water==0):
            station_dist=[]
            for index in self.station:
                station_dist.append(self.cal_manhattan(position,index))
            return min(station_dist)+max_internal_distance
        
        if len(dry)>0 and water>0:
            dry_dist=[]
            for index in dry:
                dry_dist.append(self.cal_manhattan(position,index))
            most_close_plants=min(dry_dist)
            return max_internal_distance+most_close_plants


model = tf.keras.models.load_model("agribot_model.keras")
cell = crop("agribot_map_L1.png", 20, 20)
for i in cell:
    normalized_cell = i[2]//255
    shape = normalized_cell.shape
    normalized_cell = normalized_cell.reshape(1 ,28 , 28, 1)
    prediction = model.predict(normalized_cell)
    idx=np.argmax(prediction)
    result=['D', 'F', 'R', 'S', 'T', '.'][idx]
grid_map= []



# Creazione del problema

def print_grid(problem, state, action=None):
    position, water, dry = state
    n = problem.n
    
    print(f"\n--- Azione Eseguita: {action} ---")
    print(f"Stato: Acqua [{water}/{problem.max_water}] | Piante residue: {len(dry)}")

    for r in range(n):
        row_str = ""
        for c in range(n):
            idx = r * n + c
            char = "."
            
            # Logica di assegnazione simboli
            if idx == position:
                char = YELLOW + " B " +NORMAL # Robot
            elif idx in dry:
                char = GREEN+ " D " +NORMAL      # Pianta Secca
            elif idx in problem.rocks:
                char = RED+ " R " +NORMAL     # Roccia
            elif idx in problem.station:
                char = BLUE + " T " + NORMAL    # Stazione
            elif idx == problem.finish_position:
                char = " F "    # Fine
            elif idx == problem.start_position:
                char = MAGENTA+ " S " + NORMAL
            else:
                char = " . "
            #time.sleep(3)
            row_str += char
            #print (row_str)
        print(row_str)
    print("-" * (n * 3))

            
from search import InstrumentedProblem

problem = AgriBotProblem(grid_map, max_water=2)
def ucs(): 
    problem_per_ucs = InstrumentedProblem(problem) 
    print("Avvio ricerca UCS")
    solution_node = uniform_cost_search(problem_per_ucs)

    if solution_node:
        #statistiche
        print(f"Nodi esplorati da UCS: {problem_per_ucs.states}")
        print(f"Goal test effettuati: {problem_per_ucs.goal_tests}")
        print(f"Costo: {solution_node.path_cost}")
        print(f"passi: ({len(solution_node.solution())}):")
        print(solution_node.solution())
    else:
        print("Nessuna soluzione trovata.")

def a_star():
    problem_per_astar = InstrumentedProblem(problem)
    print("Avvio ricerca A* con euristica max_pairwaise_Distance...")
    solution_node = astar_search(problem_per_astar, h=problem.h_max_pairwaise_Distance)

    if solution_node:
        print(f"Costo Totale: {solution_node.path_cost}")
        print(f"Numero passi: {len(solution_node.solution())}")
        print("Azioni:", solution_node.solution())
        print(f"Nodi esplorati da A*: {problem_per_astar.states}")
        print(f"Goal test effettuati: {problem_per_astar.goal_tests}")
        

        # Opzionale: visualizza gli stati per vedere se logica (es. refill) funziona
        # for node in solution_node.path():
        #      print(node.state)
    else:
        print("Nessuna soluzione trovata.")

def a_star1():
    problem_per_astar = InstrumentedProblem(problem)
    print("Avvio ricerca A* con euristica Manhattan...")
    solution_node = astar_search(problem_per_astar, h=problem.h_manhattan)

    if solution_node:
        print(f"Costo Totale: {solution_node.path_cost}")
        print(f"Numero passi: {len(solution_node.solution())}")
        print("Azioni:", solution_node.solution())
        print(f"Nodi esplorati da A*: {problem_per_astar.states}")
        print(f"Goal test effettuati: {problem_per_astar.goal_tests}")
        
        path = solution_node.path()
        for n in path:
    print_grid(problem, n.state, n.action)
        
        # mostra la grid
        #for n in path:
        #    print_grid(problem, n.state, n.action)
    else:
        print("Nessuna soluzione trovata.")


ucs()
print("\n\n")
a_star()
a_star1()


#bisogna considerare 3 fattori 
# A ho finito le piante e quindi l'obiettivo è raggiungere la fine
# B ho ancora piante e ancora acqua qundi continuo ad innaffiare le piante
# C ho ancora piante e ho terminato l'acqua, quindi devo riempire il serbatoio

#def h(self, node):
#    position, water, dry = node.state
#    current_pos = node.state[0]
#    current_water = node.state[1]
#    dry_plants = node.state[2]
