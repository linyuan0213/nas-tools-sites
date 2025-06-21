import os
import json
import pickle
from datetime import datetime
from typing import Tuple, Dict, List
from loguru import logger

# 配置日志
logger.add(
    "generate_dat.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
    encoding="utf-8"
)

class FileManager:
    """统一管理文件路径和操作"""
    def __init__(self, output_dir: str = "build/bin"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    @property
    def json_path(self) -> str:
        return os.path.join(self.output_dir, "sites.json")
        
    @property
    def dat_path(self) -> str:
        return os.path.join(self.output_dir, "sites.dat")
        
    def read_json(self, path: str) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def write_json(self, data: dict, path: str = None):
        path = path or self.json_path
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
    def write_dat(self, data: dict):
        with open(self.dat_path, "wb") as f:
            pickle.dump(data, f)
            
    def clear_file(self, path: str = None):
        path = path or self.json_path
        with open(path, "w") as f:
            f.truncate(0) if os.path.exists(path) else None

class SiteDataProcessor:
    """处理站点数据"""
    @staticmethod
    def process_folder(folder_path: str) -> Tuple[List[Dict], Dict]:
        indexers = []
        confs = {}
        for filename in os.listdir(folder_path):
            if not filename.endswith(".json"):
                continue
                
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        print(f"Error: {filename} is not a dictionary")
                        continue
                        
                    indexer_data = {k: v for k, v in data.items() if k != "conf"}
                    indexers.append(indexer_data)
                    
                    if "conf" in data:
                        domain = data["domain"].split("//")[-1].split("/")[0]
                        confs[domain] = data["conf"]
            except Exception as e:
                logger.exception(f"Error reading {filename}: {str(e)}")
        return indexers, confs
        
    @staticmethod
    def format_json_file(file_path: str):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            with open(file_path, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except json.JSONDecodeError as e:
            logger.exception(f"Error decoding JSON in {file_path}: {e}")

def main():
    logger.info("脚本开始执行")
    
    try:
        # 初始化文件管理器
        file_manager = FileManager()
        logger.info(f"输出目录设置为: {file_manager.output_dir}")
        
        sites_dir = "app/sites"
        # 检查sites目录是否存在
        if not os.path.exists(sites_dir):
            logger.error(f"{sites_dir}目录不存在")
            return
        
        logger.info("开始格式化JSON文件...")
        # 格式化所有JSON文件
        json_count = 0
        for filename in os.listdir(sites_dir):
            file_path = os.path.join(sites_dir, filename)
            if filename.endswith(".json"):
                logger.debug(f"格式化文件: {filename}")
                SiteDataProcessor.format_json_file(file_path)
                json_count += 1
        logger.info(f"共格式化 {json_count} 个JSON文件")
        
        logger.info("开始处理数据...")
        # 处理数据
        file_manager.clear_file()
        indexers, confs = SiteDataProcessor.process_folder(sites_dir)
        logger.success(f"处理完成，共找到 {len(indexers)} 个索引器和 {len(confs)} 个配置")
        
        # 保存结果
        version = datetime.now().strftime("%Y%m%d%H%M")
        result = {"version": version, "indexer": indexers, "conf": confs}
        logger.info("开始保存结果...")
        file_manager.write_json(result)
        file_manager.write_dat(result)
        logger.success(f"结果已保存到: {file_manager.json_path} 和 {file_manager.dat_path}")
        logger.info("脚本执行完成")
    except Exception as e:
        logger.exception(f"脚本执行出错: {str(e)}")
        raise

if __name__ == "__main__":
    main()
