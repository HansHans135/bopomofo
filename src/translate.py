import json
import asyncio

_default = 0.1e-100
punctuations = '、，。？！：；'


def max_index(arr):
    last = 0
    max_idx = 0
    for i in range(len(arr)):
        if arr[i][0] > last:
            last = arr[i][0]
            max_idx = i
    return max_idx


def viterbi(obs, states, start_p, trans_p, emit_p):
    V = [{}]
    path = {}

    for st in states:
        if st in start_p and st in emit_p:
            if obs[0] in emit_p[st]:
                V[0][st] = start_p[st] * emit_p[st][obs[0]]
            else:
                V[0][st] = _default ** 2
        else:
            V[0][st] = _default ** 2
        path[st] = [st]

    for t in range(1, len(obs)):
        V.append({})
        newpath = {}

        for curr_st in states:
            path_to_curr_st = []
            for prev_st in states:
                trans_prob = trans_p.get(prev_st, {}).get(curr_st, _default)
                emit_prob = emit_p.get(curr_st, {}).get(obs[t], _default)
                path_to_curr_st.append([
                    (V[t - 1].get(prev_st, _default)) * trans_prob * emit_prob,
                    prev_st
                ])
            
            max_idx = max_index(path_to_curr_st)
            curr_prob = path_to_curr_st[max_idx][0]
            prev_state = path_to_curr_st[max_idx][1]
            V[t][curr_st] = curr_prob
            newpath[curr_st] = path[prev_state] + [curr_st]
        
        path = newpath

    pl = []
    for st in states:
        pl.append([V[-1][st], st])
    
    max_idx = max_index(pl)
    prob = pl[max_idx][0]
    end_state = pl[max_idx][1]
    return prob, path[end_state]


def sort_keys(text):
    output = ''
    order = '1qaz2wsxedcrfv5tgbyhnujm8ik,9ol.0p;/-'
    for char in order:
        if char in text:
            output += char
    return output


def engtyping_end_fix(text):
    if len(text) > 0:
        if text[-1] not in ' 6347' and text[-1] not in punctuations:
            return text + ' '
        else:
            return text
    else:
        return ''


def engtyping_rearrange(text):
    tmp = ''
    output = ''
    for char in text:
        if char in ' 6347' or char in punctuations:
            output += sort_keys(tmp) + char
            tmp = ''
            continue
        tmp += char
    return output


def _decode_sentence_sync(text, hmm):
    start_probability = hmm['start_probability']
    transition_probability = hmm['transition_probability']
    emission_probability = hmm['emission_probability']
    engtyping2zh = hmm['engTyping2zh']
    
    tmp = ''
    observations = []
    text = engtyping_rearrange(engtyping_end_fix(text.lower()))
    
    for c in text:
        tmp += c
        if c in ' 6347' or c in punctuations:
            observations.append(tmp)
            tmp = ''
    
    states = []
    for observation in observations:
        if observation not in engtyping2zh:
            pass
        else:
            states.extend(engtyping2zh[observation])
    
    if len(states) == 0:
        return 0, ['']
    
    return viterbi(observations, states, start_probability, 
                   transition_probability, emission_probability)


async def decode_sentence(text, hmm):
    return await asyncio.to_thread(_decode_sentence_sync, text, hmm)


