const API_BASE = '/api';
let selectedAnswer = null;
let currentQuestion = null;

// 状态管理
const states = ['loading', 'init', 'wait', 'yes', 'no', 'end', 'win'];
const stateContents = {
    'loading': { e: document.getElementById('loading-spinner'), old_display: null },
    'init': {e : document.getElementById('init-state'), old_display: null },
    'wait': {e : document.getElementById('wait-state'), old_display: null },
    'yes': {e : document.getElementById('yes-state'), old_display: null },
    'no': {e : document.getElementById('no-state'), old_display: null },
    'end': {e : document.getElementById('end-state'), old_display: null },
    'win': {e : document.getElementById('win-state'), old_display: null }
}

// 分数统计
const score = {
    yes_count: 0,
    yes_acc: 0,
    no_count: 0,
    no_acc: 0
};

questions = [];

// 显示指定状态的内容
function showState(state) {
    states.forEach(s => {
        const content = stateContents[s];
        if (content.e) {
            if (s === state) {
                content.e.style.display = content.old_display;
            } else {
                content.e.style.display = 'none';
            }
        }
    });
}

// 更新分数显示
function updateScore(score) {
    document.getElementById('yes-acc').textContent = score.yes_acc;
    document.getElementById('yes-count').textContent = score.yes_count;
    document.getElementById('no-count').textContent = score.no_count;
}

// 重制分数
function resetScore() {
    score.yes_count = 0;
    score.yes_acc = 0;
    score.no_count = 0;
    updateScore(score);
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
async function nextQuestion() {
    try {
        // 加载题目
        showState('loading')
        await fetch(`${API_BASE}/light/change/loading`, { method: 'POST' });

        const response = await fetch(`${API_BASE}/question/start`, {
            method: 'POST'
        });

        questions.push(response)
        const data = await response.json();

        if (data.status === 'success') {
            const { question, options, answer, more } = data.data;
            currentQuestion = { question, options, answer, more };
            // 题目
            document.getElementById('question-text').textContent = question;
            // 选项
            const optionsContainer = document.getElementById('options-container');
            optionsContainer.innerHTML = '';
            options.forEach(option => {
                optionsContainer.appendChild(createOption(option));
            });
            // 选择的
            selectedAnswer = null;

            // 等待答题
            showState('wait');
            await fetch(`${API_BASE}/light/change/wait`, { method: 'POST' });
        } else {
            alert('获取问题失败：' + data.message);
        }
    } catch (error) {
        showState('init');
        alert('网络错误，请重试');
    }
}


function typewriterEffect(text, element, speed = 30) {
    element.textContent = ''; // Clear existing content
    let i = 0;
    
    // Function to add next character
    function typeNextChar() {
      if (i < text.length) {
        element.textContent += text.charAt(i);
        i++;
        setTimeout(typeNextChar, speed);
      }
    }
    
    // Start the typing effect
    typeNextChar();
  }

// 提交答案
async function submitAnswer() {
    if (!selectedAnswer || !currentQuestion) return;
    const isCorrect = selectedAnswer === currentQuestion.answer;
    questions[questions.length - 1]["user_is_correct"] = isCorrect
    if (isCorrect) {
        score.yes_count++;
        score.yes_acc++;
        score.no_acc = 0;
        showState('yes');
        await fetch(`${API_BASE}/light/change/yes`, {method: 'POST' });
        // 展示答案
        // document.getElementById('yes-explanation-text').textContent = currentQuestion.more;
        typewriterEffect(
            currentQuestion.more, 
            document.getElementById('yes-explanation-text')
        );
        // 通知后端显示正确灯效
    } else {
        score.no_count++;
        score.no_acc++;
        score.yes_acc = 0;
        // 通知后端显示错误灯效
        showState('no');
        await fetch(`${API_BASE}/light/change/no`, { method: 'POST' });
        typewriterEffect(
            currentQuestion.more,
            document.getElementById('no-explanation-text')
        );
    }
    updateScore(score);

    // 总结
    if (questions.length == 5) {
        document.getElementById('ai-comment').textContent = ""
        showState('win');
        typewriterEffect(
            "thinging...",
            document.getElementById('ai-comment')
        );
        if (score.yes_acc >= 3) {
            fetch(`${API_BASE}/light/change/rainbow`, { method: 'POST' });
        } else {
            fetch(`${API_BASE}/light/change/sleep`, { method: 'POST' });
        }
        const response = await fetch(`${API_BASE}/summary`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
              },
            body: JSON.stringify({
                summary: JSON.stringify(questions)
            })
        });
        console.log(response)
        const data = await response.json();
        typewriterEffect(
            data.summary,
            document.getElementById('ai-comment')
        );
        return
    }
}

// 更新分数显示
function updateScore(score) {
    document.getElementById('yes-acc').textContent = score.yes_acc;
    document.getElementById('yes-count').textContent = score.yes_count;
    document.getElementById('no-count').textContent = score.no_count;
}

// 获取初始状态
function initStatus() {
    showState('init');
    resetScore();
    questions = []
    // 通知后端切换到初始状态
    fetch(`${API_BASE}/light/change/sleep`, { method: 'POST' }).catch(console.error);
}

function boom() {
    initStatus()
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    // init stateContents old_display, old_display = e.style.display
    for (const key in stateContents) {
        stateContents[key].old_display = stateContents[key].e.style.display;
    }
    initStatus();
});