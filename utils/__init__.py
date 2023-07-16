from envyaml import EnvYAML


def getEnv():
    env = None
    try:
        env = EnvYAML("../config/config.yaml")
    except (Exception) as e:
        env = EnvYAML("../../config/config.yaml")
    return env
