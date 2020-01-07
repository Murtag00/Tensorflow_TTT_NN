from __future__ import print_function
import os
import neat
import visualize
import random
from TicTacToe import *


class Neat_Train():
    game_TTT = TTT()

    averageFitness=0

    def __init__(self,generations=101,gen_intervall = 97,dir="NEAT_Files\\",showGraphics=False):
        self.generations = generations
        self.gen_intervall = gen_intervall
        self.dir = dir
        self.showGraphics = showGraphics

    @staticmethod
    def get_NNMove(field,model): ## needs improvement!
        inputVector = TTT.fieldToVector(field)
        moveVector = model.activate(tuple(inputVector)) # STUPID IMPLEMENTATION!!!!!!!
        m = TTT.vectorToMove( list(moveVector))
        while not TTT.moveLegal(field,m):
            moveVector[m] = -99999999.0
            m = TTT.vectorToMove( moveVector)
        return m         

    def match(model_function,model):
        g = Neat_Train.game_TTT # or TTT()
        g.reset()
        while not g.game_over:
            m = model_function[g.current_player](g.field,model[g.current_player])
            if g.is_moveLegal(m):
                g.make_move(m)
                (g.game_over ,WINNER) = g.eval_game()
                if not g.game_over:
                    g.swap_player()
            else:
                print("Illegal move!")
        return WINNER

    @staticmethod
    def calc_AVGFitness(genomes):
        Neat_Train.averageFitness = 0
        for genome_id, genome in genomes:
            Neat_Train.averageFitness += genome.fitness
        Neat_Train.averageFitness = Neat_Train.averageFitness / len(genomes)

    @staticmethod
    def fitness(genomes,config):
        for genome_id, genome in genomes:
            genome.fitness = 0
        for genome_id, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome,config)
            for opponent_id, opponent_genome in genomes:
                if not opponent_id == genome_id:
                    opp_net = neat.nn.FeedForwardNetwork.create(genome,config)
                    for i in range(10):
                        move_func = Neat_Train.get_NNMove
                        winner = Neat_Train.match([move_func,move_func],[net,opp_net])
                        if winner ==  'X':
                            genome.fitness+=1
                        elif winner == 'O':
                            opponent_genome.fitness+=1
        Neat_Train.calc_AVGFitness(genomes)



    def score_match(self,model):
        g = self.game_TTT
        g.reset()
        g.field[random.randrange(0,9)] = [g.PLAYER_SIGNS[0]]
        g.current_player = 1
        while not g.game_over:
            if g.current_player == 0:
                m = g.get_NNMove()
            else:
                m = Neat_Train.get_NNMove(g.field,model)
            if g.is_moveLegal(m):
                g.make_move(m)
                (g.game_over ,WINNER) = g.eval_game()
                if not g.game_over:
                    g.swap_player()
            else:
                print("Illegal move!")
        return WINNER

    def genome_vs_Supervised(self,genome_net,total=100):
        losses = 0
        for i in range(total):
            winner = self.score_match(genome_net)
            if winner ==  'X':
                losses+=1
        print("genome lost: ",losses," matches out of", 
        total," against the supervised model")
            
    def show_Winner(self,winner,p):
        print('\nBest genome:\n{!s}'.format(winner))
        
        print("Winner Fitness is ", winner.fitness, "\n average fitness ist:", self.averageFitness,
        "\n winner is", winner.fitness/self.averageFitness,"times as fit as the average")

        winner_net = neat.nn.FeedForwardNetwork.create(winner, p.config)
        self.genome_vs_Supervised(winner_net)
        
        node_names = {}
        for index in range(-27,9):
            node_names[index] = str(index)
        if self.showGraphics:
            visualize.draw_net(p.config, winner, True, node_names=node_names,filename=self.dir+"winner.svg")

    def train_population(self,p):
        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        p.add_reporter(neat.Checkpointer(self.gen_intervall,filename_prefix=self.dir+"neat-checkpoint-"))

        winner = p.run(self.fitness,self.generations)

        self.show_Winner(winner,p)
        if  self.showGraphics:
            visualize.plot_stats(stats, ylog=False, view=True,filename=self.dir+"avg_fitness.svg")
            visualize.plot_species(stats, view=True,filename=self.dir+"speciation.svg")


    def run(self,file_path):
        config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction
        ,neat.DefaultSpeciesSet,neat.DefaultStagnation
        ,file_path)

        p = neat.population.Population(config)
        self.train_population(p)

    def check_out_population(self,p):  
        winner = p.run(fitness,1)
        self.show_Winner(winner,p)

    def continue_training(self,check_point_path):
        populus = neat.Checkpointer.restore_checkpoint(check_point_path)
        self.train_population(populus)
