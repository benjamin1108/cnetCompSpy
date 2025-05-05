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

    // 瀑布流加载功能
    function setupPagination(docType) {
        const cardsContainer = document.getElementById(`doc-cards-${docType}`);
        const paginationContainer = document.getElementById(`pagination-${docType}`);
        
        // 确保容器存在
        if (!cardsContainer) {
            console.error(`Cards container for ${docType} not found!`);
            return { filterCards: () => {} };
        }
        
        // 将分页容器转换为加载更多按钮容器
        if (paginationContainer) {
            paginationContainer.className = 'load-more-container';
            // 添加固定的ID以便后续引用
            paginationContainer.setAttribute('data-pagination-id', `pagination-${docType}`);
        }
        
        const cards = Array.from(cardsContainer.querySelectorAll('.doc-card'));
        let filteredCards = [...cards]; // 使用展开运算符创建原始数组的真正副本
        
        // 初始和增量加载的文章数量 - 所有设备统一使用相同数值
        const initialLoadCount = 20; // 初始加载20篇文章
        const loadMoreCount = 20; // 每次点击"加载更多"时加载20篇文章
        let currentlyLoaded = 0;
        
        // 存储加载状态，防止重复操作
        let isLoading = false;
        
        function renderCards(startIndex, count) {
            const endIndex = Math.min(startIndex + count, filteredCards.length);
            const cardsToRender = filteredCards.slice(startIndex, endIndex);
            
            cardsToRender.forEach(card => {
                const cardClone = card.cloneNode(true);
                cardsContainer.appendChild(cardClone);
            });
            
            return endIndex - startIndex; // 返回实际渲染的卡片数量
        }
        
        function updateLoadMoreButton() {
            if (!paginationContainer) return;
            
            // 清空加载更多按钮容器
            paginationContainer.innerHTML = '';
            
            // 创建信息文本
            const infoDiv = document.createElement('div');
            infoDiv.className = 'load-more-info';
            infoDiv.textContent = `显示 ${currentlyLoaded} / ${filteredCards.length} 篇文章`;
            paginationContainer.appendChild(infoDiv);
            
            // 如果还有更多文章可以加载，显示加载更多按钮
            if (currentlyLoaded < filteredCards.length) {
                const loadMoreBtn = document.createElement('button');
                loadMoreBtn.className = 'load-more-btn';
                loadMoreBtn.textContent = `加载更多文章`;
                
                // 计算还剩多少文章可以加载
                const remaining = filteredCards.length - currentlyLoaded;
                if (remaining <= loadMoreCount) {
                    loadMoreBtn.textContent = `加载剩余 ${remaining} 篇文章`;
                }
                
                loadMoreBtn.addEventListener('click', function() {
                    if (isLoading) return; // 防止重复点击
                    
                    isLoading = true;
                    const added = renderCards(currentlyLoaded, loadMoreCount);
                    currentlyLoaded += added;
                    
                    // 添加加载动画
                    this.classList.add('loading');
                    this.textContent = '加载中...';
                    
                    // 使用延迟来模拟加载过程，并提供更好的用户体验
                    setTimeout(() => {
                        isLoading = false;
                        updateLoadMoreButton();
                        // 滚动到新加载的内容，但不要滚太多
                        if (added > 0) {
                            const newCards = Array.from(cardsContainer.querySelectorAll('.doc-card'))
                                .slice(-added);
                            if (newCards.length > 0) {
                                newCards[0].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                            }
                        }
                    }, 300);
                });
                
                paginationContainer.appendChild(loadMoreBtn);
            } else if (filteredCards.length > 0) {
                // 全部加载完毕的提示
                const allLoadedInfo = document.createElement('div');
                allLoadedInfo.className = 'all-loaded-info';
                allLoadedInfo.textContent = '已加载全部文章';
                paginationContainer.appendChild(allLoadedInfo);
            }
        }
        
        // 排序功能
        const sortSelect = document.getElementById(`sort-${docType}`);
        if (sortSelect) {
            sortSelect.addEventListener('change', function() {
                const sortOption = this.value;
                sortCards(sortOption);
                resetAndRenderCards();
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
            
            // 重置并重新渲染卡片
            resetAndRenderCards();
        }
        
        function resetAndRenderCards() {
            // 清空卡片容器
            cardsContainer.innerHTML = '';
            
            // 重置加载计数
            currentlyLoaded = 0;
            
            // 渲染初始卡片集
            const added = renderCards(0, initialLoadCount);
            currentlyLoaded += added;
            
            // 更新加载更多按钮
            updateLoadMoreButton();
            
            // 如果没有搜索结果，显示提示
            if (filteredCards.length === 0) {
                const noResultsDiv = document.createElement('div');
                noResultsDiv.className = 'no-results';
                noResultsDiv.textContent = '没有找到匹配的文章';
                cardsContainer.appendChild(noResultsDiv);
            }
        }
        
        // 增加标签页可见性监听
        const tabContent = cardsContainer.closest('.tab-content');
        if (tabContent) {
            const observer = new MutationObserver(mutations => {
                mutations.forEach(mutation => {
                    if (mutation.attributeName === 'class' && 
                        tabContent.classList.contains('active')) {
                        console.log(`Tab ${docType} became active, refreshing cards`);
                        // 只刷新加载更多按钮，不重新加载卡片
                        updateLoadMoreButton();
                    }
                });
            });
            
            observer.observe(tabContent, { attributes: true });
        }
        
        // 初始化
        // 1. 先应用默认排序 (日期降序)
        sortCards('date-desc');
        
        // 2. 初始渲染卡片
        resetAndRenderCards();
        
        // 3. 公开筛选方法，供搜索功能使用
        return {
            filterCards: filterCards,
            docType: docType,
            updateLoadMoreButton: updateLoadMoreButton
        };
    }

    // 搜索功能
    function setupSearch() {
        // 不再需要实现搜索功能，由全局搜索替代
        console.log('局部搜索功能已禁用，请使用全局搜索');
    }

    // 初始化标签页
    setupTabs();
    
    // 初始化所有文档类型的分页，并收集分页控制器
    const paginationControllers = {};
    document.querySelectorAll('.tab-content').forEach(content => {
        const docType = content.getAttribute('data-doc-type');
        paginationControllers[docType] = setupPagination(docType);
    });

    // 初始化搜索功能
    setupSearch();
});
