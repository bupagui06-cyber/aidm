import streamlit as st
import streamlit.components.v1 as components

# 创建语音输入组件
def voice_input():
    """创建语音输入组件
    
    Returns:
        str: 语音识别的文本
    """
    # 语音输入的HTML和JavaScript代码
    voice_input_html = """
    <div id="voice-input-container">
        <button id="start-record-btn" style="padding: 6px 12px; font-size: 12px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">
            🎤 开始语音
        </button>
        <button id="stop-record-btn" style="padding: 6px 12px; font-size: 12px; background-color: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer; margin-left: 8px; display: none;">
            ⏹️ 停止录音
        </button>
        <div id="status" style="margin-top: 6px; font-size: 12px; color: #666;"></div>
        <div id="result" style="margin-top: 6px; padding: 6px; border: 1px solid #ddd; border-radius: 4px; display: none; font-size: 12px;"></div>
    </div>
    
    <script>
        // 获取DOM元素
        const startBtn = document.getElementById('start-record-btn');
        const stopBtn = document.getElementById('stop-record-btn');
        const status = document.getElementById('status');
        const result = document.getElementById('result');
        
        // 语音识别对象
        let recognition = null;
        
        // 检查浏览器是否支持语音识别
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'zh-CN';
            
            // 开始录音
            startBtn.addEventListener('click', function() {
                try {
                    recognition.start();
                    startBtn.style.display = 'none';
                    stopBtn.style.display = 'inline-block';
                    status.textContent = '正在录音...';
                    result.style.display = 'none';
                } catch (error) {
                    status.textContent = '录音失败: ' + error.message;
                }
            });
            
            // 停止录音
            stopBtn.addEventListener('click', function() {
                recognition.stop();
                startBtn.style.display = 'inline-block';
                stopBtn.style.display = 'none';
                status.textContent = '录音已停止';
            });
            
            // 录音结果
            recognition.onresult = function(event) {
                let transcript = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    transcript += event.results[i][0].transcript;
                }
                result.textContent = transcript;
                result.style.display = 'block';
                
                // 将结果发送给Streamlit
                if (window.parent) {
                    window.parent.postMessage({
                        type: 'voice_input_result',
                        data: transcript
                    }, '*');
                }
            };
            
            // 录音错误
            recognition.onerror = function(event) {
                status.textContent = '错误: ' + event.error;
                startBtn.style.display = 'inline-block';
                stopBtn.style.display = 'none';
            };
            
            // 录音结束
            recognition.onend = function() {
                startBtn.style.display = 'inline-block';
                stopBtn.style.display = 'none';
                status.textContent = '录音已结束';
            };
        } else {
            status.textContent = '您的浏览器不支持语音识别';
            startBtn.disabled = true;
        }
    </script>
    """
    
    # 渲染语音输入组件
    components.html(voice_input_html, height=100)
    
    # 处理语音识别结果
    if 'voice_input' not in st.session_state:
        st.session_state.voice_input = ""
    
    # 监听来自JavaScript的消息
    components.html("""
    <script>
        window.addEventListener('message', function(event) {
            if (event.data.type === 'voice_input_result') {
                // 将结果存储到session_state
                window.parent.document.dispatchEvent(
                    new CustomEvent('streamlit:setComponentValue', {
                        detail: {"key": "voice_input", "value": event.data.data}
                    })
                );
            }
        });
    </script>
    """, height=0)
    
    return st.session_state.get('voice_input', "")
