document.addEventListener('DOMContentLoaded', function() {
    // 查找AI分析内容
    const contentWrapper = document.getElementById('ai-content-wrapper');
    if (!contentWrapper) return;
    
    // 获取原始内容
    const originalContent = contentWrapper.innerHTML;
    console.log("原始内容长度: " + originalContent.length + " 字符");
    
    // 动态检测文档中包含的任务类型
    const taskTypes = detectTaskTypes(originalContent);
    console.log("检测到的任务类型: ", taskTypes);
    
    // 如果没有检测到任何任务类型，则保留原始内容并显示提示信息
    if (taskTypes.length === 0) {
        contentWrapper.innerHTML = '<div class="warning-message">未检测到任何AI分析任务内容</div>' + originalContent;
        return;
    }
    
    // 通过标记精确提取任务内容
    const tasks = extractTasksByMarkers(originalContent, taskTypes);
    
    // 清空原始内容，准备重新填充
    contentWrapper.innerHTML = '';
    
    // 重命名任务类型
    const renameTask = (taskType) => {
        if (taskType === "AI竞争分析") {
            return "AI摘要分析";
        }
        return taskType;
    };
    
    // 定义任务的优先级顺序
    const taskPriority = {
        "AI摘要分析": 1,
        "AI全文翻译": 2,
        "AI技术要点": 3,
        "AI市场影响": 4
    };
    
    // 按照优先级排序任务类型
    const sortedTaskTypes = [...taskTypes].sort((a, b) => {
        const taskA = a === "AI竞争分析" ? "AI摘要分析" : a;
        const taskB = b === "AI竞争分析" ? "AI摘要分析" : b;
        
        const priorityA = taskPriority[taskA] || 999;
        const priorityB = taskPriority[taskB] || 999;
        return priorityA - priorityB;
    });
    
    // 创建TAB导航
    const tabNav = document.createElement('div');
    tabNav.className = 'tab-nav';
    
    // 创建TAB内容容器
    const tabContents = {};
    
    // 按照排序后的任务顺序创建TAB
    sortedTaskTypes.forEach((taskType, index) => {
        const content = tasks[taskType] || '';
        const displayName = renameTask(taskType);
        const tabId = `tab-${index}`;
        
        // 创建TAB按钮
        const tabButton = document.createElement('button');
        tabButton.className = 'tab-button';
        tabButton.textContent = displayName;
        tabButton.setAttribute('data-tab', tabId);
        if (index === 0) {
            tabButton.classList.add('active');
        }
        tabNav.appendChild(tabButton);
        
        // 创建TAB内容
        const tabContent = document.createElement('div');
        tabContent.className = 'tab-content';
        tabContent.id = tabId;
        if (index === 0) {
            tabContent.classList.add('active');
        }
        tabContent.innerHTML = content || '<p>此部分暂无内容</p>';
        tabContents[tabId] = tabContent;
    });
    
    // 将TAB导航添加到容器
    contentWrapper.appendChild(tabNav);
    
    // 将TAB内容添加到容器
    Object.values(tabContents).forEach(content => {
        contentWrapper.appendChild(content);
    });
    
    // 添加TAB切换逻辑
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // 更新按钮状态
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
            
            // 更新内容显示
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(tabId).classList.add('active');
        });
    });
});

/**
 * 动态检测文档中包含的任务类型
 */
function detectTaskTypes(content) {
    const taskTypes = [];
    let currentPos = 0;
    const startToken = "<!-- AI_TASK_START: ";
    const endToken = " -->";
    
    while (true) {
        const startIndex = content.indexOf(startToken, currentPos);
        if (startIndex === -1) break;
        
        const typeStartIndex = startIndex + startToken.length;
        const typeEndIndex = content.indexOf(endToken, typeStartIndex);
        
        if (typeEndIndex !== -1) {
            const taskType = content.substring(typeStartIndex, typeEndIndex);
            if (taskType !== "AI标题翻译" && !taskTypes.includes(taskType)) {
                taskTypes.push(taskType);
            }
            currentPos = typeEndIndex + endToken.length;
        } else {
            break;
        }
    }
    
    return taskTypes;
}

/**
 * 通过HTML注释标记提取任务内容
 */
function extractTasksByMarkers(content, taskTypes) {
    const tasks = {};
    
    taskTypes.forEach(function(taskType) {
        const startMarker = `<!-- AI_TASK_START: ${taskType} -->`;
        const endMarker = `<!-- AI_TASK_END: ${taskType} -->`;
        
        const startIndex = content.indexOf(startMarker);
        const endIndex = content.indexOf(endMarker);
        
        if (startIndex !== -1 && endIndex !== -1 && startIndex < endIndex) {
            const taskContent = content.substring(startIndex + startMarker.length, endIndex).trim();
            console.log(`通过标记提取任务: ${taskType}, 内容长度: ${taskContent.length}`);
            tasks[taskType] = taskContent;
        }
    });
    
    return tasks;
}
