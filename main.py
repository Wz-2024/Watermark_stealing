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


def main(cfg_path: str) -> None:
    #当前的cfg_path表示初始参数的全部内容,就是python main.py 后边跟的那个路径的全部内容
    #就是把所有的参数以dict的形式返回,此时的cfgs就是所有的参数(字典)
    cfgs = get_pydantic_models_from_path(cfg_path)
    print(f"Number of configs: {len(cfgs)}")


    for cfg in cfgs:
        #这里表示的是评估结果最终存放的位置-
        out_dir = cfg.get_result_path()    #得到的是att的那一层地址 
        with create_open(f"{out_dir}/config.txt", "w") as f:
            json.dump(cfg.model_dump(mode="json"), indent=4, fp=f)


        #使用线上工具NepTune
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
        
        #这个Server加载的是llama13b.yaml,,就是本地下载好的Llama模型 
        #Server的任务有两个,第一个是生成(meta),由于已经下载好了,-----是带水印的文本
        #此处只关注cfg.server对应的处理方法
        server = Server(cfg.meta, cfg.server)

        #这里的攻击模型是一个用HFRL得到的遵循人类指令的模型
        attacker = get_attacker(cfg)
        '''
            attacker:
                algo: 'our'
                model:
                    cfg_path: "configs/model/mistral7b.yaml"
                    skip: false
                    use_sampling: true
                querying:
                    skip: true
                    dataset: 'c4'
                    batch_size: 64
                    start_from_batch_num: 0
                    end_at_batch_num: 500
                    apply_watermark: true 
                learning:
                    skip: false
                    mode: "fast"
                    nb_queries: 30000
                generation:
                    sysprompt: 'standard'
                    spoofer_strength: 3.5
                    w_abcd: 2.0
                    w_partials: 0.0
                    w_empty: 0.0
                    w_future: 0.0
                    min_wm_count_nonempty: 2 
                    min_wm_mass_empty: 0.00007
                    future_num_cands: 5
                    future_num_options_per_fillin: 10
                    future_prefix_size: 10 
                    future_local_w_decay: 0.9 
                    panic_from: 750
                    repetition_penalty: 1.6
                    use_ft_counts: true
                    prevent_eos_if_zest_bad: true
                    use_graceful_conclusion: true 

        
        '''
        #默认跳过是true的,因此这段直接不看了
        if not attacker.cfg.querying.skip:
            attacker.query_server_and_save(server)

        #Learning是不跳过的
        if not attacker.cfg.learning.skip:
            attacker.load_queries_and_learn(base=False)
            attacker.load_queries_and_learn(base=True)

        #评估过程
        evaluator = Evaluator(
            cfg.meta.seed,
            cfg.evaluator,
            server,
            verbose=True,
            neptune_project=cfg.meta.neptune_project,
            run=run,
        )
        if not cfg.evaluator.skip:
            # Server needed only for scrubbing (to generate original watermarked completions)
            evaluator.run_eval(server, attacker, out_dir=out_dir)

        if not cfg.gradio.skip:
            run_gradio(cfg, server, attacker, evaluator)

        if cfg.meta.use_neptune:
            assert run is not None
            run.stop()

        # Clean up
        server = None  # type: ignore
        attacker = None  # type: ignore
        evaluator = None  # type: ignore
        run = None
        gc.collect()
        torch.cuda.empty_cache()

    print("Done")


if __name__ == "__main__":
    print(f"{datetime.datetime.now()}")
    if len(sys.argv) != 2:
        raise ValueError(
            f"Exactly one argument expected (the path to the config file), got {len(sys.argv)}."
        )
    main(sys.argv[1])
