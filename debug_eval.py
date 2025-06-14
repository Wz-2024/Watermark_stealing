import datetime
import gc
import json
import os
import sys

import neptune
import torch
from neptune.utils import stringify_unsupported

from src.attackers import get_attacker
from src.config.meta_config import get_pydantic_models_from_path
from src.evaluator import Evaluator
from src.gradio import run_gradio
from src.server import Server
from src.utils import create_open
import os
from accelerate import Accelerator, PartialState

# 设置 CUDA_VISIBLE_DEVICES 环境变量
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

# 重新初始化 accelerate 配置
state = PartialState()
# 可以打印配置信息来确认
print(f"当前分布式环境状态: {state}")
print(f"当前可用的设备数量: {state.num_processes}")

cfg_path ='configs/spoofing/llama13b/mistral_selfhash.yaml'
cfgs = get_pydantic_models_from_path(cfg_path)
print(f"Number of configs: {len(cfgs)}")
cfg=cfgs[14]
out_dir = cfg.get_result_path()
with create_open(f"{out_dir}/config.txt", "w") as f:
    json.dump(cfg.model_dump(mode="json"), indent=4, fp=f)
cfg.meta.use_neptune=False
if cfg.meta.use_neptune:
    mode = "scrub" if "dipper" in cfg.attacker.model.name else "spoof"
    model = "llama" if "llama" in cfg.meta.out_root_dir else "mistral"
    run = neptune.init_run(
        project=cfg.meta.neptune_project,
        api_token=os.environ["NEPTUNE_API_TOKEN"],
        name=f"{mode}-{model}",
        monitoring_namespace="monitoring-namespace",
    )  # your credentials
    # Set up logging
    run["cfg_path"] = cfg_path
    run["config"] = stringify_unsupported(cfg.model_dump(mode="json"))
else:
    run = None

print('正在加载Server,attacker')
server = Server(cfg.meta, cfg.server)
attacker = get_attacker(cfg)

if not attacker.cfg.querying.skip:
    attacker.query_server_and_save(server)

print('正在加载cache')
if not attacker.cfg.learning.skip:
    #加载带水印的文本数据,分析文本中的token模式,学习水印的特征,将学习结果保存在了counts_wn中
    attacker.load_queries_and_learn(base=False)
    #加载不带水印的文本数据,分析文本中的token模式,学习水印的特征,将学习结果保存在了counts_base中
    attacker.load_queries_and_learn(base=True)
print('正在初始化Evaluator')
evaluator = Evaluator(
    cfg.meta.seed,
    cfg.evaluator,
    server,
    verbose=True,
    neptune_project=cfg.meta.neptune_project,
    run=run,
)
print('开始尝试评估')
if not cfg.evaluator.skip:
    print(cfg.evaluator.skip)
    # Server needed only for scrubbing (to generate original watermarked completions)
    evaluator.run_eval(server, attacker, out_dir=out_dir)