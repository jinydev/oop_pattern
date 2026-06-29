import os
import sys
import time
import glob
from google import genai
from PIL import Image

def get_api_key():
    # 1. Check environment variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key

    # 2. Check for .env files in source folder and parent folders
    for path in ['.env', '../.env', '../../.env']:
        if os.path.exists(path):
            with open(path, 'r') as f:
                for line in f:
                    if line.strip().startswith('GEMINI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                        if api_key:
                            return api_key
    return None

def main():
    api_key = get_api_key()
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment or .env file.", file=sys.stderr)
        print("Please set GEMINI_API_KEY environment variable or create a .env file.", file=sys.stderr)
        sys.exit(1)

    books_dir = "/Users/hojin9/dev/jinysite/pattern/src/books"
    if not os.path.exists(books_dir):
        print(f"Error: Books directory {books_dir} not found.", file=sys.stderr)
        sys.exit(1)

    img_files = glob.glob(os.path.join(books_dir, "*.jpg")) + glob.glob(os.path.join(books_dir, "*.png"))
    img_files.sort()
    
    if not img_files:
        print("No images found in the books directory.", file=sys.stderr)
        sys.exit(0)

    # Batch size limit (can be overridden via command line argument)
    limit = 30
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            pass

    print(f"Initializing Gemini client... (Batch Limit: {limit})")
    client = genai.Client(api_key=api_key)

    PROMPT = """
이 이미지는 디자인 패턴 책의 한 페이지입니다. 다음 규칙을 엄격히 준수하여 이미지의 내용을 텍스트로 추출해주세요.
1. 이미지의 내용을 1:1로 정확하게 마크다운(Markdown)으로 변환합니다.
2. 페이지 번호는 출력에서 제외합니다.
3. 코드 블록은 해당 프로그래밍 언어(Java, PHP, C++ 등)를 지정하여 마크다운 코드 블록(```java, ```php 등)으로 작성합니다.
4. 다이어그램이나 도식, 그림이 있다면 그 구조와 내용을 설명하거나 Mermaid(```mermaid)를 사용하여 유사하게 도식화해주세요.
5. 오직 변환된 마크다운 결과물만 출력합니다. (인사말 등 불필요한 서론/결론 제외)
"""

    processed_count = 0
    total_images = len(img_files)
    
    for idx, img_path in enumerate(img_files, start=1):
        basename = os.path.basename(img_path)
        md_filename = os.path.splitext(basename)[0] + ".md"
        md_path = os.path.join(books_dir, md_filename)
        
        # Skip if already processed and not empty
        if os.path.exists(md_path) and os.path.getsize(md_path) > 10:
            continue

        if processed_count >= limit:
            print(f"Reached batch limit of {limit} files. Stopping batch.")
            break

        print(f"[{idx}/{total_images}] Processing {basename}... ", end="", flush=True)
        
        max_retries = 3
        success = False
        
        for attempt in range(max_retries):
            try:
                img = Image.open(img_path)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[PROMPT, img]
                )
                
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(response.text.strip())
                
                print("Done.")
                success = True
                processed_count += 1
                break
            except Exception as e:
                err_msg = str(e).lower()
                if "429" in err_msg or "quota" in err_msg or "exhausted" in err_msg:
                    wait_sec = 20 * (attempt + 1)
                    print(f" (Rate limit hit. Waiting {wait_sec}s...) ", end="", flush=True)
                    time.sleep(wait_sec)
                else:
                    print(f" (Error: {e}) ", end="", flush=True)
                    time.sleep(5)
        
        if not success:
            print("Failed after retries.")
        
        # Respect Gemini free tier RPM limits (15 RPM -> 4.0s minimum sleep, 4.5s is safer)
        time.sleep(4.5)

    print(f"Finished batch run. Processed {processed_count} files in this batch.")

if __name__ == "__main__":
    main()
