import argparse

def summarize_e(name):
    print '========================'
    print '{0} summary:'.format(name)

    high_score = 0
    deaths = 0
    timeouts = 0
    best_local = 0
    with open(name, 'r') as f:
        text = f.read()
        for cur_step, line in enumerate(text.splitlines()):
            parts = map(float, line.split(',')) # round eff, deaths, average, cumul, local
            score = parts[0]
            deaths = parts[1]
            timeouts = parts[2]
            accumulated_reward = parts[3]
            local = parts[4]
            if local > best_local:
                best_local = max(local, best_local)
                bl_round = cur_step
            high_score = max(score, high_score)

    print 'Accumulated reward: {0}'.format(accumulated_reward)
    print 'Best local reward: {0} in round {1}'.format(best_local, bl_round)
    print 'Total deaths: {0}'.format(deaths)
    print 'Total timeouts: {0}'.format(timeouts)
    print 'High Score: {0}'.format(high_score)
    magic = (best_local * 2 - deaths * 3) * (high_score + accumulated_reward / high_score) * 0.001 + (high_score * 0.001)
    print 'Evaluation score: {0}'.format(magic)
    return (accumulated_reward, best_local, bl_round, deaths, timeouts, high_score)

def summarize(name):
    print '========================'
    print '{0} summary:'.format(name)
    best_average = 0
    best_local = 0
    ba_round = 0
    bl_round = 0
    deaths = 0
    timeouts = 0
    with open(name, 'r') as f:
        text = f.read()
        for cur_round, line in enumerate(text.splitlines()):
            parts = map(float, line.split(',')) # round eff, deaths, average, cumul, local
            round_deaths = parts[1]
            average = parts[2]
            local = parts[4]
            if average > best_average and cur_round > 50:
                best_average = max(average, best_average)
                ba_round = cur_round
            if local > best_local:
                best_local = max(local, best_local)
                bl_round = cur_round
            if round_deaths == -1:
                timeouts += 1
            else:
                deaths += round_deaths

    print 'Best average: {0} in round {1}'.format(best_average, ba_round)
    print 'Best local reward: {0} in round {1}'.format(best_local, bl_round)
    print 'Total deaths: {0}'.format(deaths)
    print 'Total timeouts: {0}'.format(timeouts)
    return (best_average, ba_round, best_local, bl_round, deaths, timeouts)

def make_plot(bav, bar, blv, blr, dts, tos):
    raise Exception('Not implemented')

def main():
    global args
    for fn in args.names:
        data = summarize_e(fn)
        if args.plot:
            make_plot(*data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='graph plotter')
    parser.add_argument('names', nargs='+', help='input file name(s)')
    parser.add_argument('--plot', help='plot results')
    args = parser.parse_args()
    try:
        main()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    except Exception as e:
        print 'error', e
        raise
