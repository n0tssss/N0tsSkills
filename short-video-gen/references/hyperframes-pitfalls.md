# HyperFrames 常见错误及修复

## 渲染错误

### 1. `window.__hf not ready after 45000ms`
**原因**：没有正确暴露 `window.__hf` 对象
**修复**：在script中添加：
```javascript
window.__hf = {
  duration: 40,  // 总时长（秒）
  seek: function(time) {
    tl.seek(time);
  }
};
```

### 2. `Private field '#title' must be declared`
**原因**：JavaScript选择器用了私有字段语法
**修复**：选择器必须加引号
```javascript
// 错误
gsap.fromTo(#title, {...}, {...});

// 正确
gsap.fromTo('#title', {...}, {...});
```

### 3. `gsap_infinite_repeat`
**原因**：GSAP动画使用了 `repeat: -1`（无限循环）
**修复**：改为有限次数
```javascript
// 错误
gsap.to('#el', {textShadow: '...', repeat: -1});

// 正确
gsap.to('#el', {textShadow: '...', repeat: 2});
```

### 4. `root_missing_dimensions`
**原因**：根元素缺少 `data-width` 和 `data-height`
**修复**：在根div上添加属性
```html
<div id="composition" data-composition-id="my-video" 
     data-width="1080" data-height="1920" data-start="0">
```

### 5. `missing_timeline_registry`
**原因**：没有注册 `window.__timelines`
**修复**：
```javascript
window.__timelines = window.__timelines || {};
window.__timelines["my-video"] = tl;
```

### 6. `timeline_id_mismatch`
**原因**：注册的timeline ID和data-composition-id不匹配
**修复**：确保两者一致
```javascript
// data-composition-id="hermes-intro"
window.__timelines["hermes-intro"] = tl;
```

## HTML结构要求

### 根元素必须包含
```html
<div id="composition" 
     class="container" 
     data-composition-id="project-name"
     data-width="1080" 
     data-height="1920"
     data-start="0">
```

### 场景元素
```html
<div id="scene-1" class="scene" style="opacity: 0;">
  <!-- 元素 -->
</div>
```

### 音频元素（如果有）
```html
<audio id="bgm" 
       src="voiceover.wav" 
       data-start="0" 
       data-duration="40" 
       data-track-index="0" 
       data-volume="1">
</audio>
```

## GSAP动画限制

### 禁止使用
- `repeat: -1`（无限循环）
- 复杂的CSS选择器（如 `:nth-child`）
- 动态计算的属性名

### 推荐模式
```javascript
const tl = gsap.timeline({ paused: true });

// 入场动画
tl.add(() => { 
  gsap.fromTo('#title', 
    {opacity: 0, y: 50}, 
    {opacity: 1, y: 0, duration: 0.5, ease: 'power2.out'}
  ); 
}, startTime);

// 强调动画
tl.add(() => { 
  gsap.to('#title', 
    {scale: 1.1, duration: 0.3, yoyo: true, repeat: 1}
  ); 
}, startTime + 0.5);

// 退场动画
tl.add(() => { 
  gsap.to('#title', 
    {opacity: 0, duration: 0.3}
  ); 
}, endTime - 0.3);
```
