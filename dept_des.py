import pandas as pd
import simpy


def patient(env, patient_id, starting_state, states_pool, surgery_resource, logger):
    """Processing patients through the pool of states with queueing for states N* and I*"""
    state = starting_state
    while not states_pool[state].is_final:
        logger.append({'ID': patient_id, 'TIME': env.now, 'STATE': state, 'DIRECTION': 'IN'})
        # print(env.now, logger[-1])
        surgery_state = state[0] in ['N', 'I']
        if surgery_state:
            request = surgery_resource.request()
            yield request
        duration = int(states_pool[state].generate_duration())
        yield env.timeout(duration)
        if surgery_state:
            surgery_resource.release(request)
        logger.append({'ID': patient_id, 'TIME': env.now, 'STATE': state, 'DIRECTION': 'OUT'})
        # print(env.now, logger[-1])
        state = states_pool[state].generate_next_state()
    logger.append({'ID': patient_id, 'TIME': env.now, 'STATE': state, 'DIRECTION': 'IN'})


def emitter(env, span_generator, states_pool, surgery_resource, logger):
    """Emitting patients with inter-patients time by span generator"""
    counter = 0
    while True:
        env.process(patient(env, counter, '_01', states_pool, surgery_resource, logger))
        counter += 1
        span_dur = int(span_generator.rvs())
        print(str(env.now) + ': emitting new patient #' + str(counter) + ' waiting ' + str(span_dur))
        yield env.timeout(span_dur)


def simulate_patients_flow(n_surgeries, states_pool, span_generator, simulation_time):
    log_track = []
    env = simpy.Environment()
    res = simpy.Resource(env, capacity=n_surgeries)
    env.process(emitter(env, span_generator, states_pool, res, log_track))
    env.run(until=simulation_time)
    return pd.DataFrame(log_track, columns=['TIME', 'ID', 'STATE', 'DIRECTION'])
