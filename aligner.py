import sklearn.linear_model
import numpy as np
import itertools
import forkpy

from subtitles import Subtitles

def aggregate(subs, window_duration):
    total_duration = int(subs[-1].stop)
    n_windows = total_duration//window_duration
    windows = [list() for i in range(n_windows)]
    for i in range(n_windows):
        start, stop = i*window_duration, (i+1)*window_duration
        for j in range(len(subs)):
            if ((start <= int(subs[j].start) < stop)
            or (start <= int(subs[j].stop) < stop)):
                windows[i].append(j)
    return windows

def partition(subs, target_average, early_stop=5000):
    search_area = [0, int(subs[-1].stop)]
    windows, window_duration = list(), 0.
    while True:
        if search_area[1] - search_area[0] <= early_stop:
            return windows, window_duration
        window_duration = int(.5 * sum(search_area))
        windows = aggregate(subs, window_duration)
        average = float(sum(map(len, windows))) / len(windows)
        if average <= target_average:
            search_area[0] = window_duration
        if average >= target_average:
            search_area[1] = window_duration

def select(subs, target_average, threshold, direction=1):
    windows, window_duration = partition(subs, target_average)
    cursor = int(threshold * len(windows))
    while True:
        if 1.25 * target_average >= len(windows[cursor]) >= target_average:
            break
        cursor += direction
    return cursor*window_duration, windows[cursor]

def align(tgt, selection, wl):
    top = 0, dict()
    for length in range(len(selection), 0, -1):
        for combination in itertools.combinations(selection, length):
            wl.cursor = 0
            n_matches = 0
            matches = dict()
            for sub in combination:
                match = wl.align(tgt[sub])
                if match is not None:
                    matches[sub] = match
                    n_matches += len(matches[sub])
            if n_matches > top[0]:
                top = n_matches, matches
    return top[1]

def offset(subs, matches, wl):
    values = []
    for sub, words in matches.items():
        average_start = sum([wl[w].lower_bound for w in words]) / len(words)
        average_stop = sum([wl[w].upper_bound for w in words]) / len(words)
        duration = average_stop - average_start
        correction = (duration-int(subs[sub].stop)+int(subs[sub].start))//2
        values.append(int(subs[sub].start) - average_start + correction)
    if len(values) == 0:
        return 0
    return sorted(values)[len(values)//2]

def fit(tgt, ref, target_average, checkpoint):
    wl = ref.to_word_list()
    t, slice = select(tgt, target_average, checkpoint)
    return t, offset(tgt, align(tgt, slice, wl), wl)

def task(args, worker):
    return fit(args["tgt"], args["ref"], args["count"], args["checkpoint"])

def process(ref, tgt, count=5, checkpoints=[.2, .4, .6, .8]):
    factory = forkpy.Factory(verbosity=forkpy.Factory.PROGRESS)
    for checkpoint in checkpoints:
        factory.assign(forkpy.Task({
            "tgt": tgt,
            "ref": ref,
            "count": count,
            "checkpoint": checkpoint
        }, task))
    factory.start()
    factory.join()
    x, y = [], []
    for result in factory.results:
        x.append(result[forkpy.Task.KEY_RESULT][0])
        y.append(result[forkpy.Task.KEY_RESULT][1])
    model = sklearn.linear_model.LinearRegression()
    x = np.array(x).reshape((-1, 1))
    y = np.array(y)
    model.fit(x, y)
    print("Intercept:", model.intercept_)
    print("Slope:", float(model.coef_))
    print("Regression coefficient:", model.score(x, y))
    for sub in tgt:
        sub.start.sync(model.intercept_, float(model.coef_))
        sub.stop.sync(model.intercept_, float(model.coef_))
