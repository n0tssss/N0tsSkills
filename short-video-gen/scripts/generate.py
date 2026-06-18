#!/usr/bin/env python3
"""
HyperFrames HTML Generator
根据JSON配置生成HyperFrames兼容的HTML文件
"""

import json
import sys
import os

# 动画定义
ANIMATIONS = {
    # 入场动画
    "fadeIn": "gsap.fromTo(el, {opacity: 0}, {opacity: 1, duration: {duration}, ease: 'power2.out'})",
    "slideInLeft": "gsap.fromTo(el, {x: -100, opacity: 0}, {x: 0, opacity: 1, duration: {duration}, ease: 'power2.out'})",
    "slideInRight": "gsap.fromTo(el, {x: 100, opacity: 0}, {x: 0, opacity: 1, duration: {duration}, ease: 'power2.out'})",
    "slideInUp": "gsap.fromTo(el, {y: 50, opacity: 0}, {y: 0, opacity: 1, duration: {duration}, ease: 'power2.out'})",
    "scaleIn": "gsap.fromTo(el, {scale: 0.8, opacity: 0}, {scale: 1, opacity: 1, duration: {duration}, ease: 'back.out(1.7)'})",
    "blurIn": "gsap.fromTo(el, {filter: 'blur(10px)', opacity: 0}, {filter: 'blur(0px)', opacity: 1, duration: {duration}, ease: 'power2.out'})",
    
    # 强调动画
    "pulse": "gsap.to(el, {scale: 1.1, duration: {duration}/2, yoyo: true, repeat: 1, ease: 'power2.inOut'})",
    "shake": "gsap.to(el, {x: 5, duration: 0.1, yoyo: true, repeat: 5, ease: 'power2.inOut'})",
    "glow": "gsap.to(el, {textShadow: '0 0 20px #00d4ff', duration: {duration}, yoyo: true, repeat: -1})",
    "bounce": "gsap.fromTo(el, {y: 0}, {y: -20, duration: {duration}/2, yoyo: true, repeat: 1, ease: 'bounce.out'})",
    
    # 退场动画
    "fadeOut": "gsap.to(el, {opacity: 0, duration: {duration}, ease: 'power2.in'})",
    "slideOutLeft": "gsap.to(el, {x: -100, opacity: 0, duration: {duration}, ease: 'power2.in'})",
    "slideOutRight": "gsap.to(el, {x: 100, opacity: 0, duration: {duration}, ease: 'power2.in'})",
    "scaleOut": "gsap.to(el, {scale: 0.8, opacity: 0, duration: {duration}, ease: 'power2.in'})",
    "blurOut": "gsap.to(el, {filter: 'blur(10px)', opacity: 0, duration: {duration}, ease: 'power2.in'})",
}

def generate_element_html(element, scene_start):
    """生成单个元素的HTML"""
    el_id = element.get("id", "element")
    el_type = element.get("type", "text")
    content = element.get("content", "")
    position = element.get("position", {"x": "center", "y": "center"})
    style = element.get("style", {})
    
    # 构建CSS样式
    css_styles = []
    if "fontSize" in style:
        css_styles.append(f"font-size: {style['fontSize']}px")
    if "fontWeight" in style:
        css_styles.append(f"font-weight: {style['fontWeight']}")
    if "color" in style:
        css_styles.append(f"color: {style['color']}")
    if "textAlign" in style:
        css_styles.append(f"text-align: {style['textAlign']}")
    if "lineHeight" in style:
        css_styles.append(f"line-height: {style['lineHeight']}")
    
    style_str = "; ".join(css_styles) if css_styles else ""
    
    # 位置样式
    position_css = []
    if position.get("x") == "center":
        position_css.append("left: 50%")
        position_css.append("transform: translateX(-50%)")
    elif position.get("x") == "left":
        position_css.append("left: 60px")
    elif position.get("x") == "right":
        position_css.append("right: 60px")
        
    if position.get("y") == "center":
        position_css.append("top: 50%")
        position_css.append("transform: translateY(-50%)")
    elif position.get("y") == "top":
        position_css.append("top: 100px")
    elif position.get("y") == "bottom":
        position_css.append("bottom: 100px")
    
    position_str = "; ".join(position_css) if position_css else ""
    
    # 生成HTML
    if el_type == "text":
        return f'<div id="{el_id}" class="element" style="position: absolute; {position_str}; {style_str}; opacity: 0;">{content}</div>'
    elif el_type == "image":
        src = element.get("src", "")
        return f'<img id="{el_id}" class="element" src="{src}" style="position: absolute; {position_str}; max-width: 80%; {style_str}; opacity: 0;" />'
    else:
        return f'<div id="{el_id}" class="element" style="position: absolute; {position_str}; {style_str}; opacity: 0;">{content}</div>'

def generate_scene_html(scene):
    """生成场景的HTML"""
    scene_id = scene.get("id", "scene")
    background = scene.get("background", "#0a0a0a")
    elements = scene.get("elements", [])
    
    elements_html = "\n".join([generate_element_html(el, scene.get("start", 0)) for el in elements])
    
    return f'''
    <div id="{scene_id}" class="scene" style="position: absolute; width: 100%; height: 100%; background: {background}; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 60px; opacity: 0;">
      {elements_html}
    </div>'''

def generate_animation_js(scenes, total_duration):
    """生成GSAP动画JavaScript"""
    js_lines = []
    js_lines.append("const tl = gsap.timeline({ paused: true });")
    js_lines.append("")
    
    for i, scene in enumerate(scenes):
        scene_id = scene.get("id", f"scene-{i+1}")
        start = scene.get("start", 0)
        duration = scene.get("duration", 4)
        elements = scene.get("elements", [])
        
        # 场景入场
        js_lines.append(f"// 场景 {i+1}: {scene.get('name', '')}")
        js_lines.append(f"tl.to('#{scene_id}', {{ opacity: 1, duration: 0.3 }}, {start});")
        
        # 元素动画
        for el in elements:
            el_id = el.get("id", "element")
            animation = el.get("animation", {})
            
            # 入场动画
            enter_anim = animation.get("enter", {})
            if enter_anim:
                anim_type = enter_anim.get("type", "fadeIn")
                anim_duration = enter_anim.get("duration", 0.5)
                anim_start = start + enter_anim.get("delay", 0)
                
                if anim_type in ANIMATIONS:
                    anim_code = ANIMATIONS[anim_type].replace("{selector}", f"#{el_id}").replace("{duration}", str(anim_duration))
                    js_lines.append(f"tl.add(() => {{ {anim_code} }}, {anim_start});")
            
            # 强调动画
            emphasis_anim = animation.get("emphasis", {})
            if emphasis_anim:
                anim_type = emphasis_anim.get("type", "pulse")
                anim_duration = emphasis_anim.get("duration", 0.5)
                anim_start = start + emphasis_anim.get("delay", 0.5)
                
                if anim_type in ANIMATIONS:
                    anim_code = ANIMATIONS[anim_type].replace("{selector}", f"#{el_id}").replace("{duration}", str(anim_duration))
                    js_lines.append(f"tl.add(() => {{ {anim_code} }}, {anim_start});")
            
            # 退场动画
            exit_anim = animation.get("exit", {})
            if exit_anim:
                anim_type = exit_anim.get("type", "fadeOut")
                anim_duration = exit_anim.get("duration", 0.3)
                anim_start = start + duration - anim_duration
                
                if anim_type in ANIMATIONS:
                    anim_code = ANIMATIONS[anim_type].replace("{selector}", f"#{el_id}").replace("{duration}", str(anim_duration))
                    js_lines.append(f"tl.add(() => {{ {anim_code} }}, {anim_start});")
        
        # 场景退场
        js_lines.append(f"tl.to('#{scene_id}', {{ opacity: 0, duration: 0.3 }}, {start + duration - 0.3});")
        js_lines.append("")
    
    return "\n".join(js_lines)

def generate_html(spec):
    """根据JSON配置生成完整HTML"""
    project = spec.get("project", {})
    style = spec.get("style", {})
    scenes = spec.get("scenes", [])
    audio = spec.get("audio", {})
    
    width = project.get("width", 1080)
    height = project.get("height", 1920)
    duration = project.get("duration", 40)
    
    colors = style.get("colors", {})
    font = style.get("font", {})
    
    # 生成场景HTML
    scenes_html = "\n".join([generate_scene_html(scene) for scene in scenes])
    
    # 生成动画JS
    animation_js = generate_animation_js(scenes, duration)
    
    # 生成音频元素（如果有）
    audio_html = ""
    if audio.get("enabled", False):
        audio_file = audio.get("file", "voiceover.wav")
        audio_html = f'<audio id="bgm" src="{audio_file}" data-start="0" data-duration="{duration}" data-track-index="0" data-volume="1"></audio>'
    
    # 生成完整HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{project.get("name", "video")}</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}
    
    body {{
      background: {colors.get("background", "#0a0a0a")};
      color: white;
      font-family: {font.get("main", "system-ui")}, sans-serif;
      overflow: hidden;
    }}
    
    .container {{
      width: {width}px;
      height: {height}px;
      position: relative;
      overflow: hidden;
    }}
    
    .scene {{
      position: absolute;
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 60px;
      opacity: 0;
    }}
    
    .element {{
      position: absolute;
    }}
  </style>
</head>
<body>
  <div id="composition" class="container" data-composition-id="{project.get("name", "video")}" data-width="{width}" data-height="{height}" data-start="0">
    {scenes_html}
    {audio_html}
  </div>
  
  <script>
    document.addEventListener('DOMContentLoaded', function() {{
      {animation_js}
      
      // 注册timeline
      window.__timelines = window.__timelines || {{}};
      window.__timelines["{project.get("name", "video")}"] = tl;
      
      // 暴露__hf
      window.__hf = {{
        duration: {duration},
        seek: function(time) {{
          tl.seek(time);
        }}
      }};
      
      console.log('HyperFrames ready');
    }});
  </script>
</body>
</html>'''
    
    return html

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate.py <spec.json> [output.html]")
        sys.exit(1)
    
    spec_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "index.html"
    
    # 读取JSON配置
    with open(spec_file, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    
    # 生成HTML
    html = generate_html(spec)
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Generated: {output_file}")
    print(f"Project: {spec.get('project', {}).get('name', 'unknown')}")
    print(f"Duration: {spec.get('project', {}).get('duration', 0)}s")
    print(f"Scenes: {len(spec.get('scenes', []))}")

if __name__ == "__main__":
    main()
