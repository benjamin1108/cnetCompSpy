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

    // 分页功能
    function setupPagination(docType) {
        const cardsContainer = document.getElementById(`doc-cards-${docType}`);
        const paginationContainer = document.getElementById(`pagination-${docType}`);
        const cards = Array.from(cardsContainer.querySelectorAll('.doc-card'));
        const itemsPerPage = calculateItemsPerPage();
        let currentPage = 1;
        let filteredCards = [...cards]; // 使用展开运算符创建原始数组的真正副本

        function calculateItemsPerPage() {
            // 从URL参数中获取显示模式
            const urlParams = new URLSearchParams(window.location.search);
            const viewMode = urlParams.get('view');
            
            // 如果URL中指定了"all"，则显示全部文章
            if (viewMode === 'all') {
                return 1000; // 设置一个很大的数字，实际上相当于显示全部
            }
            
            // 根据设备屏幕宽度调整每页项目数
            const isMobile = window.innerWidth <= 768;
            const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
            
            // 默认值 - 可以根据需要调整
            if (isMobile) {
                // 移动端每页显示较多文章，但不是全部
                return isIOS ? 30 : 25;
            } else {
                // 桌面端按屏幕高度计算，但至少显示15个
                const cardHeight = 150;
                const containerHeight = window.innerHeight * 0.6;
                const cardsPerRow = 3;
                return Math.max(15, Math.floor(containerHeight / cardHeight) * cardsPerRow);
            }
        }

        function renderPage(page) {
            currentPage = page;
            const startIndex = (page - 1) * itemsPerPage;
            const endIndex = startIndex + itemsPerPage;
            const pageCards = filteredCards.slice(startIndex, endIndex);

            // 清空容器前保存当前排序选项
            const sortSelect = document.getElementById(`sort-${docType}`);
            const currentSortOption = sortSelect ? sortSelect.value : 'date-desc';

            cardsContainer.innerHTML = '';
            
            // 检测是否为移动设备
            const isMobile = window.innerWidth <= 768;
            const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
            
            pageCards.forEach(card => {
                const cardClone = card.cloneNode(true);
                
                // 在移动设备上增强触摸体验
                if (isMobile) {
                    // 找到卡片中的链接
                    const cardLink = cardClone.querySelector('.doc-title a');
                    const cardUrl = cardLink ? cardLink.getAttribute('href') : null;
                    
                    if (cardUrl) {
                        // 在整个卡片上添加点击事件
                        cardClone.style.cursor = 'pointer';
                        cardClone.addEventListener('click', function(e) {
                            // 如果点击的不是链接本身，则触发链接点击
                            if (e.target !== cardLink) {
                                window.location.href = cardUrl;
                            }
                        });
                        
                        // 添加触摸反馈效果
                        cardClone.addEventListener('touchstart', function() {
                            this.style.opacity = '0.8';
                            this.style.transform = 'scale(0.98)';
                        });
                        
                        cardClone.addEventListener('touchend', function() {
                            this.style.opacity = '1';
                            this.style.transform = '';
                        });
                    }
                }
                
                cardsContainer.appendChild(cardClone);
            });

            renderPaginationControls(filteredCards.length);
            
            // 在iOS设备上滚动到页面顶部
            if (isIOS && currentPage > 1) {
                const tabContent = cardsContainer.closest('.tab-content');
                if (tabContent) {
                    tabContent.scrollIntoView({ behavior: 'smooth' });
                }
            }
        }

        function renderPaginationControls(totalItems) {
            const totalPages = Math.ceil(totalItems / itemsPerPage);
            paginationContainer.innerHTML = '';

            // 检测是否为移动设备，及设备类型
            const isMobile = window.innerWidth <= 768;
            const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
            
            // 添加总文章数和当前页信息
            const infoDiv = document.createElement('div');
            infoDiv.className = 'pagination-info';
            
            // 创建分页信息文本，在移动设备上简化显示
            const infoText = document.createElement('span');
            if (isMobile) {
                infoText.textContent = `共 ${totalItems} 篇 (${currentPage}/${Math.max(1, totalPages)}页)`;
            } else {
                infoText.textContent = `共 ${totalItems} 篇文档，第 ${currentPage}/${Math.max(1, totalPages)} 页`;
            }
            infoDiv.appendChild(infoText);
            
            // 检查当前是否已经是"显示全部"模式
            const urlParams = new URLSearchParams(window.location.search);
            const isViewingAll = urlParams.get('view') === 'all';
            
            // 如果不是"显示全部"模式且文档数量足够多，添加"显示全部"链接
            if (!isViewingAll && totalItems > itemsPerPage) {
                const viewAllLink = document.createElement('a');
                viewAllLink.className = 'view-all-link';
                
                // 移动设备上使用更清晰的文本
                viewAllLink.textContent = isMobile ? '👁️ 显示全部文章' : '显示全部';
                viewAllLink.href = '?view=all'; // 添加view=all参数
                viewAllLink.title = '显示所有文档，不分页';
                
                // 保留其他URL参数
                const currentParams = new URLSearchParams(window.location.search);
                currentParams.set('view', 'all');
                viewAllLink.href = `${window.location.pathname}?${currentParams.toString()}`;
                
                // 添加到信息div
                infoDiv.appendChild(viewAllLink);
            } 
            // 如果已经是"显示全部"模式，添加"分页查看"链接
            else if (isViewingAll) {
                const viewPaginatedLink = document.createElement('a');
                viewPaginatedLink.className = 'view-all-link';
                
                // 移动设备上使用更清晰的文本
                viewPaginatedLink.textContent = isMobile ? '📄 切换到分页模式' : '分页查看';
                
                // 移除view参数，保留其他参数
                const currentParams = new URLSearchParams(window.location.search);
                currentParams.delete('view');
                const newUrl = currentParams.toString() 
                    ? `${window.location.pathname}?${currentParams.toString()}`
                    : window.location.pathname;
                
                viewPaginatedLink.href = newUrl;
                viewPaginatedLink.title = '使用分页查看文档';
                
                // 添加到信息div
                infoDiv.appendChild(viewPaginatedLink);
            }
            
            paginationContainer.appendChild(infoDiv);
            
            // 在移动设备上总是显示分页控件，即使只有一页
            // 这样用户总能看到"显示全部"选项
            if (totalPages <= 1 && !isMobile) {
                return;
            }

            const prevButton = document.createElement('button');
            prevButton.textContent = '上一页';
            prevButton.disabled = currentPage === 1;
            prevButton.addEventListener('click', () => {
                if (currentPage > 1) renderPage(currentPage - 1);
            });
            paginationContainer.appendChild(prevButton);

            // 移动端显示较少的页码按钮，但iOS设备显示更多
            const maxVisiblePages = isMobile ? (isIOS ? 5 : 3) : 5;
            
            let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
            let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

            if (endPage - startPage < maxVisiblePages - 1) {
                startPage = Math.max(1, endPage - maxVisiblePages + 1);
            }

            for (let i = startPage; i <= endPage; i++) {
                const button = document.createElement('button');
                button.textContent = i;
                button.classList.toggle('active', i === currentPage);
                button.addEventListener('click', () => renderPage(i));
                paginationContainer.appendChild(button);
            }

            const nextButton = document.createElement('button');
            nextButton.textContent = '下一页';
            nextButton.disabled = currentPage === totalPages;
            nextButton.addEventListener('click', () => {
                if (currentPage < totalPages) renderPage(currentPage + 1);
            });
            paginationContainer.appendChild(nextButton);
        }

        // 排序功能
        const sortSelect = document.getElementById(`sort-${docType}`);
        if (sortSelect) {
            sortSelect.addEventListener('change', function() {
                const sortOption = this.value;
                sortCards(sortOption);
                renderPage(1); // 排序后重新渲染第一页
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
            
            // 重新渲染第一页
            renderPage(1);
        }

        // 初始化
        // 1. 先应用默认排序 (日期降序)
        sortCards('date-desc');
        
        // 2. 渲染第一页
        renderPage(1);
        
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
