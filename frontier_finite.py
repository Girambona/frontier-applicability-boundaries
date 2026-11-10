#!/usr/bin/env python3
"""Exact finite diagnostic example for FRONTIER. No LLM, dataset, or external packages."""
import argparse, csv, json, math
from fractions import Fraction
from pathlib import Path

H=tuple(range(4))
QUERIES=('signature','boundary')

def observation(h,q):
    if q=='signature': return int(h in (2,3,4))
    if q=='boundary': return int(h==3)
    raise ValueError(q)

def required_action(h):
    return 'B' if h in (3,4) else 'A'

def posterior(hs,q,o):
    return tuple(h for h in hs if observation(h,q)==o)

def loss(h,a): return int(required_action(h)!=a)

def bayes_risk(hs):
    if not hs: raise ValueError('Empty hypothesis set: unresolved, not zero risk.')
    return min(sum(Fraction(loss(h,a),len(hs)) for h in hs) for a in ('A','B'))

def choose_action(hs):
    if not hs: return None
    return min(('A','B'),key=lambda a:(sum(loss(h,a) for h in hs),a))

def consensus(hs):
    if not hs:return None
    actions=set(required_action(h) for h in hs)
    return next(iter(actions)) if len(actions)==1 else None

def entropy(hs):
    if not hs: raise ValueError('Empty hypothesis set.')
    return math.log2(len(hs))

def evaluate_query(hs,q):
    groups=[posterior(hs,q,o) for o in (0,1)]
    groups=[g for g in groups if g]
    residual_entropy=sum(len(g)/len(hs)*entropy(g) for g in groups)
    residual_risk=sum((Fraction(len(g),len(hs))*bayes_risk(g) for g in groups),Fraction())
    return {'query':q,'information_gain_bits':entropy(hs)-residual_entropy,
            'expected_residual_bayes_risk':float(residual_risk),
            'decision_gain':float(bayes_risk(hs)-residual_risk)}

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    candidates=[evaluate_query(H,q) for q in QUERIES]
    entropy_q=max(candidates,key=lambda r:r['information_gain_bits'])['query']
    decision_q=max(candidates,key=lambda r:r['decision_gain'])['query']
    assert entropy_q=='signature' and decision_q=='boundary'
    assert bayes_risk(H)==Fraction(1,4)
    assert evaluate_query(H,'signature')['decision_gain']==0
    assert evaluate_query(H,'boundary')['decision_gain']==.25
    rows=[]
    for policy in ('passive','entropy_one_probe','frontier_one_probe'):
        for actual in H:
            q=None if policy=='passive' else entropy_q if policy=='entropy_one_probe' else decision_q
            hs=H if q is None else posterior(H,q,observation(actual,q))
            a=choose_action(hs)
            rows.append({'policy':policy,'actual_hypothesis':actual,'query':q or 'none',
                'observation':None if q is None else observation(actual,q),
                'remaining_hypotheses':','.join(map(str,hs)),'action':a,
                'required_action':required_action(actual),'wrong':loss(actual,a),
                'probe_count':int(q is not None),'conditional_consensus':int(consensus(hs) is not None)})
    summaries=[]
    for p in ('passive','entropy_one_probe','frontier_one_probe'):
        rs=[r for r in rows if r['policy']==p]
        summaries.append({'policy':p,'correct':sum(1-r['wrong'] for r in rs),'cases':len(rs),
                         'mean_probe_count':sum(r['probe_count'] for r in rs)/len(rs)})
    # Misspecification witness: h4 mimics h2 on all available probes but needs the opposite action.
    assert all(observation(4,q)==observation(2,q) for q in QUERIES)
    assert required_action(4)!=required_action(2)
    hs=posterior(H,decision_q,observation(4,decision_q))
    a=choose_action(hs)
    assert a=='A' and loss(4,a)==1
    # A subsequent executed action-check gives a failure no retained hypothesis predicted.
    failed_action_consistent=tuple(h for h in hs if loss(h,a)==loss(4,a))
    assert not failed_action_consistent
    misspec={'actual_out_of_class':'h4','probe_outcome':observation(4,decision_q),
        'predicted_action':a,'required_action':required_action(4),'conditional_consensus_was_wrong':True,
        'after_failed_action_check':'empty hypothesis set; enter unresolved; no automatic recovery claimed'}
    # Check Proposition 2 for every nonempty subset of H in this finite loss table.
    checked=0
    for mask in range(1,1<<len(H)):
        subset=tuple(h for i,h in enumerate(H) if mask&(1<<i))
        common=consensus(subset)
        if common is not None:assert all(loss(h,common)==0 for h in subset)
        checked+=1
    assert checked==15
    data={'scope':'Exact enumeration of a constructed deterministic hypothesis table. No Gemma results.',
        'hypotheses':[{'h':h,'signature':observation(h,'signature'),'boundary':observation(h,'boundary'),
                       'correct_action':required_action(h)} for h in H],
        'query_statistics':candidates,'policies':summaries,'misspecification':misspec,
        'verification':{'all_nonempty_subsets_checked':checked,'assertions_passed':True}}
    (out/'finite_results.json').write_text(json.dumps(data,indent=2))
    with (out/'finite_trace.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps(data,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='frontier_results');args=p.parse_args();run(args.output)
