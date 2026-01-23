// ==========================================
// 康复科助手 - 交互逻辑
// ==========================================

// 当前选中的患者
let currentPatient = {
    id: 'patient1',
    name: '张三',
    hospitalNumber: '20241234',
    diagnosis: '脑梗死恢复期',
    dayNumber: 85
};

// ==========================================
// 患者选择功能
// ==========================================

function selectPatient(patientId) {
    // 移除所有患者的选中状态
    document.querySelectorAll('.patient-card').forEach(card => {
        card.style.boxShadow = '';
    });

    // 添加选中效果
    event.currentTarget.style.boxShadow = '0 0 0 3px rgba(0, 122, 255, 0.3)';

    // 根据患者ID更新工作区
    const patientData = {
        'patient1': {
            id: 'patient1',
            name: '张三',
            hospitalNumber: '20241234',
            gender: '男',
            age: 65,
            admissionDate: '2024-10-30',
            dayNumber: 85,
            diagnosis: '脑梗死恢复期'
        },
        'patient2': {
            id: 'patient2',
            name: '李四',
            hospitalNumber: '20241235',
            gender: '女',
            age: 52,
            admissionDate: '2025-01-21',
            dayNumber: 2,
            diagnosis: '脊髓损伤恢复期'
        },
        'patient3': {
            id: 'patient3',
            name: '王五',
            hospitalNumber: '20241236',
            gender: '男',
            age: 48,
            admissionDate: '2025-01-08',
            dayNumber: 15,
            diagnosis: '颅脑损伤恢复期'
        },
        'patient4': {
            id: 'patient4',
            name: '赵六',
            hospitalNumber: '20241237',
            gender: '女',
            age: 61,
            admissionDate: '2024-12-26',
            dayNumber: 28,
            diagnosis: '脑出血恢复期'
        }
    };

    currentPatient = patientData[patientId];

    // 更新界面显示
    updateWorkspaceDisplay();

    // 显示提示
    showNotification(`已选择患者：${currentPatient.name}`);
}

// 更新工作区显示
function updateWorkspaceDisplay() {
    const workspace = document.querySelector('.workspace');

    // 更新患者信息
    workspace.querySelector('.detail-row:nth-child(1) .value').textContent = currentPatient.hospitalNumber;
    workspace.querySelector('.detail-row:nth-child(2) .value').textContent = currentPatient.name;
    workspace.querySelector('.detail-row:nth-child(3) .value').textContent = currentPatient.gender;
    workspace.querySelector('.detail-row:nth-child(4) .value').textContent = currentPatient.age + '岁';
    workspace.querySelector('.detail-row:nth-child(5) .value').textContent = `${currentPatient.admissionDate} (第${currentPatient.dayNumber}天)`;
    workspace.querySelector('.detail-row:nth-child(6) .value').textContent = currentPatient.diagnosis;

    // 清空输入和预览
    document.getElementById('daily-condition').value = '';
    document.getElementById('preview-content').innerHTML = '';
}

// ==========================================
// 病程记录生成功能
// ==========================================

function generateNote() {
    const dailyCondition = document.getElementById('daily-condition').value.trim();

    if (!dailyCondition) {
        showNotification('请输入当日情况', 'warning');
        return;
    }

    // 显示生成中提示
    const btn = event.currentTarget;
    const originalContent = btn.innerHTML;
    btn.innerHTML = '<span class="icon">⏳</span><span class="btn-label">生成中...</span>';
    btn.disabled = true;

    // 模拟AI生成（实际应用中会调用AI API）
    setTimeout(() => {
        const generatedNote = generateMockNote(dailyCondition);

        // 显示生成的病程记录
        document.getElementById('preview-content').innerHTML = generatedNote;

        // 恢复按钮状态
        btn.innerHTML = originalContent;
        btn.disabled = false;

        showNotification('病程记录生成成功！', 'success');
    }, 1500);
}

// 生成模拟病程记录
function generateMockNote(condition) {
    const today = new Date();
    const dateStr = today.toISOString().split('T')[0];
    const timeStr = '09:' + String(Math.floor(Math.random() * 60)).padStart(2, '0');

    return `
        <strong>${dateStr} ${timeStr} 主治医师查房记录</strong><br><br>
        汇报病史略<br><br>
        主诉：${condition}<br><br>
        查体：患者神志清，精神可。T：36.5°C，P：78次/分，R：18次/分，BP：128/78mmHg。心肺等内科查体未见明确异常。右侧上肢肌力3+级，右侧下肢肌力4级，左侧肢体肌力5级。<br><br>
        上级医师分析：患者脑梗死恢复期，目前病情稳定，康复训练效果良好，继续当前康复方案。<br><br>
        家属宣教：指导患者坚持康复训练，家属配合辅助训练。<br><br>
        <br>
        住院医师：于友达<br>
        主治医师：都吉香
    `;
}

// ==========================================
// 保存功能
// ==========================================

function saveNote() {
    const previewContent = document.getElementById('preview-content').innerHTML.trim();

    if (!previewContent) {
        showNotification('没有可保存的病程记录', 'warning');
        return;
    }

    // 模拟保存
    showNotification('病程记录已保存', 'success');
}

// ==========================================
// 导出功能
// ==========================================

function exportNote() {
    const previewContent = document.getElementById('preview-content').innerText.trim();

    if (!previewContent) {
        showNotification('没有可导出的病程记录', 'warning');
        return;
    }

    // 创建文本文件
    const blob = new Blob([previewContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentPatient.hospitalNumber}_${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);

    showNotification('病程记录已导出为TXT文件', 'success');
}

// ==========================================
// 模板插入功能
// ==========================================

function insertTemplate(type, value) {
    if (!value) return;

    const textarea = document.getElementById('daily-condition');
    const currentValue = textarea.value;

    if (currentValue) {
        textarea.value = currentValue + ' ' + value;
    } else {
        textarea.value = value;
    }

    textarea.focus();

    // 重置下拉框
    event.target.selectedIndex = 0;
}

function insertPhrase(phrase) {
    const textarea = document.getElementById('daily-condition');
    const currentValue = textarea.value;

    if (currentValue) {
        textarea.value = currentValue + '，' + phrase;
    } else {
        textarea.value = phrase;
    }

    textarea.focus();
}

// ==========================================
// 历史记录加载
// ==========================================

function loadRecord(date) {
    showNotification(`正在加载 ${date} 的记录...`, 'info');

    // 模拟加载历史记录
    setTimeout(() => {
        document.getElementById('preview-content').innerHTML = `
            <strong>${date}-2025 查房记录</strong><br><br>
            主诉：患者病情稳定，继续康复训练。<br><br>
            查体：患者神志清，精神可。T：36.3°C，P：76次/分，R：17次/分，BP：125/75mmHg。<br><br>
            分析：患者康复进展良好，继续当前方案。<br><br>
            处理：1.继续康复训练 2.监测生命体征
        `;
        showNotification('记录加载完成', 'success');
    }, 500);
}

// ==========================================
// 新患者模态框
// ==========================================

function showNewPatientModal() {
    document.getElementById('newPatientModal').classList.add('active');
    goToStep(1);
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// 步骤导航
function goToStep(stepNumber) {
    // 隐藏所有步骤内容
    document.querySelectorAll('.step-content').forEach(content => {
        content.classList.remove('active');
    });

    // 显示目标步骤
    document.getElementById(`step${stepNumber}`).classList.add('active');

    // 更新步骤指示器
    document.querySelectorAll('.step').forEach((step, index) => {
        if (index + 1 <= stepNumber) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

// 提取患者信息（模拟）
function extractInfo() {
    const initialNote = document.getElementById('initial-note').value.trim();

    if (!initialNote) {
        showNotification('请粘贴首次病程记录', 'warning');
        return;
    }

    // 显示提取中提示
    showNotification('AI正在提取患者信息...', 'info');

    // 模拟AI提取
    setTimeout(() => {
        goToStep(3);
        showNotification('患者信息提取成功！', 'success');
    }, 1500);
}

// 保存患者
function savePatient() {
    showNotification('患者档案创建成功！', 'success');
    closeModal('newPatientModal');

    // 模拟添加到患者列表
    setTimeout(() => {
        showNotification('新患者已添加到今日待办列表', 'success');
    }, 500);
}

// ==========================================
// 设置模态框
// ==========================================

function showSettings() {
    document.getElementById('settingsModal').classList.add('active');
}

// 标签切换
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        // 移除所有激活状态
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        // 添加当前激活状态
        this.classList.add('active');
        const tabName = this.dataset.tab;
        document.getElementById(`tab-${tabName}`).classList.add('active');
    });
});

// ==========================================
// 提醒功能
// ==========================================

function showReminders() {
    const reminders = `
        今日待办提醒 (5项)：
        🚨 张三 - 住院第85天，注意90天限制
        🚨 张三 - 需书写主治医师查房记录
        🔬 李四 - 请查看化验检查结果
        📝 王五 - 需书写常规查房记录
        📝 赵六 - 需书写常规查房记录
    `;
    alert(reminders);
}

// ==========================================
// 搜索知识库
// ==========================================

function searchKnowledge() {
    showNotification('正在从知识库检索相关资料...', 'info');

    setTimeout(() => {
        showNotification('知识库检索完成，已找到3篇相关文档', 'success');
    }, 1000);
}

function showHistory() {
    showNotification('正在加载历史病程记录...', 'info');

    setTimeout(() => {
        showNotification('已加载最近3次病程记录', 'success');
    }, 500);
}

// ==========================================
// 通知系统
// ==========================================

function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // 添加样式
    Object.assign(notification.style, {
        position: 'fixed',
        top: '80px',
        right: '24px',
        padding: '12px 20px',
        borderRadius: '12px',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        zIndex: '9999',
        animation: 'slideIn 0.3s ease',
        maxWidth: '300px',
        fontSize: '14px',
        fontWeight: '500'
    });

    // 根据类型设置颜色
    const colors = {
        success: '#34C759',
        warning: '#FF9500',
        error: '#FF3B30',
        info: '#007AFF'
    };

    notification.style.background = colors[type] || colors.info;
    notification.style.color = 'white';

    // 添加到页面
    document.body.appendChild(notification);

    // 3秒后自动移除
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ==========================================
// 键盘快捷键
// ==========================================

document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + N: 新患者
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        showNewPatientModal();
    }

    // Ctrl/Cmd + S: 保存
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveNote();
    }

    // Ctrl/Cmd + Enter: 生成
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        generateNote();
    }

    // ESC: 关闭模态框
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
    }
});

// ==========================================
// 初始化
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('康复科助手系统已启动');

    // 显示欢迎提示
    setTimeout(() => {
        showNotification('欢迎使用康复科助手！', 'success');
    }, 500);

    // 设置默认选中第一个患者
    selectPatient('patient1');
});

// ==========================================
// 工具函数
// ==========================================

// 格式化日期
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// 计算住院天数
function calculateDayNumber(admissionDate) {
    const admission = new Date(admissionDate);
    const today = new Date();
    const diffTime = Math.abs(today - admission);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

// 生成随机时间
function generateRandomTime() {
    const hour = Math.floor(Math.random() * 3) + 8; // 8-10点
    const minute = String(Math.floor(Math.random() * 60)).padStart(2, '0');
    return `${hour}:${minute}`;
}

console.log('康复科助手 - 交互逻辑加载完成');
