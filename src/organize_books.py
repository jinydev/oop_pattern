import os
import re
import shutil

# Paths
SRC_DIR = "/Users/hojin9/dev/jinysite/pattern/src"
BOOKS_DIR = os.path.join(SRC_DIR, "books")
IMAGES_DIR = os.path.join(BOOKS_DIR, "images")

# Page mappings for chapters (1-indexed, inclusive)
CHAPTERS = {
    0:  (20, 25, "디자인 패턴"),
    1:  (33, 57, "팩토리 패턴"),
    2:  (58, 84, "싱글턴 패턴"),
    3:  (85, 105, "팩토리 메서드 패턴"),
    4:  (106, 128, "추상 팩토리 패턴"),
    5:  (129, 148, "빌더 패턴"),
    6:  (149, 164, "프로토타입 패턴"),
    7:  (170, 184, "어댑터 패턴"),
    8:  (185, 202, "브리지 패턴"),
    9:  (203, 228, "복합체 패턴"),
    10: (229, 243, "장식자 패턴"),
    11: (244, 262, "파사드 패턴"),
    12: (263, 287, "플라이웨이트 패턴"),
    13: (288, 318, "프록시 패턴"),
    14: (326, 341, "반복자 패턴"),
    15: (342, 362, "명령 패턴"),
    16: (363, 382, "방문자 패턴"),
    17: (383, 403, "체인 패턴"),
    18: (404, 423, "감시자 패턴"),
    19: (424, 437, "중재자 패턴"),
    20: (438, 459, "상태 패턴"),
    21: (460, 476, "메멘토 패턴"),
    22: (477, 496, "템플릿 메서드 패턴"),
    23: (497, 515, "전략 패턴"),
    24: (516, 531, "인터프리터 패턴"),
}

# Non-chapter file mappings
NON_CHAPTER_FILES = {
    "author.md": (5, 5),
    "preface.md": (6, 7),
    "part01/index.md": (26, 32),
    "part02/index.md": (165, 169),
    "part03/index.md": (319, 325),
}

def clean_destinations():
    """Remove any previously created chapter folders and non-chapter files to start fresh."""
    print("Cleaning up previous generated folders and files...")
    for ch_num in CHAPTERS:
        ch_dir = os.path.join(SRC_DIR, f"ch{ch_num:02d}")
        if os.path.exists(ch_dir):
            shutil.rmtree(ch_dir)
            print(f"Removed folder: {ch_dir}")
            
    for filename in NON_CHAPTER_FILES:
        filepath = os.path.join(SRC_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Removed file: {filepath}")

    root_index = os.path.join(SRC_DIR, "index.md")
    if os.path.exists(root_index):
        os.remove(root_index)
        print(f"Removed root index file: {root_index}")

def read_page(page_num):
    """Read the content of a page file by number."""
    filename = f"page_{page_num:03d}_img_01.md"
    filepath = os.path.join(BOOKS_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def process_image_references(text, ch_num):
    """Update image references in text and move referenced SVG files."""
    ch_img_dir = os.path.join(SRC_DIR, f"ch{ch_num:02d}", "img")
    os.makedirs(ch_img_dir, exist_ok=True)
    
    # Regex to match image patterns like ![그림 5-8](images/fig_5_8.svg) or (fig_5_8.svg)
    img_pattern = r"!\[([^\]]*)\]\((?:\./)?(?:images/)?(fig_(\d+)_([^\)]+))\)"
    
    def replace_func(match):
        alt_text = match.group(1)
        filename = match.group(2)
        
        # Source path of the SVG image
        src_path = os.path.join(IMAGES_DIR, filename)
        dest_path = os.path.join(ch_img_dir, filename)
        
        if os.path.exists(src_path):
            shutil.move(src_path, dest_path)
            print(f"  Moved image: {filename} -> ch{ch_num:02d}/img/")
        elif os.path.exists(dest_path):
            # Already moved in a previous run or by wildcard
            pass
        else:
            print(f"  Warning: Image {filename} not found in source or destination!")
            
        return f"![{alt_text}](./img/{filename})"
    
    updated_text = re.sub(img_pattern, replace_func, text)
    return updated_text

def pre_move_images():
    """Pre-emptively move all images in the images folder to their respective chapter folders by filename pattern."""
    if not os.path.exists(IMAGES_DIR):
        print("Source images folder not found (or already moved).")
        return
        
    for filename in os.listdir(IMAGES_DIR):
        if filename.endswith(".svg"):
            # Extract chapter number from fig_X_Y.svg
            match = re.match(r"^fig_(\d+)_\d+(?:_\d+)?\.svg$", filename)
            if match:
                ch_num = int(match.group(1))
                if ch_num in CHAPTERS:
                    ch_img_dir = os.path.join(SRC_DIR, f"ch{ch_num:02d}", "img")
                    os.makedirs(ch_img_dir, exist_ok=True)
                    src_path = os.path.join(IMAGES_DIR, filename)
                    dest_path = os.path.join(ch_img_dir, filename)
                    shutil.move(src_path, dest_path)
                    print(f"Pre-moved {filename} -> ch{ch_num:02d}/img/")
                else:
                    print(f"Warning: image {filename} maps to invalid chapter {ch_num}")

def run_organization():
    # 1. Clean up
    clean_destinations()
    
    # 2. Pre-move images by pattern
    pre_move_images()
    
    # 3. Process chapters
    print("Processing chapters...")
    for ch_num, (start, end, title) in CHAPTERS.items():
        ch_dir = os.path.join(SRC_DIR, f"ch{ch_num:02d}")
        os.makedirs(ch_dir, exist_ok=True)
        
        combined_pages = []
        for p in range(start, end + 1):
            content = read_page(p)
            if content:
                combined_pages.append(content)
                
        combined_text = "\n\n".join(combined_pages)
        # Update references and make sure any missed images are moved
        updated_text = process_image_references(combined_text, ch_num)
        
        dest_filepath = os.path.join(ch_dir, "index.md")
        front_matter = f"---\nlayout: docs\ntitle: \"CHAPTER {ch_num} {title}\"\n---\n\n{{% raw %}}\n"
        with open(dest_filepath, "w", encoding="utf-8") as f:
            f.write(front_matter + updated_text + "\n{% endraw %}\n")
        print(f"Created chapter index: ch{ch_num:02d}/index.md (Pages {start}-{end})")
        
    # 4. Process non-chapter files
    print("Processing non-chapter files...")
    for filename, pages in NON_CHAPTER_FILES.items():
        combined_pages = []
        # If it is a tuple of pages (like cover.md: 1, 2, 4)
        if len(pages) > 2:
            page_list = pages
        else:
            page_list = range(pages[0], pages[1] + 1)
            
        for p in page_list:
            content = read_page(p)
            if content:
                combined_pages.append(content)
                
        combined_text = "\n\n".join(combined_pages)
        
        # Post-process combined page text (Deduplication, raw page number removal, and inline pattern learning links)
        import re

        if filename == "part03/index.md":
            # 1. Clean up duplicate paragraphs due to transcription split on page 322/323
            # We target the literal '322' prefix to avoid clipping '참조값' on page 322
            combined_text = re.sub(
                r'322\s+조값을 가지며 참조를 통해 객체의 의존 관계를 형성합니다\. 이렇게 분리되는 객체는 알고리즘 형태로 대체됩니다\.\s+분리된 객체의 참조값은 매개변수를 통해 전달하거나 별도의 setter 메서드를 통해 설정할 수 있습니다\. 이때 기존 객체에는 의존 관계인 외부 객체를 제어하는 로직이 필요합니다\.',
                '',
                combined_text
            )
            # Remove duplicate first list or clean it
            pattern_list_to_remove = "* 감시자 패턴\n* 메멘토 패턴\n* 명령 패턴\n* 반복자 패턴\n* 방문자 패턴\n* 복합체 패턴 (구조)\n* 브리지 패턴 (구조)\n* 빌더 패턴 (생성)\n* 상태 패턴\n* 싱글턴 패턴 (생성)\n* 어댑터 패턴 (구조)\n* 인터프리터 패턴\n* 장식자 패턴 (구조)\n* 전략 패턴\n* 중재자 패턴\n* 체인 패턴\n* 추상 팩토리 패턴 (생성)\n* 템플릿 메서드 패턴\n* 파사드 패턴 (구조)\n* 팩토리 메서드 패턴 (생성)\n* 팩토리 패턴 (생성)\n* 프로토타입 패턴 (생성)\n* 프록시 패턴 (구조)\n* 플라이웨이트 패턴 (구조)"
            combined_text = combined_text.replace(pattern_list_to_remove, "")

        # Clean up raw page numbers globally
        combined_text = re.sub(r'\n\s*\d+\s*\n', '\n\n', combined_text)
        combined_text = re.sub(r'^\d+\s*$', '', combined_text, flags=re.MULTILINE)

        if filename == "part01/index.md":
            # Remove duplicate alphabetical list of all patterns from page 28
            pattern_list_to_remove = "* 감시자 패턴\n* 메멘토 패턴\n* 명령 패턴\n* 반복자 패턴\n* 방문자 패턴\n* 복합체 패턴\n* 브리지 패턴\n* 빌더 패턴\n* 상태 패턴\n* 싱글턴 패턴\n* 어댑터 패턴\n* 인터프리터 패턴\n* 장식자 패턴\n* 전략 패턴\n* 중재자 패턴\n* 체인 패턴\n* 추상 팩토리 패턴\n* 템플릿 메서드 패턴\n* 파사드 패턴\n* 팩토리 메서드 패턴\n* 팩토리 패턴\n* 프로토타입 패턴\n* 프록시 패턴\n* 플라이웨이트 패턴"
            combined_text = combined_text.replace(pattern_list_to_remove, "")

            # Fix page split word '팩\n\n토리에'
            combined_text = re.sub(r'팩\s+토리에', '팩토리에', combined_text)

            combined_text = combined_text.replace("### 팩토리 패턴", "### 팩토리 패턴\n\n[학습하기](/ch01/)")
            combined_text = combined_text.replace("### 싱글턴 패턴", "### 싱글턴 패턴\n\n[학습하기](/ch02/)")
            combined_text = combined_text.replace("### 팩토리 메서드 패턴", "### 팩토리 메서드 패턴\n\n[학습하기](/ch03/)")
            combined_text = combined_text.replace("### 추상 팩토리 패턴", "### 추상 팩토리 패턴\n\n[학습하기](/ch04/)")
            combined_text = combined_text.replace("### 빌더 패턴", "### 빌더 패턴\n\n[학습하기](/ch05/)")
            combined_text = combined_text.replace("### 프로토타입 패턴", "### 프로토타입 패턴\n\n[학습하기](/ch06/)")
        elif filename == "part02/index.md":
            # Remove duplicate alphabetical matrix list of all patterns
            matrix_list_to_remove = "감시자 패턴 | 메멘토 패턴\n" \
                                    "명령 패턴 | 반복자 패턴\n" \
                                    "방문자 패턴 | 복합체 패턴 | **브리지 패턴**\n" \
                                    "빌더 패턴 | 상태 패턴\n" \
                                    "싱글턴 패턴 | **어댑터 패턴** | 인터프리터 패턴\n" \
                                    "**장식자 패턴** | 전략 패턴\n" \
                                    "중재자 패턴 | 체인 패턴\n" \
                                    "추상 팩토리 패턴 | 템플릿 메서드 패턴\n" \
                                    "**파사드 패턴** | 팩토리 메서드 패턴\n" \
                                    "팩토리 패턴 | 프로토타입 패턴\n" \
                                    "**프록시 패턴** | **플라이웨이트 패턴**\n\n" \
                                    "*(참고: 구조 패턴에 해당하는 패턴들이 강조 표시되어 있습니다.)*"
            combined_text = combined_text.replace(matrix_list_to_remove, "")

            combined_text = combined_text.replace("### 어댑터 패턴", "### 어댑터 패턴\n\n[학습하기](/ch07/)")
            combined_text = combined_text.replace("### 브리지 패턴", "### 브리지 패턴\n\n[학습하기](/ch08/)")
            combined_text = combined_text.replace("### 복합체 패턴", "### 복합체 패턴\n\n[학습하기](/ch09/)")
            combined_text = combined_text.replace("### 장식자 패턴", "### 장식자 패턴\n\n[학습하기](/ch10/)")
            combined_text = combined_text.replace("### 파사드 패턴", "### 파사드 패턴\n\n[학습하기](/ch11/)")
            combined_text = combined_text.replace("### 플라이웨이트 패턴", "### 플라이웨이트 패턴\n\n[학습하기](/ch12/)")
            combined_text = combined_text.replace("### 프록시 패턴", "### 프록시 패턴\n\n[학습하기](/ch13/)")
        elif filename == "part03/index.md":

            # 2. Add learning links
            combined_text = combined_text.replace("### 반복자 패턴", "### 반복자 패턴\n\n[학습하기](/ch14/)")
            combined_text = combined_text.replace("### 명령 패턴", "### 명령 패턴\n\n[학습하기](/ch15/)")
            combined_text = combined_text.replace("### 방문자 패턴", "### 방문자 패턴\n\n[학습하기](/ch16/)")
            combined_text = combined_text.replace("### 체인 패턴", "### 체인 패턴\n\n[학습하기](/ch17/)")
            combined_text = combined_text.replace("### 감시자 패턴", "### 감시자 패턴\n\n[학습하기](/ch18/)")
            combined_text = combined_text.replace("### 중재자 패턴", "### 중재자 패턴\n\n[학습하기](/ch19/)")
            combined_text = combined_text.replace("### 상태 패턴", "### 상태 패턴\n\n[학습하기](/ch20/)")
            combined_text = combined_text.replace("### 메멘토 패턴", "### 메멘토 패턴\n\n[학습하기](/ch21/)")
            combined_text = combined_text.replace("### 템플릿 메서드 패턴", "### 템플릿 메서드 패턴\n\n[학습하기](/ch22/)")
            combined_text = combined_text.replace("### 전략 패턴", "### 전략 패턴\n\n[학습하기](/ch23/)")

            # 3. Add Interpreter pattern under ### with learning link
            combined_text += "\n\n### 인터프리터 패턴\n\n" \
                             "인터프리터 패턴은 언어의 문법 규칙을 나타내는 클래스들을 정의하고, " \
                             "이들을 사용하여 언어로 표현된 문장을 해석하고 실행하는 패턴입니다.\n\n" \
                             "[학습하기](/ch24/)"
        
        NON_CHAPTER_TITLES = {
            "author.md": "지은이 소개",
            "preface.md": "지은이의 말",
            "part01/index.md": "Part 1 생성 패턴",
            "part02/index.md": "Part 2 구조 패턴",
            "part03/index.md": "Part 3 행동 패턴",
        }
        front_matter = f"---\nlayout: docs\ntitle: \"{NON_CHAPTER_TITLES[filename]}\"\n---\n\n{{% raw %}}\n"
        dest_filepath = os.path.join(SRC_DIR, filename)
        os.makedirs(os.path.dirname(dest_filepath), exist_ok=True)
        with open(dest_filepath, "w", encoding="utf-8") as f:
            f.write(front_matter + combined_text + "\n{% endraw %}\n")
        print(f"Created non-chapter file: {filename} (Pages {list(page_list)})")

    # 5. Generate root index.md
    generate_root_index()

def generate_root_index():
    print("Generating root index.md...")
    index_content = """---
layout: welcome
title: "쉽게 배워 바로 써먹는 디자인 패턴"
permalink: /
---

# 쉽게 배워 바로 써먹는 디자인 패턴
24가지 패턴으로 알아보는 객체지향의 원리

## CHAPTER 0
- [CHAPTER 0 디자인 패턴](ch00/)

## PART 1 생성 패턴 (Creational Patterns)
- [CHAPTER 1 팩토리 패턴](ch01/)
- [CHAPTER 2 싱글턴 패턴](ch02/)
- [CHAPTER 3 팩토리 메서드 패턴](ch03/)
- [CHAPTER 4 추상 팩토리 패턴](ch04/)
- [CHAPTER 5 빌더 패턴](ch05/)
- [CHAPTER 6 프로토타입 패턴](ch06/)

## PART 2 구조 패턴 (Structural Patterns)
- [CHAPTER 7 어댑터 패턴](ch07/)
- [CHAPTER 8 브리지 패턴](ch08/)
- [CHAPTER 9 복합체 패턴](ch09/)
- [CHAPTER 10 장식자 패턴](ch10/)
- [CHAPTER 11 파사드 패턴](ch11/)
- [CHAPTER 12 플라이웨이트 패턴](ch12/)
- [CHAPTER 13 프록시 패턴](ch13/)

## PART 3 행동 패턴 (Behavioral Patterns)
- [CHAPTER 14 반복자 패턴](ch14/)
- [CHAPTER 15 명령 패턴](ch15/)
- [CHAPTER 16 방문자 패턴](ch16/)
- [CHAPTER 17 체인 패턴](ch17/)
- [CHAPTER 18 감시자 패턴](ch18/)
- [CHAPTER 19 중재자 패턴](ch19/)
- [CHAPTER 20 상태 패턴](ch20/)
- [CHAPTER 21 메멘토 패턴](ch21/)
- [CHAPTER 22 템플릿 메서드 패턴](ch22/)
- [CHAPTER 23 전략 패턴](ch23/)
- [CHAPTER 24 인터프리터 패턴](ch24/)
"""
    root_index_path = os.path.join(SRC_DIR, "index.md")
    with open(root_index_path, "w", encoding="utf-8") as f:
        f.write(index_content)
    print("Created root index: index.md")

if __name__ == "__main__":
    run_organization()
    print("Reorganization complete!")
