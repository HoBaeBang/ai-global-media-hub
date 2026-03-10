import logging
from config import TARGET_COUNTRIES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    logging.info("Starting Blog Automation Pipeline...")
    
    # 1. 트렌드 수집 (fetcher.py)
    # 2. 중복 검사 (db_client.py)
    # 3. 콘텐츠 생성 및 번역 (generator.py)
    # 4. 블로그 포스팅 발행 (publisher.py)
    
    logging.info("Pipeline Execution Completed.")

if __name__ == "__main__":
    main()
