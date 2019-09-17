import CTFd.plugins.CTFd_ICPC_Challenges.models as models
import requests

from CTFd.models import db
from .config import JUDGE_ADDR, JUDGE_PORT, JUDGE_TOKEN

ses = requests.session()
ses.headers.update({'X-Judge-Server-Token': JUDGE_TOKEN})


def judge_online(func):
    def check(*args, **kwargs):
        try:
            res = ses.get(f'http://{JUDGE_ADDR}:{JUDGE_PORT}/ping').json()
            if not res['message'] == 'pong':
                return False, 'Judge Misbehaved'
        except Exception:
            return False, 'Judge Offline'
        return func(*args, **kwargs)

    return check


def filter_judge_cases(file_list):
    inputs = []
    outputs = []
    for i in file_list:
        if '.in' == i.location[-3:]:
            inputs.append(i)
        elif '.out' == i.location[-4:]:
            outputs.append(i)
    input_names = [i.location.split('/')[-1] for i in inputs]
    output_names = [i.location.split('/')[-1] for i in outputs]
    available_cases = [i.split('.')[0] for i in input_names if i.split('.')[
        0] + '.out' in output_names]
    j, k = 0, 0
    for i in range(len(available_cases)):
        while available_cases[i] + '.in' not in inputs[j].location:
            j += 1
        while available_cases[i] + '.out' not in outputs[k].location:
            k += 1
        yield inputs[j], outputs[k]
    return


@judge_online
def challenge_prepared(prob_id):
    res = ses.get(
        f'http://{JUDGE_ADDR}:{JUDGE_PORT}/problem/info/{prob_id}'
    )
    try:
        if res.json()['content']['exists']:
            return True
        if res.status_code != 200:
            ses.get(f'http://{JUDGE_ADDR}:{JUDGE_PORT}/init')
    except Exception:
        pass
    return False


@judge_online
def prepare_challenge(challenge):
    result = {'status': 0, 'message': '', 'content': ''}
    try:
        if challenge.problem_id != -1 and challenge_prepared(challenge.id):
            return True
        files = models.JudgeCaseFiles.query.filter_by(challenge_id=challenge.id).all()
        data = {
            'cases': [],
            'limits': {
                'max_cpu_time': challenge.max_cpu_time,
                'max_real_time': challenge.max_real_time,
                'max_memory': challenge.max_memory,
                'max_process_number': challenge.max_process_number,
                'max_output_size': challenge.max_output_size,
                'max_stack': challenge.max_stack,
            }
        }
        for i, o in filter_judge_cases(files):
            data['cases'].append({'input': i.location, 'output': o.location})
        result = ses.post(
            f'http://{JUDGE_ADDR}:{JUDGE_PORT}/problem/add', json=data).json()
        if result['status'] >= 500:
            ses.get(f'http://{JUDGE_ADDR}:{JUDGE_PORT}/init')
            result = ses.post(
                f'http://{JUDGE_ADDR}:{JUDGE_PORT}/problem/add', json=data).json()

        assert (result['status'] == 200)
        challenge.problem_id = result['content']['problem_id']
        db.session.commit()
    except AssertionError:
        return {
            'result': -100,
            'message': 'Judger Error During Initialization',
        }
    except Exception as e:
        return False


@judge_online
def request_judge(prob_id, code, lang):
    res = {'status': 0, 'message': '', 'content': ''}
    try:
        res = ses.post(
            f'http://{JUDGE_ADDR}:{JUDGE_PORT}/judge',
            json={
                'problem_id': prob_id,
                'code': code,
                'lang': lang,
            }
        ).json()
        assert (res['status'] == 200)
        return res['content']
    except AssertionError:
        return {'result': -1, 'message': 'Judger Internal Error'}
    except Exception as e:
        return {'result': -1, 'message': 'Unknown Error'}


@judge_online
def update_problem(prob_id, limits=None, cases=None):
    res = {'status': 0, 'message': '', 'content': ''}
    if limits:
        res = ses.post(
            f'http://{JUDGE_ADDR}:{JUDGE_PORT}/problem/update/limits/{prob_id}',
            json=limits
        ).json()
    if cases:
        res = ses.post(
            f'http://{JUDGE_ADDR}:{JUDGE_PORT}/problem/update/cases/{prob_id}',
            json=cases
        ).json()
    assert (res['status'] == 200)


@judge_online
def query_details(submission_id):
    try:
        res = ses.get(
            f'http://{JUDGE_ADDR}:{JUDGE_PORT}/submission/{submission_id}',
        ).json()
        return res
    except:
        raise FileNotFoundError()


@judge_online
def submission_list():
    res = ses.get(
        f'http://{JUDGE_ADDR}:{JUDGE_PORT}/submission'
    ).json()
