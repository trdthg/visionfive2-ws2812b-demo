const API_BASE = '/api';
let selectedAnswer = null;
let currentQuestion = null;

// 状态管理
const states = ['init', 'wait', 'yes', 'no', 'end'];
const stateContents = {
    'init': document.getElementById('init-state'),
    'wait': document.getElementById('wait-state'),
    'yes': document.getElementById('yes-state'),
    'no': document.getElementById('no-state'),
    'end': document.getElementById('end-state')
};

// 分数统计
const score = {
    yes_count: 0,
    yes_acc: 0,
    no_count: 0,
    no_acc: 0
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
        // 如果是从 end 状态开始，不显示加载动画
        const endState = document.getElementById('end-state');
        const initState = document.getElementById('init-state');
        
        if (!endState.classList.contains('hidden')) {
            showState('wait');
        } else if (!initState.classList.contains('hidden')) {
            showState('wait');
        } else {
            document.getElementById('loading-spinner').classList.remove('hidden');
        }
        
        const response = await fetch(`${API_BASE}/question/start`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            const { question, options, answer, more } = data.data;
            currentQuestion = { question, options, answer, more };
            
            document.getElementById('question-text').textContent = question;
            const optionsContainer = document.getElementById('options-container');
            optionsContainer.innerHTML = '';
            options.forEach(option => {
                optionsContainer.appendChild(createOption(option));
            });
            
            selectedAnswer = null;
            document.getElementById('submit-btn').disabled = true;
            
            document.getElementById('loading-spinner').classList.add('hidden');
            showState('wait');
            
            // 通知后端切换到等待状态
            await fetch(`${API_BASE}/light/wait`, { method: 'POST' });
        } else {
            document.getElementById('loading-spinner').classList.add('hidden');
            showState('init');
            alert('获取问题失败：' + data.message);
        }
    } catch (error) {
        document.getElementById('loading-spinner').classList.add('hidden');
        showState('init');
        alert('网络错误，请重试');
    }
}

// 提交答案
async function submitAnswer() {
    if (!selectedAnswer || !currentQuestion) return;
    
    const isCorrect = selectedAnswer === currentQuestion.answer;
    
    if (isCorrect) {
        score.yes_count++;
        score.yes_acc++;
        score.no_acc = 0;
        showState('yes');
        document.getElementById('yes-explanation-text').textContent = currentQuestion.more;
        // 通知后端显示正确灯效
        await fetch(`${API_BASE}/light/correct`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ combo: score.yes_acc })
        });
    } else {
        score.no_count++;
        score.no_acc++;
        score.yes_acc = 0;
        showState('no');
        document.getElementById('no-explanation-text').textContent = currentQuestion.more;
        // 通知后端显示错误灯效
        await fetch(`${API_BASE}/light/wrong`, { method: 'POST' });
    }
    
    updateScore(score);
}

// 下一题
async function nextQuestion() {
    try {
        document.getElementById('loading-spinner').classList.remove('hidden');
        showState('end');
        
        // 通知后端切换到结束状态
        await fetch(`${API_BASE}/light/end`, { method: 'POST' });
        
        document.getElementById('loading-spinner').classList.add('hidden');
        setTimeout(startQuestion, 1000);
    } catch (error) {
        document.getElementById('loading-spinner').classList.add('hidden');
        alert('网络错误，请重试');
    }
}

// 获取初始状态
function getStatus() {
    showState('init');
    updateScore(score);
    // 通知后端切换到初始状态
    fetch(`${API_BASE}/light/init`, { method: 'POST' }).catch(console.error);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    getStatus();
});