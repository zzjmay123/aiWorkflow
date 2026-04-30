# Self-Improving Agent for CoPaw

## ✅ 已完成设置

### 目录结构
```
~/self-improving/
├── memory.md          # HOT 记忆（已初始化）
├── index.md           # 索引（已创建）
├── corrections.md     # 纠正日志（已创建）
├── projects/          # 项目特定记忆
├── domains/           # 领域特定记忆
└── archive/           # 归档记忆
```

### 配置文件更新
- ✅ `AGENTS.md` - 添加自我改进记忆说明
- ✅ `SOUL.md` - 添加自我改进工作流
- ✅ `HEARTBEAT.md` - 添加定期维护检查

### 当前状态
```
📊 Self-Improving Memory

🔥 HOT (always loaded):
   memory.md: 21 lines

🌡️ WARM (load on demand):
   projects/: 0 files
   domains/: 0 files

❄️ COLD (archived):
   archive/: 0 files

⚙️ Mode: Passive
```

## 使用方法

### 1. 任务前读取记忆
```bash
# 读取 HOT 记忆
cat ~/self-improving/memory.md

# 列出可用领域/项目文件
for d in ~/self-improving/domains ~/self-improving/projects; do
  [ -d "$d" ] && find "$d" -maxdepth 1 -type f -name "*.md"
done | sort
```

### 2. 记录纠正
用户纠正时，立即追加到 `corrections.md`：
```markdown
## 2026-03-08
- [时间] 错误内容 → 正确内容
  Type: technical|format|communication|project
  Context: 纠正发生的场景
  Confirmed: pending (N/3) | yes | no
```

### 3. 自我反思
完成任务后，评估并记录：
```
CONTEXT: [任务类型]
REFLECTION: [发现的问题]
LESSON: [下次如何改进]
```

### 4. 查询记忆
```bash
# 查看所有模式
cat ~/self-improving/memory.md

# 查看最近的纠正
tail -20 ~/self-improving/corrections.md

# 查看统计
cat ~/self-improving/index.md
```

## CoPaw 集成说明

### 与 MEMORY.md 的区别
- `MEMORY.md` — 事实性记忆（事件、决策、上下文）
- `~/self-improving/` — 执行改进（偏好、工作流、模式）

### 何时使用
| 内容类型 | 存储位置 |
|---------|---------|
| 用户纠正 | `corrections.md` → `memory.md` |
| 工作偏好 | `memory.md` |
| 项目教训 | `projects/<project>.md` |
| 领域知识 | `domains/<domain>.md` |
| 事件记录 | `memory/YYYY-MM-DD.md` |
| 长期记忆 | `MEMORY.md` |

## 维护

### 定期清理（Heartbeat）
- [ ] 检查 corrections.md 是否有可提升的模式
- [ ] 检查 memory.md 行数（应 ≤100）
- [ ] 归档 >90 天未使用的模式

### 升级规则
- 7 天内使用 3 次 → 晋升 HOT
- 30 天未使用 → 降级 WARM
- 90 天未使用 → 归档 COLD

## 示例

### 记录用户纠正
用户说："不对，飞书配置在 `~/.copaw/config.json`，不是 `~/.openclaw/openclaw.json`"

→ 追加到 `corrections.md`：
```markdown
## 2026-03-08
- [11:00] Feishu File Sender 技能配置路径错误
  Type: technical
  Context: 技能从 `~/.openclaw/openclaw.json` 读取配置，但 CoPaw 配置在 `~/.copaw/config.json`
  Confirmed: yes
  Lesson: CoPaw 的技能需要适配 `~/.copaw/config.json` 配置路径
```

### 记录工作偏好
用户说："输出简洁点，不要显示中间步骤"

→ 追加到 `memory.md` 的 "Confirmed Preferences" 部分：
```markdown
- 输出简洁：只显示最终结论，不显示中间步骤
```

---

**版本：** v1.2.10 (CoPaw 适配)
**设置日期：** 2026-03-08
