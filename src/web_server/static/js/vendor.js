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
        let filteredCards = cards;

        function calculateItemsPerPage() {
            const cardHeight = 150; // 假设每个卡片的高度大约为150px
            const containerHeight = window.innerHeight * 0.6; // 使用视口高度的60%作为容器高度
            return Math.floor(containerHeight / cardHeight) * 3; // 假设每行有3个卡片
        }

        function renderPage(page) {
            currentPage = page;
            const startIndex = (page - 1) * itemsPerPage;
            const endIndex = startIndex + itemsPerPage;
            const pageCards = filteredCards.slice(startIndex, endIndex);

            cardsContainer.innerHTML = '';
            pageCards.forEach(card => cardsContainer.appendChild(card));

            renderPaginationControls(filteredCards.length);
        }

        function renderPaginationControls(totalItems) {
            const totalPages = Math.ceil(totalItems / itemsPerPage);
            paginationContainer.innerHTML = '';

            if (totalPages <= 1) return;

            const prevButton = document.createElement('button');
            prevButton.textContent = '上一页';
            prevButton.disabled = currentPage === 1;
            prevButton.addEventListener('click', () => {
                if (currentPage > 1) renderPage(currentPage - 1);
            });
            paginationContainer.appendChild(prevButton);

            const maxVisiblePages = 5;
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
        sortSelect.addEventListener('change', function() {
            const sortOption = this.value;
            sortCards(sortOption);
            renderPage(1);
        });

        function sortCards(option) {
            filteredCards.sort((a, b) => {
                if (option === 'date-desc') {
                    return new Date(b.getAttribute('data-date') || '1970-01-01') - new Date(a.getAttribute('data-date') || '1970-01-01');
                } else if (option === 'date-asc') {
                    return new Date(a.getAttribute('data-date') || '1970-01-01') - new Date(b.getAttribute('data-date') || '1970-01-01');
                } else if (option === 'title-asc') {
                    return a.getAttribute('data-title').localeCompare(b.getAttribute('data-title'));
                } else if (option === 'title-desc') {
                    return b.getAttribute('data-title').localeCompare(a.getAttribute('data-title'));
                }
            });
        }

        // 初始化过滤卡片
        function initializeFilteredCards() {
            filteredCards = cards;
        }

        // 初始化并渲染
        initializeFilteredCards();
        // 默认按日期降序排序，确保最新在前
        sortCards('date-desc');
        renderPage(1);
    }

    // 搜索功能
    function setupSearch() {
        const searchInput = document.getElementById('document-search');
        const allCards = Array.from(document.querySelectorAll('.doc-card'));

        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            allCards.forEach(card => {
                const title = card.getAttribute('data-title');
                if (title.includes(searchTerm)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });

            // 重新渲染分页
            document.querySelectorAll('.tab-content').forEach(content => {
                const docType = content.getAttribute('data-doc-type');
                setupPagination(docType);
            });
        });
    }

    // 初始化标签页
    setupTabs();

    // 初始化所有文档类型的分页
    document.querySelectorAll('.tab-content').forEach(content => {
        const docType = content.getAttribute('data-doc-type');
        setupPagination(docType);
    });

    // 初始化搜索功能
    setupSearch();
});
