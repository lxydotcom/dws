
def update_environment(env):
    from ..core.get_environment_info import getEnvironmentInfo
    from .utils import Request

    # get full env id
    fullEnvironmentId = env.environment_id
    simulatedRequest = Request(**{'environment_id': fullEnvironmentId})
    output = getEnvironmentInfo(simulatedRequest)

    output = dict(output)

    if output['result'] == 'failed':
        error = output['error']
        raise RuntimeError(error)
    else:
        from .environment_record import fill_environment_from_output
        fill_environment_from_output(env, output)
