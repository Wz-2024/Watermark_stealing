import flash_attn
print(flash_attn.__version__)
print(3)

# export OAI_API_KEY=sk-cwc0kIxuSiezRF7lmQd3R5QBCARLOkR1N8ZtEyQ4h5HGKMjx


#将/data_disk/dyy/python_projects/watermark-stealing/configs/model/llama13b.yaml 中的路径修改为本地路径
#因此测试的运行脚本改为
'''
    python3 main.py configs/spoofing/llama13b/mistral_selfhash.yaml
    /data_disk/dyy/python_projects/ws/watermark-stealing-main/watermark-stealing-main/configs/scrubbing/llama13b/server_selfhash.yaml
    
    擦除代码
    python3 main.py configs/scrubbing/llama13b/server_selfhash.yaml
'''
 