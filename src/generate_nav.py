import os
import re

# Paths
SRC_DIR = "/Users/hojin9/dev/jinysite/pattern/src"
DATA_DIR = os.path.join(SRC_DIR, "_data")

# Groups mappings
GROUPS = {
    "ch00": [0],
    "creational": list(range(1, 7)),
    "structural": list(range(7, 14)),
    "behavioral": list(range(14, 25))
}

# Mapping of chapter numbers to titles
CHAPTER_TITLES = {
    0: "디자인 패턴",
    1: "팩토리 패턴",
    2: "싱글턴 패턴",
    3: "팩토리 메서드 패턴",
    4: "추상 팩토리 패턴",
    5: "빌더 패턴",
    6: "프로토타입 패턴",
    7: "어댑터 패턴",
    8: "브리지 패턴",
    9: "복합체 패턴",
    10: "장식자 패턴",
    11: "파사드 패턴",
    12: "플라이웨이트 패턴",
    13: "프록시 패턴",
    14: "반복자 패턴",
    15: "명령 패턴",
    16: "방문자 패턴",
    17: "체인 패턴",
    18: "감시자 패턴",
    19: "중재자 패턴",
    20: "상태 패턴",
    21: "메멘토 패턴",
    22: "템플릿 메서드 패턴",
    23: "전략 패턴",
    24: "인터프리터 패턴",
}

def make_id(title):
    # kramdown header ID logic:
    # 1. Strip special chars except spaces, hyphens, alphanumeric, and Korean
    clean = re.sub(r'[^\w\s\-\uAC00-\uD7A3]', '', title)
    # 2. Replace spaces with hyphens
    clean = re.sub(r'\s+', '-', clean)
    # 3. Lowercase
    return clean.strip("-").lower()

def get_subitems(ch_num):
    filepath = os.path.join(SRC_DIR, f"ch{ch_num:02d}", "index.md")
    subitems = []
    if not os.path.exists(filepath):
        return subitems
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Find all lines starting with ##
    lines = content.split("\n")
    for line in lines:
        if line.startswith("## "):
            title = line[3:].strip()
            # Ignore headers that might be page metadata or not section headers
            if not title:
                continue
            anchor_id = make_id(title)
            subitems.append({
                "title": title,
                "url": f"/ch{ch_num:02d}/#{anchor_id}"
            })
    return subitems

def generate_navigation():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. Generate group files
    for group_name, ch_list in GROUPS.items():
        yaml_lines = []
        if group_name == "ch00":
            yaml_lines.append("- title: \"지은이 소개\"")
            yaml_lines.append("  url: \"/author.html\"")
            yaml_lines.append("- title: \"지은이의 말\"")
            yaml_lines.append("  url: \"/preface.html\"")
        elif group_name == "creational":
            yaml_lines.append("- title: \"Part 1 생성 패턴\"")
            yaml_lines.append("  url: \"/part01/\"")
        elif group_name == "structural":
            yaml_lines.append("- title: \"Part 2 구조 패턴\"")
            yaml_lines.append("  url: \"/part02/\"")
        elif group_name == "behavioral":
            yaml_lines.append("- title: \"Part 3 행동 패턴\"")
            yaml_lines.append("  url: \"/part03/\"")
            
        for ch_num in ch_list:
            ch_title = f"CHAPTER {ch_num} {CHAPTER_TITLES[ch_num]}"
            subitems = get_subitems(ch_num)
            
            yaml_lines.append(f"- title: \"{ch_title}\"")
            yaml_lines.append(f"  url: \"/ch{ch_num:02d}/\"")
            if subitems:
                yaml_lines.append("  subitems:")
                for subitem in subitems:
                    yaml_lines.append(f"    - title: \"{subitem['title']}\"")
                    yaml_lines.append(f"      url: \"{subitem['url']}\"")
            
        dest_path = os.path.join(DATA_DIR, f"{group_name}.yml")
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write("\n".join(yaml_lines) + "\n")
        print(f"Generated data file: {dest_path}")

    # 2. Generate header_nav.yml
    header_nav = [
        {"title": "패턴", "url": "/ch00/"},
        {"title": "생성패턴", "url": "/part01/"},
        {"title": "구조패턴", "url": "/part02/"},
        {"title": "행동패턴", "url": "/part03/"}
    ]
    
    header_yaml = []
    for item in header_nav:
        header_yaml.append(f"- title: \"{item['title']}\"")
        header_yaml.append(f"  url: \"{item['url']}\"")
        
    header_nav_path = os.path.join(DATA_DIR, "header_nav.yml")
    with open(header_nav_path, "w", encoding="utf-8") as f:
        f.write("\n".join(header_yaml) + "\n")
    print(f"Generated header_nav file: {header_nav_path}")

if __name__ == "__main__":
    generate_navigation()
