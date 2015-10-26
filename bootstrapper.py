#!/usr/bin/python2
import argparse
import copy
import evaluator
import summarizer
import os, sys, traceback
from game import Game
from plotter import evaluation_plot, compare_evals
from  functools import partial

def comparison():
    e1 = evaluate(args.solution_name)
    e2 = evaluate(args.compare_to)
    compare_evals(e1, e2)

def convert(name):
    return name.rstrip('.py').replace('/','.').replace('solutions.','')

def evaluate(name, no_initial_training=False):
    # import the solution name into the global namespace as 'exercise'
    exercise = __import__(convert(name))
    name = convert(name)
    def load_reward_profile(agent):
        if args.custom_rewards:
            agent.adjust_rewards(*map(int, args.custom_rewards.split(',')))
        else:
            exercise.reward_profile(agent)
    # game and agent setup code
    game = Game(do_render=False)
    game.set_size(args.grid_size, args.grid_size)
    original_game = copy.copy(game)
    # fetch the agent from the provided solution
    agent = exercise.get_agent(game)
    agent.reward_scaling([1, -1, -1])
    agent.fov = args.fov
    agent.gamma = args.gamma
    agent.game.suppressed = True
    # train the agent using the provided solution
    load_reward_profile(agent)
#   exercise.reward_profile(agent)
    file_name_add = ''
    if not no_initial_training:
        if args.dephase:
            agent.dephase = True
        exercise.train(agent)
    else: 
        file_name_add = 'no_train_'
    agent.reward_scaling([1, -1, -1])
    # clean up after training
    agent.accumulated = 0   # reset accumulated rewards
    agent.set_epsilon(0.0)  # turn off exploration
    agent.game.reset()      # reset the game
    agent.game.high_score = 0
    agent.fov  = args.fov
    agent.game = original_game # if the training modifies the game, it is fixed here
    load_reward_profile(agent)
#   exercise.reward_profile(agent)
    if args.dephase:
        agent.dephase = False
        exercise.train(agent)
    # clean up after training
    # evaluate the training results
    folder = 'eval_solutions'
    file_name = evaluator.evaluate(agent, name=os.path.join(folder, file_name_add+name))
    # print out a nice summary of how the evaluation went
    summarizer.summarize_e(file_name)
    return file_name

def main():
    if args.dephase:
        file_name = evaluate(args.solution_name)
        file_name2 = evaluate(args.solution_name, no_initial_training=True)
        compare_evals(file_name, file_name2)
    else:
        num_iters = 1 if not args.multi else args.multi
        show = False if args.multi else True
        evals = []
        for iteration_number in range(num_iters):
            if args.outfile and os.path.exists(args.outfile):
                raise OSError('The destination file already exists, move it or pick another name.')
            file_name = evaluate(args.solution_name)
            if args.outfile or args.multi:
                outname = file_name if not args.outfile else args.outfile
                if args.multi:
                    outname += str(iteration_number)
                os.rename(file_name, outname)
                file_name = outname
            evals.append(file_name)

            evaluation_plot(file_name, display=show)
        if args.multi:
            summarizer.sum_sum(evals)           

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RL Learner exercise')
    parser.add_argument('solution_name', default='exercise', nargs='?', help='exercise to evaluate')
    parser.add_argument('--outfile', metavar='FILENAME', help='output file name')
    parser.add_argument('-g', '--grid_size', type=int, default=10, help='grid size')
    parser.add_argument('-f', '--fov', type=int, default=3, help='base field of view')
    parser.add_argument('--gamma', type=float, default=0.8, metavar='FLOAT', help='discount factor')
    parser.add_argument('-c', '--compare_to', metavar='OTHER_FILE', help='compare two solutions')
    parser.add_argument('--custom_rewards', metavar='CHEESE,TRAP,HUNGER', help='reward profile in the format "c,t,h" (without quotes)')
    parser.add_argument('--dephase', action='store_true', help=u'swap reward scalars (180\N{DEGREE SIGN} out of phase)')
    parser.add_argument('--multi', type=int, metavar='N', help='number of evaluations to make (single evaluations only)')
    args = parser.parse_args()
    sys.path.insert(0, 'solutions') # to avoid needing an __init__.py in the 'solutions' directory
    try:
        if args.compare_to:
            comparison()
        else:
            main()
    except SystemExit:
        exit(1)
    except KeyboardInterrupt:
        print '\rCTRL + C detected, canceling...'
        exit(2)
    except Exception, e:
        print '\nERROR'
        print 'traceback:'
        print traceback.print_exc()
        print 'message:'
        print e
        


