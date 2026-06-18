# GSAP动画模式库

## 入场动画

### fadeIn（淡入）
```javascript
gsap.fromTo('#el', {opacity: 0}, {opacity: 1, duration: 0.5, ease: 'power2.out'});
```

### slideInLeft（从左滑入）
```javascript
gsap.fromTo('#el', {x: -100, opacity: 0}, {x: 0, opacity: 1, duration: 0.6, ease: 'power2.out'});
```

### slideInRight（从右滑入）
```javascript
gsap.fromTo('#el', {x: 100, opacity: 0}, {x: 0, opacity: 1, duration: 0.6, ease: 'power2.out'});
```

### slideInUp（从下滑入）
```javascript
gsap.fromTo('#el', {y: 50, opacity: 0}, {y: 0, opacity: 1, duration: 0.5, ease: 'power2.out'});
```

### scaleIn（缩放进入）
```javascript
gsap.fromTo('#el', {scale: 0.8, opacity: 0}, {scale: 1, opacity: 1, duration: 0.6, ease: 'back.out(1.7)'});
```

### blurIn（模糊进入）
```javascript
gsap.fromTo('#el', {filter: 'blur(10px)', opacity: 0}, {filter: 'blur(0px)', opacity: 1, duration: 0.7, ease: 'power2.out'});
```

### typewriter（打字机效果）
```javascript
// 需要逐字显示的实现
const text = '#el';
gsap.fromTo(text, {clipPath: 'inset(0 100% 0 0)'}, {clipPath: 'inset(0 0% 0 0)', duration: 1, ease: 'none'});
```

## 强调动画

### pulse（脉冲缩放）
```javascript
gsap.to('#el', {scale: 1.1, duration: 0.3, yoyo: true, repeat: 1, ease: 'power2.inOut'});
```

### shake（抖动）
```javascript
gsap.to('#el', {x: 5, duration: 0.1, yoyo: true, repeat: 5, ease: 'power2.inOut'});
```

### glow（发光）
```javascript
gsap.to('#el', {textShadow: '0 0 20px #00d4ff', duration: 0.5, yoyo: true, repeat: 2});
```

### bounce（弹跳）
```javascript
gsap.fromTo('#el', {y: 0}, {y: -20, duration: 0.3, yoyo: true, repeat: 1, ease: 'bounce.out'});
```

### colorShift（颜色变换）
```javascript
gsap.to('#el', {color: '#00d4ff', duration: 0.5, yoyo: true, repeat: 1});
```

## 退场动画

### fadeOut（淡出）
```javascript
gsap.to('#el', {opacity: 0, duration: 0.3, ease: 'power2.in'});
```

### slideOutLeft（向左滑出）
```javascript
gsap.to('#el', {x: -100, opacity: 0, duration: 0.4, ease: 'power2.in'});
```

### slideOutRight（向右滑出）
```javascript
gsap.to('#el', {x: 100, opacity: 0, duration: 0.4, ease: 'power2.in'});
```

### scaleOut（缩放退出）
```javascript
gsap.to('#el', {scale: 0.8, opacity: 0, duration: 0.4, ease: 'power2.in'});
```

### blurOut（模糊退出）
```javascript
gsap.to('#el', {filter: 'blur(10px)', opacity: 0, duration: 0.4, ease: 'power2.in'});
```

## 组合动画模式

### 场景完整流程
```javascript
const tl = gsap.timeline({ paused: true });

// 场景入场
tl.to('#scene-1', {opacity: 1, duration: 0.3}, 0);

// 元素动画
tl.add(() => { gsap.fromTo('#title', {y: 50, opacity: 0}, {y: 0, opacity: 1, duration: 0.6}) }, 0.2);
tl.add(() => { gsap.fromTo('#subtitle', {y: 30, opacity: 0}, {y: 0, opacity: 1, duration: 0.5}) }, 0.5);

// 强调
tl.add(() => { gsap.to('#title', {scale: 1.1, duration: 0.3, yoyo: true, repeat: 1}) }, 1.5);

// 退场
tl.add(() => { gsap.to('#title', {opacity: 0, duration: 0.3}) }, 3.5);
tl.add(() => { gsap.to('#subtitle', {opacity: 0, duration: 0.3}) }, 3.7);

// 场景退场
tl.to('#scene-1', {opacity: 0, duration: 0.3}, 3.8);
```

## 时间轴控制

### 基本方法
```javascript
tl.seek(5);      // 跳转到5秒
tl.play();       // 播放
tl.pause();      // 暂停
tl.progress(0.5); // 跳转到50%
```

### 相对时间
```javascript
tl.add(() => {...}, '+=0.5');  // 相对上一个动画结束后0.5秒
tl.add(() => {...}, '-=0.3');  // 相对上一个动画结束前0.3秒
```

## 缓动函数参考

### 常用缓动
- `power1.out` - 慢速开始，快速结束
- `power2.out` - 中等速度变化
- `power2.inOut` - 先慢后快再慢
- `back.out(1.7)` - 回弹效果
- `bounce.out` - 弹跳效果
- `elastic.out(1, 0.3)` - 弹性效果

### 查看所有缓动
https://greensock.com/docs/v3/Eases
