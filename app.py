import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
import logic

# 配置API
load_dotenv()
LLM_API_KEY = os.getenv('LLM_API_KEY', 'sk-45033f83643042199b4f0bc3c77a00de')
BASE_URL = os.getenv('BASE_URL', 'https://api.deepseek.com/v1')
MODEL_NAME = os.getenv('MODEL_NAME', 'deepseek-chat')

client = OpenAI(api_key=LLM_API_KEY, base_url=BASE_URL)

# 游戏阶段定义
GAME_PHASES = {
    1: "搜证",
    2: "诡计",
    3: "质证",
    4: "复盘"
}

def init_session_state():
    """初始化会话状态"""
    if 'game_state' not in st.session_state:
        st.session_state.game_state = logic.GameState()
        print("初始化新的游戏状态")
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'selected_role' not in st.session_state:
        st.session_state.selected_role = None
    
    if 'welcome_message_sent' not in st.session_state:
        st.session_state.welcome_message_sent = False

def load_system_prompt():
    """加载系统提示"""
    try:
        with open('data/system_prompt.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"加载系统提示失败: {e}")
        return "你是剧本杀《桩基础谜案》的智能主持人（DM），身份是'零号监理'。性格冷酷、客观、尊重物理规律。"

def generate_ai_response(prompt, character_id):
    """生成AI回复"""
    system_prompt = load_system_prompt()
    game_state = st.session_state.game_state
    current_stage = game_state.current_stage
    
    character_hint = game_state.get_character_hint(character_id, current_stage)
    stage_opening = game_state.get_stage_opening(current_stage)
    
    messages = [
        {"role": "system", "content": f"{system_prompt}\n\n【当前阶段】：第{current_stage}阶段 - {GAME_PHASES[current_stage]}\n【角色提示】：{character_hint}"},
        *[{"role": msg['role'], "content": msg['content']} for msg in st.session_state.messages],
        {"role": "user", "content": prompt}
    ]
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.7,
        max_tokens=5000,
        stream=True
    )
    
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            full_response += chunk.choices[0].delta.content
            yield full_response

def check_search_trigger(prompt):
    """检查是否触发搜证"""
    keywords = ['搜查', '搜索', '查看', '检查', '调查', '线索', '证据', '现场', '断口', '碎片', '样本', '监控', '泥浆', '液氮', '磨光机', '记录', '报告', '转账', '举报信']
    return any(keyword in prompt for keyword in keywords)

def main():
    """主应用函数"""
    init_session_state()
    
    st.set_page_config(page_title="桩基础谜案 - AI DM", layout="wide")
    st.title("桩基础谜案 - AI DM")
    
    # 侧边栏
    with st.sidebar:
        st.subheader("游戏状态")
        current_stage = st.session_state.game_state.current_stage
        st.write(f"当前阶段: {GAME_PHASES[current_stage]}")
        
        st.subheader("剩余AP点数")
        st.write(st.session_state.game_state.ap_points)
        
        if st.button("推进至下一阶段"):
            st.session_state.game_state.next_stage()
            new_stage = st.session_state.game_state.current_stage
            opening = st.session_state.game_state.get_stage_opening(new_stage)
            if opening:
                st.session_state.messages.append({"role": "assistant", "content": opening})
            st.rerun()
        
        st.subheader("线索背包")
        with st.expander("已解锁线索"):
            unlocked_clues = st.session_state.game_state.unlocked_clues
            if unlocked_clues:
                for clue in unlocked_clues:
                    st.markdown(f"**{clue['name']}**")
                    st.write(f"ID: {clue['id']}")
                    st.write(f"描述: {clue['description']}")
                    st.write(f"AP消耗: {clue['ap_cost']}")
                    st.markdown("---")
            else:
                st.write("暂无解锁的线索")
    
    # 主界面
    if not st.session_state.selected_role:
        st.subheader("角色选择")
        roles = st.session_state.game_state.get_all_roles()
        for role in roles:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(role.get('photo', 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + role['id']), use_container_width=True, caption=role['name'])
            with col2:
                st.markdown(f"### {role['name']}")
                st.write(f"职业: {role['profession']}")
                st.write(f"年龄: {role['age']}")
                st.write(f"描述: {role['description']}")
                if st.button(f"选择 {role['name']}", key=role['id']):
                    st.session_state.selected_role = role['id']
                    st.session_state.welcome_message_sent = False
                    st.rerun()
    else:
        st.subheader("对话区")
        
        for msg in st.session_state.messages:
            with st.chat_message(msg['role']):
                st.write(msg['content'])
        
        user_input = st.chat_input("说吧")
        voice_input = st.text_input("语音输入（测试）")
        
        final_input = user_input or voice_input
        
        if final_input:
            st.session_state.messages.append({"role": "user", "content": final_input})
            with st.chat_message("user"):
                st.write(final_input)
            
            # 搜证阶段处理
            if check_search_trigger(final_input) and current_stage == 1:
                clue = st.session_state.game_state.unlock_clue(final_input)
                if isinstance(clue, dict):
                    ai_response = f"你发现了新线索：\n\n**{clue['name']}**\nID: {clue['id']}\n描述: {clue['description']}\n\n消耗了 {clue['ap_cost']} 点AP。"
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    with st.chat_message("assistant"):
                        st.write(ai_response)
                    st.rerun()
                else:
                    st.session_state.messages.append({"role": "assistant", "content": clue})
                    with st.chat_message("assistant"):
                        st.write(clue)
            # 复盘阶段：直接输出真相文件内容
            elif current_stage == 4:
                truth = st.session_state.game_state.get_truth()
                if truth:
                    truth_response = f"【复盘真相】\n\n{truth}"
                    st.session_state.messages.append({"role": "assistant", "content": truth_response})
                    with st.chat_message("assistant"):
                        st.write(truth_response)
                else:
                    error_msg = "错误：无法加载真相文件！"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    with st.chat_message("assistant"):
                        st.write(error_msg)
            # 其他阶段：调用AI
            else:
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    full_response = ""
                    for chunk in generate_ai_response(final_input, st.session_state.selected_role):
                        full_response = chunk
                        response_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
