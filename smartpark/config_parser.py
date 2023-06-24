import tomli


def get_config(filename: str = "config.toml") -> dict:
    with open("config.toml", mode="rb") as fp:
        config = tomli.load(fp)
    return config


def parse_config(config: dict, section: str) -> dict:
    the_config = config[section]
    return the_config
