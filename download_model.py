from modelscope import snapshot_download

# 模型会下载到 D:\models\bge-m3 目录
snapshot_download('BAAI/bge-m3', cache_dir=r'D:\models\bge-m3')
print("下载成功！");