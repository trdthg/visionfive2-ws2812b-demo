const API_BASE = '/api';
let selectedAnswer = null;

// 状态管理
const states = ['init', 'wait', 'yes', 'no', 'end'];
const stateContents = {
    'init': document.getElementById('init-state'),
    'wait': document.getElementById('wait-state'),
    'yes': document.getElementById('yes-state'),
    'no': document.getElementById('no-state'),
    'end': document.getElementById('end-state')
};

// 显示指定状态的内容
function showState(state) {
    states.forEach(s => {
        const content = stateContents[s];
        if (content) {
            content.classList.toggle('hidden', s !== state);
        }
    });
}

// 更新分数显示
function updateScore(score) {
    document.getElementById('yes-acc').textContent = score.yes_acc;
    document.getElementById('yes-count').textContent = score.yes_count;
    document.getElementById('no-count').textContent = score.no_count;
}

// 创建选项元素
// 创建选项元素
function createOption(text) {
    const option = document.createElement('div');
    option.className = 'option-item';
    option.textContent = text;
    option.onclick = () => {
        document.querySelectorAll('.option-item').forEach(opt => {
            opt.classList.remove('selected');
        });
        option.classList.add('selected');
        // 只取选项的第一个字母（A、B、C、D）
        selectedAnswer = text.split(':')[0].trim();
        document.getElementById('submit-btn').disabled = false;
    };
    return option;
}

// 开始新问题
async function startQuestion() {
    try {
        // 显示加载动画
        document.getElementById('loading-spinner').classList.remove('hidden');
        document.getElementById('init-state').classList.add('hidden');
        
        const response = await fetch(`${API_BASE}/question/start`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            const { question, options } = data.data;
            document.getElementById('question-text').textContent = question;
            
            const optionsContainer = document.getElementById('options-container');
            optionsContainer.innerHTML = '';
            options.forEach(option => {
                optionsContainer.appendChild(createOption(option));
            });
            
            selectedAnswer = null;
            document.getElementById('submit-btn').disabled = true;
            
            // 隐藏加载动画并显示问题
            document.getElementById('loading-spinner').classList.add('hidden');
            showState('wait');
        } else {
            // 出错时也要隐藏加载动画
            document.getElementById('loading-spinner').classList.add('hidden');
            showState('init');
            alert('获取问题失败：' + data.message);
        }
    } catch (error) {
        // 出错时也要隐藏加载动画
        document.getElementById('loading-spinner').classList.add('hidden');
        showState('init');
        alert('网络错误，请重试');
    }
}

// 提交答案
async function submitAnswer() {
    if (!selectedAnswer) return;
    
    try {
        const response = await fetch(`${API_BASE}/question/answer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ answer: selectedAnswer })
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            const { correct, explanation, score } = data.data;
            
            // 更新解释文本
            const explanationElement = document.getElementById(correct ? 'yes-explanation' : 'no-explanation');
            explanationElement.textContent = explanation;
            
            updateScore(score);
            showState(correct ? 'yes' : 'no');
        } else {
            alert('提交答案失败：' + data.message);
        }
    } catch (error) {
        alert('网络错误，请重试');
    }
}

// 下一题
async function nextQuestion() {
    try {
        const response = await fetch(`${API_BASE}/question/next`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            showState('end');
            setTimeout(startQuestion, 1000);
        } else {
            alert('操作失败：' + data.message);
        }
    } catch (error) {
        alert('网络错误，请重试');
    }
}

// 获取初始状态
async function getStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        
        if (data.status === 'success') {
            // 忽略后端状态，总是显示初始状态
            showState('init');
            updateScore(data.data.score);
        }
    } catch (error) {
        console.error('获取状态失败');
        // 出错时也显示初始状态
        showState('init');
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    getStatus();
});