import pandas as pd
import simpy
import scipy.stats.mstats
import numpy as np
import logging


def patient(env, patient_id, pat_class_id, starting_state, states_pool, surgery_resource, log_track):
    """Processing patients through the pool of states with queueing for states N* and I*"""
    m_log = logging.getLogger(__name__)
    state = starting_state
    while not states_pool[state].is_final:
        log_track.append({'ID': patient_id, 'PAT_CLASS': pat_class_id, 'TIME': env.now, 'STATE': state,
                          'DIRECTION': 'IN', 'QUEUE_TIME': 0, 'QUEUE_LENGTH': 0})
        m_log.info('{}: {}'.format(env.now, log_track[-1]))
        surgery_state = state[0] in ['N', 'I']
        time_before_queue = env.now
        queue_length = 0
        if (surgery_resource is not None) and surgery_state:
            queue_length = len(surgery_resource.queue)
            request = surgery_resource.request()
            yield request
        time_in_queue = env.now - time_before_queue
        duration = int(states_pool[state].generate_duration())
        yield env.timeout(duration)
        if (surgery_resource is not None) and surgery_state:
            surgery_resource.release(request)
        log_track.append({'ID': patient_id, 'PAT_CLASS': pat_class_id, 'TIME': env.now, 'STATE': state,
                          'DIRECTION': 'OUT', 'QUEUE_TIME': time_in_queue, 'QUEUE_LENGTH': queue_length})
        m_log.info('{}: {}'.format(env.now, log_track[-1]))
        state = states_pool[state].generate_next_state()
    log_track.append({'ID': patient_id, 'PAT_CLASS': pat_class_id, 'TIME': env.now, 'STATE': state,
                      'DIRECTION': 'IN', 'QUEUE_TIME': 0, 'QUEUE_LENGTH': 0})


def background_surgery_process(env, surgery_resource, duration, log_track):
    """Processing request to surgery room"""
    log_track.append({'ID': -1, 'PAT_CLASS': -1, 'TIME': env.now, 'STATE': 'IXX', 'DIRECTION': 'IN',
                      'QUEUE_TIME': 0, 'QUEUE_LENGTH': 0})
    time_before_queue = env.now
    if surgery_resource is not None:
        request = surgery_resource.request()
        yield request
    yield env.timeout(duration)
    if surgery_resource is not None:
        surgery_resource.release(request)
    log_track.append({'ID': -1, 'PAT_CLASS': -1, 'TIME': env.now, 'STATE': 'IXX', 'DIRECTION': 'OUT',
                      'QUEUE_TIME': env.now - time_before_queue, 'QUEUE_LENGTH': 0})


def generate_day_sequence(per_day_gen, time_in_day_gen, scale=1.0):
    """Generating sequence of requests within 24h"""
    seq = [0, 24*60]
    n = per_day_gen.rvs()
    for i in range(int(n * scale)):
        seq.append(int(time_in_day_gen.rvs()))
    seq.sort()
    return seq


def background_emitter(env, surgery_resource, log_track,
                       surgery_bg_event_generator, surgery_bg_time_generator, surgery_bg_scale):
    """Generating daily activity in surgery room"""
    m_log = logging.getLogger(__name__)
    while True:
        seq = surgery_bg_event_generator.generate_day_sequence(scale=surgery_bg_scale)
        m_log.info('Background surgery sequence for day: {}'.format(seq))
        for i in range(1, len(seq) - 1):
            yield env.timeout(seq[i] - seq[i - 1])
            env.process(background_surgery_process(env, surgery_resource, int(surgery_bg_time_generator.rvs()), log_track))
        yield env.timeout(seq[-1] - seq[-2])


def target_emitter(env, target_event_generator, target_patient_generator, surgery_resource, log_track, target_scale=1.0):
    """Emitting patients with inter-patients time by span generator"""
    m_log = logging.getLogger(__name__)
    counter = 0
    while True:
        seq = target_event_generator.generate_day_sequence(scale=target_scale)
        m_log.info('Planned sequence for day: {}'.format(seq))
        for i in range(1, len(seq) - 1):
            yield env.timeout(seq[i] - seq[i - 1])
            pat_state, pat_pool, pat_class = target_patient_generator.get_patient()
            env.process(patient(env, counter, pat_class, pat_state, pat_pool, surgery_resource, log_track))
            counter += 1
            m_log.info('{}: emitting new patient #{} at {}'.format(env.now, counter, seq[i]))
        yield env.timeout(seq[-1] - seq[-2])


def simulate_patients_flow(target_patient_generator, target_event_generator,
                           surgery_rooms_n, surgery_bg_event_generator, surgery_bg_time_generator, surgery_bg_scale,
                           target_flow_scale, simulation_time, use_queueing=True):
    """Run main simulation cycle"""
    log_track = []
    env = simpy.Environment()
    res = simpy.Resource(env, capacity=surgery_rooms_n) if use_queueing else None
    env.process(target_emitter(env, target_event_generator, target_patient_generator, res, log_track,
                               target_scale=target_flow_scale))
    env.process(background_emitter(env, res, log_track,
                                   surgery_bg_event_generator, surgery_bg_time_generator, surgery_bg_scale))
    env.run(until=simulation_time)
    return pd.DataFrame(log_track, columns=log_track[0].keys())


def get_queue_statistics(sim_res):
    """Basic stats for queue witing time"""
    mask = [st[0] in ['N', 'I'] for st in sim_res.STATE] & (sim_res.DIRECTION == 'OUT') & (sim_res.ID >= 0)
    mask_with_queue = mask & (sim_res.QUEUE_TIME > 0)
    qq = scipy.stats.mstats.mquantiles(sim_res[mask_with_queue].QUEUE_TIME)
    return {'PART': mask_with_queue.sum() / mask.sum(),
            'MIN': sim_res[mask_with_queue].QUEUE_TIME.min(),
            'MAX': sim_res[mask_with_queue].QUEUE_TIME.max(),
            'AVG': np.average(sim_res[mask_with_queue].QUEUE_TIME),
            'Q1': qq[0], 'Q2': qq[1], 'Q3': qq[2],
            'MAX_QUEUE_LENGTH': sim_res[mask_with_queue].QUEUE_LENGTH.max()}