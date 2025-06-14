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


def compare_configs(configs):
    if not configs:
        return
    
    # Print first config
    print("\nFirst config:")
    print(f"Device: {configs[0].meta.device}")
    print(f"Seed: {configs[0].meta.seed}")
    print(f"Output directory: {configs[0].meta.out_root_dir}")
    
    # Find differences
    print("\nDifferences:")
    
    # Compare meta config
    meta_fields = ['device', 'seed', 'out_root_dir', 'use_neptune']
    for field in meta_fields:
        values = [getattr(cfg.meta, field) for cfg in configs]
        if len(set(values)) > 1:
            print(f"\nMeta.{field}:")
            for i, cfg in enumerate(configs):
                print(f"  Config {i+1}: {getattr(cfg.meta, field)}")
    
    # Compare server config
    server_fields = ['model.name', 'watermark.scheme']
    for field in server_fields:
        values = []
        for cfg in configs:
            value = cfg.server
            for part in field.split('.'):
                value = getattr(value, part)
            values.append(value)
        if len(set(values)) > 1:
            print(f"\nServer.{field}:")
            for i, cfg in enumerate(configs):
                value = cfg.server
                for part in field.split('.'):
                    value = getattr(value, part)
                print(f"  Config {i+1}: {value}")
    
    # Compare attacker config
    attacker_fields = ['algo', 'model.name', 'learning.mode', 'generation.spoofer_strength']
    for field in attacker_fields:
        values = []
        for cfg in configs:
            value = cfg.attacker
            for part in field.split('.'):
                value = getattr(value, part)
            values.append(value)
        if len(set(values)) > 1:
            print(f"\nAttacker.{field}:")
            for i, cfg in enumerate(configs):
                value = cfg.attacker
                for part in field.split('.'):
                    value = getattr(value, part)
                print(f"  Config {i+1}: {value}")
    
    # Compare evaluator config
    evaluator_fields = ['skip', 'batch_size', 'metrics', 'eval_class', 'eval_mode']
    for field in evaluator_fields:
        values = []
        for cfg in configs:
            value = cfg.evaluator
            for part in field.split('.'):
                value = getattr(value, part)
            values.append(value)
        
        # Handle unhashable types (like lists)
        if isinstance(values[0], (list, dict, set)):
            # Convert to string representation for comparison
            str_values = [str(v) for v in values]
            if len(set(str_values)) > 1:
                print(f"\nEvaluator.{field}:")
                for i, cfg in enumerate(configs):
                    value = cfg.evaluator
                    for part in field.split('.'):
                        value = getattr(value, part)
                    print(f"  Config {i+1}: {value}")
        else:
            if len(set(values)) > 1:
                print(f"\nEvaluator.{field}:")
                for i, cfg in enumerate(configs):
                    value = cfg.evaluator
                    for part in field.split('.'):
                        value = getattr(value, part)
                    print(f"  Config {i+1}: {value}")


def main(cfg_path: str) -> None:
    cfgs = get_pydantic_models_from_path(cfg_path)
    print(f"Number of configs: {len(cfgs)}")
    print('--------------------------------')
    compare_configs(cfgs)


if __name__ == "__main__":
    print(f"{datetime.datetime.now()}")
    if len(sys.argv) != 2:
        raise ValueError(
            f"Exactly one argument expected (the path to the config file), got {len(sys.argv)}."
        )
    main(sys.argv[1])