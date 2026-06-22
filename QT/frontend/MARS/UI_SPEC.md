# MARS AI Agent — UI 规范说明

## 设计语言
Apple Design Language (macOS Sequoia / iOS 18 风格)

## 色彩系统

### 主色 (Accent)
| Token | 值 | 用途 |
|-------|-----|------|
| accentColor | #AF52DE | 主色（按钮、选中态、用户气泡） |
| accentLight | #C77BFF | 悬停态 |
| accentDark | #8944AB | 按下态 |
| accentTint | rgba(175,82,222,0.12) | 选中背景 |

### 亮色模式
| Token | 值 | 用途 |
|-------|-----|------|
| bgColor | #F2F2F7 | 页面背景 (systemGroupedBackground) |
| cardColor | #FFFFFF | 卡片背景 |
| textColor | #1C1C1E | 主文本 (label) |
| secondaryText | #8E8E93 | 次文本 (secondaryLabel) |
| separatorColor | rgba(60,60,67,0.12) | 分割线 |
| inputBg | #F2F2F7 | 输入框背景 |

### 暗色模式
| Token | 值 | 用途 |
|-------|-----|------|
| bgColor | #000000 | 页面背景 (true black, OLED) |
| cardColor | #1C1C1E | 卡片背景 |
| textColor | #FFFFFF | 主文本 |
| secondaryText | #98989F | 次文本 |
| separatorColor | rgba(84,84,88,0.36) | 分割线 |
| inputBg | #1C1C1E | 输入框背景 |

### 系统状态色
| Token | 值 | Apple 系统色名 |
|-------|-----|----------------|
| infoBg | #007AFF | Blue |
| successBg | #34C759 | Green |
| warningBg | #FF9F0A | Orange |
| errorBg | #FF3B30 | Red |

## 字体

### 优先级链
SF Pro Display → Segoe UI Variable → Segoe UI

### 字号阶梯
| Token | 值 | 用途 |
|-------|-----|------|
| fontSizeCaption | 11px | 辅助文字、标签 |
| fontSizeBody | 13px | 正文 |
| fontSizeHeadline | 15px | 卡片标题 |
| fontSizeTitle | 17px | 页面标题 |
| fontSizeTitle2 | 20px | 二级标题 |
| fontSizeLargeTitle | 28px | 大标题 |

### 字重
| Token | 值 |
|-------|-----|
| fontWeightRegular | Font.Normal (400) |
| fontWeightMedium | Font.Medium (500) |
| fontWeightSemibold | Font.DemiBold (600) |

## 间距 (4pt 网格)

| Token | 值 |
|-------|-----|
| spacing1 | 4px |
| spacing2 | 8px |
| spacing3 | 12px |
| spacing4 | 16px |
| spacing5 | 20px |
| spacing6 | 24px |
| spacing7 | 32px |
| spacing8 | 48px |

## 圆角

| Token | 值 | 用途 |
|-------|-----|------|
| cornerRadiusXs | 4px | 小标签 |
| cornerRadiusSm | 6px | 按钮 |
| cornerRadiusMd | 10px | 卡片、容器 |
| cornerRadiusLg | 14px | 信息条 |
| cornerRadiusXl | 18px | 消息气泡 |

## 阴影

| 模式 | 颜色 | Y偏移 | 用途 |
|------|------|--------|------|
| 亮色 | rgba(0,0,0,0.03) | 2px | 卡片阴影 |
| 暗色 | rgba(0,0,0,0.2) | 1px | 卡片阴影 |

## 动效

| 类型 | 时长 | 缓动 |
|------|------|------|
| 颜色过渡 | 150ms | ColorAnimation |
| 尺寸过渡 | 300ms | Easing.OutCubic |
| 消息入场 | 300ms | Easing.OutQuart |
| 按压弹簧 | - | SpringAnimation (spring:4, damping:0.4) |
| Toggle滑块 | - | SpringAnimation (spring:5, damping:0.5) |

## 组件规范

### 按钮高度
| 类型 | 高度 |
|------|------|
| 标准按钮 | 36px |
| 小按钮 | 28px |

### 导航栏
| 属性 | 值 |
|------|-----|
| 宽度 | 72px |
| 选中态圆角 | 10px |
| 图标大小 | 22px |
| 标签字号 | 10px |

### 消息气泡
| 属性 | 值 |
|------|-----|
| 圆角 | 18px |
| 尖角 | 4px (对角) |
| 最大宽度 | 75% 父容器 |
| 内边距 | 16px |
| 行高 | 1.45 |

### 输入栏
| 属性 | 值 |
|------|-----|
| 高度 | 64px |
| 容器圆角 | 16px |
| 发送按钮 | 36px 圆形 |
| 发送按钮圆角 | 18px |

### Toggle 开关
| 属性 | 值 |
|------|-----|
| 宽度 | 36px |
| 高度 | 22px |
| 圆角 | 11px |
| 滑块 | 18px 圆形 |
| 开启色 | accentColor |
| 关闭色(暗) | #39393C |
| 关闭色(亮) | #E9E9EA |
