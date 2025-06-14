import datetime
# import gc
# import json
# import os
import sys

# import neptune
# import torch
from neptune.utils import stringify_unsupported

# from src.attackers import get_attacker
from src.config.meta_config import get_pydantic_models_from_path
# from src.evaluator import Evaluator
# from src.gradio import run_gradio
# from src.server import Server
# from src.utils import create_open


def main(cfg_path: str) -> None:
    cfgs = get_pydantic_models_from_path(cfg_path)
    print(f"Number of configs: {len(cfgs)}")
    print('--------------------------------')
    # print(type(cfgs))
    # for cfg in cfgs:
    #     print(cfg)
    #     print("--------------------------------")
    #     print()
    #     print()

if __name__ == "__main__":
    print(f"{datetime.datetime.now()}")
    if len(sys.argv) != 2:
        raise ValueError(
            f"Exactly one argument expected (the path to the config file), got {len(sys.argv)}."
        )
    main(sys.argv[1])
    # print(type(sys.argv[1]))
    # print(sys.argv[1])