document.addEventListener('DOMContentLoaded', function() {
    // 标签页切换功能
    function setupTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tabId = this.getAttribute('data-tab');
                
                // 更新标签按钮状态
                tabButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // 显示对应的标签内容
                tabContents.forEach(content => {
                    if (content.id === `tab-${tabId}`) {
                        content.classList.add('active');
                    } else {
                        content.classList.remove('active');
                    }
                });
            });
        });

        // 默认显示第一个标签
        if (tabButtons.length > 0) {
            tabButtons[0].classList.add('active');
            tabContents[0].classList.add('active');
        }
    }

    // 分页功能改为瀑布流加载
    function setupPagination(docType) {
        const cardsContainer = document.getElementById(`doc-cards-${docType}`);
        const paginationContainer = document.getElementById(`pagination-${docType}`);
        
        // 确保容器存在
        if (!cardsContainer) {
            console.error(`Cards container for ${docType} not found!`);
            return { filterCards: () => {} };
        }
        
        // 隐藏分页容器，因为我们不需要加载更多按钮
        if (paginationContainer) {
            paginationContainer.style.display = 'none';
        }
        
        const cards = Array.from(cardsContainer.querySelectorAll('.doc-card'));
        let filteredCards = [...cards]; // 使用展开运算符创建原始数组的真正副本
        
        function renderAllCards() {
            // 清空卡片容器
            cardsContainer.innerHTML = '';
            
            // 渲染所有卡片
            filteredCards.forEach(card => {
                const cardClone = card.cloneNode(true);
                cardsContainer.appendChild(cardClone);
            });
            
            // 如果没有搜索结果，显示提示
            if (filteredCards.length === 0) {
                const noResultsDiv = document.createElement('div');
                noResultsDiv.className = 'no-results';
                noResultsDiv.textContent = '没有找到匹配的文章';
                cardsContainer.appendChild(noResultsDiv);
            }
        }
        
        // 排序功能
        const sortSelect = document.getElementById(`sort-${docType}`);
        if (sortSelect) {
            sortSelect.addEventListener('change', function() {
                const sortOption = this.value;
                sortCards(sortOption);
                renderAllCards(); // 排序后重新渲染所有卡片
            });
        }
        
        function sortCards(option) {
            console.log(`Sorting ${docType} cards by ${option}`); // 调试日志
            
            filteredCards.sort((a, b) => {
                if (option === 'date-desc' || option === 'date-asc') {
                    // 获取日期字符串，确保格式一致
                    let dateA = a.getAttribute('data-date') || '1970-01-01';
                    let dateB = b.getAttribute('data-date') || '1970-01-01';
                    
                    // 标准化日期格式 (YYYY-MM-DD)
                    if (dateA.includes('_')) dateA = dateA.replace(/_/g, '-');
                    if (dateB.includes('_')) dateB = dateB.replace(/_/g, '-');
                    
                    // 处理可能的日期格式问题
                    const parseDate = (dateStr) => {
                        try {
                            // 尝试直接创建日期对象
                            const date = new Date(dateStr);
                            // 检查日期是否有效
                            if (isNaN(date.getTime())) {
                                console.log(`Invalid date: ${dateStr}, using fallback`);
                                return new Date('1970-01-01');
                            }
                            return date;
                        } catch (e) {
                            console.log(`Error parsing date: ${dateStr}`, e);
                            return new Date('1970-01-01');
                        }
                    };
                    
                    const parsedDateA = parseDate(dateA);
                    const parsedDateB = parseDate(dateB);
                    
                    // 根据排序选项返回比较结果
                    return option === 'date-desc' 
                        ? parsedDateB - parsedDateA 
                        : parsedDateA - parsedDateB;
                } else if (option === 'title-asc') {
                    return (a.getAttribute('data-title') || '').localeCompare(b.getAttribute('data-title') || '');
                } else if (option === 'title-desc') {
                    return (b.getAttribute('data-title') || '').localeCompare(a.getAttribute('data-title') || '');
                }
                return 0; // 默认返回
            });
        }
        
        // 过滤功能 - 与搜索功能配合
        function filterCards(searchTerm = '') {
            if (!searchTerm) {
                filteredCards = [...cards]; // 重置为所有卡片
            } else {
                searchTerm = searchTerm.toLowerCase();
                filteredCards = cards.filter(card => {
                    const title = (card.getAttribute('data-title') || '').toLowerCase();
                    return title.includes(searchTerm);
                });
            }
            
            // 应用当前选择的排序
            const currentSortOption = sortSelect ? sortSelect.value : 'date-desc';
            sortCards(currentSortOption);
            
            // 渲染所有卡片
            renderAllCards();
        }
        
        // 增加标签页可见性监听
        const tabContent = cardsContainer.closest('.tab-content');
        if (tabContent) {
            const observer = new MutationObserver(mutations => {
                mutations.forEach(mutation => {
                    if (mutation.attributeName === 'class' && 
                        tabContent.classList.contains('active')) {
                        console.log(`Tab ${docType} became active, refreshing cards`);
                    }
                });
            });
            
            observer.observe(tabContent, { attributes: true });
        }
        
        // 初始化
        // 1. 先应用默认排序 (日期降序)
        sortCards('date-desc');
        
        // 2. 直接渲染所有卡片
        renderAllCards();
        
        // 3. 公开筛选方法，供搜索功能使用
        return {
            filterCards: filterCards
        };
    }

    // 搜索功能
    function setupSearch() {
        // 存储每个docType的分页控制器
        const paginationControllers = {};
        
        // 使用新的class选择器
        const searchInputs = document.querySelectorAll('.document-search');
        
        searchInputs.forEach(searchInput => {
            // 获取当前标签页的内容
            const tabContent = searchInput.closest('.tab-content');
            if (!tabContent) return;
            
            const docType = tabContent.getAttribute('data-doc-type');
            
            // 监听搜索输入
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                console.log(`Searching in ${docType} for: ${searchTerm}`); // 调试日志
                
                // 使用对应文档类型的过滤器
                if (paginationControllers[docType]) {
                    paginationControllers[docType].filterCards(searchTerm);
                }
            });
        });
        
        // 返回分页控制器集合，供后续使用
        return paginationControllers;
    }

    // 初始化标签页
    setupTabs();
    
    // 初始化所有文档类型的分页，并收集分页控制器
    const paginationControllers = {};
    document.querySelectorAll('.tab-content').forEach(content => {
        const docType = content.getAttribute('data-doc-type');
        paginationControllers[docType] = setupPagination(docType);
    });

    // 初始化搜索功能，并传入分页控制器
    setupSearch(paginationControllers);
    
    // 处理窗口大小变化，重新计算分页和布局
    let resizeTimeout;
    window.addEventListener('resize', function() {
        // 防抖动，避免频繁触发
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            console.log('Window resized, recalculating layout');
            
            // 重新初始化所有文档类型的分页
            document.querySelectorAll('.tab-content').forEach(content => {
                const docType = content.getAttribute('data-doc-type');
                
                // 获取当前活动的排序选项
                const sortSelect = document.getElementById(`sort-${docType}`);
                const currentSortOption = sortSelect ? sortSelect.value : 'date-desc';
                
                // 重新初始化分页
                paginationControllers[docType] = setupPagination(docType);
                
                // 应用之前的排序选项
                if (sortSelect) {
                    sortSelect.value = currentSortOption;
                    sortSelect.dispatchEvent(new Event('change'));
                }
            });
        }, 250); // 250ms延迟
    });
});
