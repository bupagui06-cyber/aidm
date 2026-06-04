import streamlit as st
import json
import os
import re
from openai import OpenAI
from logic import GameState
from dotenv import load_dotenv
from voice_input import voice_input

# 从环境变量读取API配置（支持Streamlit Cloud Secrets）
load_dotenv()  # 加载本地.env文件（开发环境）

LLM_API_KEY = os.getenv('LLM_API_KEY', '')
BASE_URL = os.getenv('BASE_URL', 'https://api.deepseek.com/v1')
MODEL_NAME = os.getenv('MODEL_NAME', 'deepseek-chat')

# 打印调试信息
if LLM_API_KEY:
    print(f"LLM_API_KEY: {LLM_API_KEY[:10]}...")
else:
    print("LLM_API_KEY not configured")
print(f"BASE_URL: {BASE_URL}")
print(f"MODEL_NAME: {MODEL_NAME}")

# 游戏阶段定义
GAME_PHASES = {
    1: "搜证",
    2: "诡计",
    3: "质证",
    4: "复盘"
}

# 初始化会话状态
def init_session_state():
    """初始化游戏状态"""
    if 'game_state' not in st.session_state:
        st.session_state.game_state = GameState()
        print("初始化新的游戏状态")
    else:
        print("使用已存在的游戏状态")
    
    roles = st.session_state.game_state.get_all_roles()
    print(f"角色数量: {len(roles)}")
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'selected_role' not in st.session_state:
        st.session_state.selected_role = None
    if 'welcome_message_sent' not in st.session_state:
        st.session_state.welcome_message_sent = False
    if 'last_stage' not in st.session_state:
        st.session_state.last_stage = 1
    
    # 状态一致性检查：如果没有选择角色，重置到第一阶段
    if not st.session_state.selected_role and st.session_state.game_state.current_stage > 1:
        print("状态不一致：没有选择角色但阶段>1，重置阶段")
        st.session_state.game_state.current_stage = 1
        st.session_state.game_state.ap_points = 10
        st.session_state.game_state.unlocked_clues = []

# 检查是否触发搜证条件
def check_search_trigger(user_input):
    """检查用户输入是否触发搜证条件"""
    search_keywords = ['搜查', '搜索', '查看', '检查', '调查', '线索', '证据', '现场', '断口', '碎片', '样本', '搜证', '寻找']
    return any(keyword in user_input for keyword in search_keywords)

# 生成AI回复（流式）
def generate_ai_response(user_input, selected_role_id):
    """调用LLM生成回复（流式）"""
    if not LLM_API_KEY:
        error_message = "请先配置LLM_API_KEY环境变量"
        yield error_message
        return error_message
    
    try:
        client = OpenAI(
            api_key=LLM_API_KEY,
            base_url=BASE_URL
        )
        
        # 构建系统提示
        try:
            import os
            prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'system_prompt.txt')
            with open(prompt_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
        except Exception as e:
            print(f"加载系统提示失败: {e}")
            system_prompt = "你是零号监理，性格冷酷、客观，严格遵守物理定律。"
        
        # 获取角色提示
        character_hint = st.session_state.game_state.get_character_hint(
            selected_role_id, 
            st.session_state.game_state.current_stage
        )
        
        # 获取角色信息
        role_info = st.session_state.game_state.get_role_by_id(selected_role_id)
        role_name = role_info.get('name', '玩家') if role_info else '玩家'
        
        # 添加角色称呼信息
        system_prompt += f"\n\n当前玩家角色：{role_name}"
        
        # 如果有角色提示，添加到系统提示中
        if character_hint:
            system_prompt += f"\n\n当前玩家角色提示：{character_hint}"
        
        # 添加当前游戏阶段信息
        current_stage = st.session_state.game_state.current_stage
        stage_name = GAME_PHASES.get(current_stage, "未知阶段")
        system_prompt += f"\n\n当前游戏阶段：第{current_stage}阶段 - {stage_name}"
        
        # 为每个阶段添加具体任务说明
        stage_tasks = {
            1: "【当前阶段任务】搜证阶段：请引导玩家搜索现场线索，收集物理证据。不要透露凶手身份。",
            2: "【当前阶段任务】诡计阶段：请引导玩家分析液氮冷脆等物理诡计，解释科学原理。不要说出凶手。",
            3: "【当前阶段任务】质证阶段：请引导玩家对峙嫌疑人，聚焦证据链，要求投票指认凶手。",
            4: "【当前阶段任务】复盘阶段：请揭示完整真相，凶手是赵泰，解释物理原理。"
        }
        system_prompt += f"\n\n{stage_tasks.get(current_stage, '')}"
        
        # 添加称呼指令
        system_prompt += f"\n\n指令：请直接称呼玩家为'{role_name}'，不要让玩家再告诉你他是谁。"
        
        # 第四阶段添加真相
        if current_stage == 4:
            truth = st.session_state.game_state.get_truth()
            if truth:
                system_prompt += f"\n\n上帝视角真相：{truth}"
        
        # 构建对话历史
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # 流式生成回复
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=5000,
            stream=True
        )
        
        # 流式输出
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                yield full_response
        
        return full_response
    except Exception as e:
        error_message = f"AI调用失败: {e}"
        yield error_message
        return error_message

# 主应用函数
def main():
    """主应用函数"""
    # 初始化会话状态
    init_session_state()
    
    # 设置页面标题
    st.set_page_config(page_title="桩基础谜案 - AI DM", layout="wide")
    
    # 页面标题
    st.title("桩基础谜案 - AI DM")
    
    # 侧边栏
    with st.sidebar:
        st.header("游戏状态")
        
        # 当前阶段
        st.subheader("当前阶段")
        st.write(f"{st.session_state.game_state.current_stage}. {GAME_PHASES[st.session_state.game_state.current_stage]}")
        
        # AP点数
        st.subheader("剩余AP点数")
        st.write(st.session_state.game_state.ap_points)
        
        # 推进阶段按钮
        if st.button("推进至下一阶段"):
            st.session_state.game_state.next_stage()
            current_stage = st.session_state.game_state.current_stage
            stage_name = GAME_PHASES[current_stage]
            
            # 获取阶段开场台词
            stage_opening = st.session_state.game_state.get_stage_opening(current_stage)
            
            # 添加AI消息到聊天历史
            if stage_opening:
                st.session_state.messages.append({"role": "assistant", "content": stage_opening})
            
            st.success(f"已进入{stage_name}阶段")
            # 刷新页面
            st.rerun()
        
        # 线索背包
        st.subheader("线索背包")
        with st.expander("已解锁线索"):
            if st.session_state.game_state.unlocked_clues:
                for clue in st.session_state.game_state.unlocked_clues:
                    st.markdown(f"**{clue['name']}**")
                    st.write(f"ID: {clue['id']}")
                    st.write(f"描述: {clue['description']}")
                    st.write(f"AP消耗: {clue['ap_cost']}")
                    st.divider()
            else:
                st.write("暂无解锁的线索")
    
    # 主界面 - 角色选择
    if not st.session_state.selected_role:
        st.header("角色选择")
        roles = st.session_state.game_state.get_all_roles()
        
        # 角色卡片布局
        cols = st.columns(2)
        for i, role in enumerate(roles):
            with cols[i % 2]:
                # 创建角色卡片容器
                with st.container(border=True):
                    # 角色照片和信息并排显示
                    photo_col, info_col = st.columns([1, 2], gap="small")
                    with photo_col:
                        # 显示角色照片
                        if 'photo' in role:
                            try:
                                # 使用use_container_width让图片自适应容器宽度，确保清晰显示
                                st.image(role['photo'], use_container_width=True, caption=role['name'], output_format="PNG")
                            except:
                                # 如果照片不存在，显示占位图
                                st.markdown(f"### 👤")
                                st.caption(role['name'])
                        else:
                            st.markdown(f"### 👤")
                            st.caption(role['name'])
                    with info_col:
                        st.markdown(f"### {role['name']}")
                        st.write(f"**职业:** {role['profession']}")
                        st.write(f"**年龄:** {role['age']}")
                # 显示角色描述
                st.write(f"**描述:** {role['description']}")
                # 选择按钮
                if st.button(f"选择 {role['name']}", key=role['id']):
                    st.session_state.selected_role = role['id']
                    st.session_state.welcome_message_sent = False
                    # 刷新页面
                    st.rerun()
    else:
        # 主界面 - 聊天室
        st.header("对话区")
        
        # 显示聊天记录
        for msg in st.session_state.messages:
            if msg['role'] == 'user':
                with st.chat_message("user"):
                    st.write(msg['content'])
            else:
                with st.chat_message("assistant"):
                    st.write(msg['content'])
        
        # 发送欢迎语
        if not st.session_state.welcome_message_sent:
            welcome_message = "欢迎来到《桩基础谜案》。我是零号监理，将全程引导你完成这次推理。根据你的角色，你需要查明严成坠海的真相。现在开始你的推理吧。"
            st.session_state.messages.append({"role": "assistant", "content": welcome_message})
            st.session_state.welcome_message_sent = True
            with st.chat_message("assistant"):
                st.write(welcome_message)
        
        # 语音输入
        st.subheader("语音输入")
        voice_text = voice_input()
        
        # 文本输入
        user_input = st.chat_input("请输入你的推理或行动...")
        
        # 处理输入
        final_input = user_input or voice_text
        
        if final_input:
            # 添加用户输入到聊天历史
            st.session_state.messages.append({"role": "user", "content": final_input})
            
            # 显示用户输入
            with st.chat_message("user"):
                st.write(final_input)
            
            # 检查是否触发搜证
            if check_search_trigger(final_input) and st.session_state.game_state.current_stage == 1:
                clue = st.session_state.game_state.unlock_clue(final_input)
                if isinstance(clue, dict):
                    # 生成包含线索的回复
                    ai_response = f"你发现了新线索：\n\n**{clue['name']}**\nID: {clue['id']}\n描述: {clue['description']}\n\n消耗了 {clue['ap_cost']} 点AP。"
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    with st.chat_message("assistant"):
                        st.write(ai_response)
                    # 刷新页面，更新线索背包
                    st.rerun()
                else:
                    # 显示系统提示
                    st.session_state.messages.append({"role": "assistant", "content": clue})
                    with st.chat_message("assistant"):
                        st.write(clue)
            else:
                # 调用AI生成回复（流式）
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    full_response = ""
                    for chunk in generate_ai_response(final_input, st.session_state.selected_role):
                        full_response = chunk
                        response_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
