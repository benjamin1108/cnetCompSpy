// 全局变量
let statsData = null;
let detailsTable = null;
let comparisonTable = null;
let summaryTable = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 加载数据
    loadStatsData();
    
    // 刷新按钮点击事件
    document.getElementById('refreshBtn').addEventListener('click', function() {
        loadStatsData();
    });
    
    // 初始化下拉菜单
    initDropdowns();
    
    // 初始化过滤器
    initFilters();
    
    // 初始化标签页切换事件
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(e) {
            // 当切换到详细视图时，重新调整表格列宽
            if (e.target.id === 'details-tab' && detailsTable) {
                detailsTable.columns.adjust();
            }
        });
    });
});

// 初始化下拉菜单
function initDropdowns() {
    document.querySelectorAll('.filter-dropdown-toggle').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const menu = this.nextElementSibling;
            menu.classList.toggle('show');
        });
    });
    
    // 点击其他地方关闭下拉菜单
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.filter-dropdown')) {
            document.querySelectorAll('.filter-dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
}

// 初始化过滤器
function initFilters() {
    // 状态过滤器
    document.getElementById('status-all').addEventListener('change', function() {
        const checked = this.checked;
        document.querySelectorAll('#statusFilter input[type="checkbox"]:not(#status-all)').forEach(checkbox => {
            checkbox.checked = checked;
        });
        if (comparisonTable) {
            applyStatusFilter();
        }
    });
    
    document.querySelectorAll('#statusFilter input[type="checkbox"]:not(#status-all)').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateAllCheckbox('status');
            if (comparisonTable) {
                applyStatusFilter();
            }
        });
    });
    
    // 厂商过滤器
    document.getElementById('vendor-all').addEventListener('change', function() {
        const checked = this.checked;
        document.querySelectorAll('#vendorFilter input[type="checkbox"]:not(#vendor-all)').forEach(checkbox => {
            checkbox.checked = checked;
        });
        if (detailsTable) {
            applyVendorFilter();
        }
    });
    
    // 类型过滤器
    document.getElementById('type-all').addEventListener('change', function() {
        const checked = this.checked;
        document.querySelectorAll('#typeFilter input[type="checkbox"]:not(#type-all)').forEach(checkbox => {
            checkbox.checked = checked;
        });
        if (detailsTable) {
            applyTypeFilter();
        }
    });
    
    // 搜索框
    document.getElementById('detailSearch').addEventListener('input', function() {
        if (detailsTable) {
            detailsTable.search(this.value).draw();
        }
    });
    
    document.getElementById('comparisonSearch').addEventListener('input', function() {
        if (comparisonTable) {
            comparisonTable.search(this.value).draw();
        }
    });
}

// 更新"全部"复选框状态
function updateAllCheckbox(type) {
    const allCheckbox = document.getElementById(`${type}-all`);
    const checkboxes = document.querySelectorAll(`#${type}Filter input[type="checkbox"]:not(#${type}-all)`);
    const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);
    allCheckbox.checked = allChecked;
}

// 应用状态过滤器
function applyStatusFilter() {
    const showOk = document.getElementById('status-ok').checked;
    const showMissingMetadata = document.getElementById('status-missing-metadata').checked;
    const showMissingRaw = document.getElementById('status-missing-raw').checked;
    const showMissingAnalysis = document.getElementById('status-missing-analysis').checked;
    
    $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
        if (settings.nTable.id !== 'comparisonTable') return true;
        
        const status = data[3]; // 状态列
        
        if (status.includes('正常') && !showOk) return false;
        if (status.includes('缺少元数据') && !showMissingMetadata) return false;
        if (status.includes('缺少原始文件') && !showMissingRaw) return false;
        if (status.includes('缺少分析文件') && !showMissingAnalysis) return false;
        
        return true;
    });
    
    comparisonTable.draw();
    
    // 移除过滤器
    $.fn.dataTable.ext.search.pop();
}

// 应用厂商过滤器
function applyVendorFilter() {
    const vendorCheckboxes = document.querySelectorAll('#vendorFilter input[type="checkbox"]:not(#vendor-all)');
    const selectedVendors = Array.from(vendorCheckboxes)
        .filter(checkbox => checkbox.checked)
        .map(checkbox => checkbox.value);
    
    $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
        if (settings.nTable.id !== 'detailsTable') return true;
        
        const vendor = data[0]; // 厂商列
        
        return selectedVendors.includes(vendor);
    });
    
    detailsTable.draw();
    
    // 移除过滤器
    $.fn.dataTable.ext.search.pop();
}

// 应用类型过滤器
function applyTypeFilter() {
    const typeCheckboxes = document.querySelectorAll('#typeFilter input[type="checkbox"]:not(#type-all)');
    const selectedTypes = Array.from(typeCheckboxes)
        .filter(checkbox => checkbox.checked)
        .map(checkbox => checkbox.value);
    
    $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
        if (settings.nTable.id !== 'detailsTable') return true;
        
        const type = data[1]; // 类型列
        
        return selectedTypes.includes(type);
    });
    
    detailsTable.draw();
    
    // 移除过滤器
    $.fn.dataTable.ext.search.pop();
}

// 加载统计数据
function loadStatsData() {
    // 显示加载中状态
    document.getElementById('total-metadata').textContent = '-';
    document.getElementById('total-raw').textContent = '-';
    document.getElementById('total-analysis').textContent = '-';
    document.getElementById('total-mismatch').textContent = '-';
    
    document.getElementById('summaryTable').querySelector('tbody').innerHTML = '<tr><td colspan="7" class="text-center">加载中...</td></tr>';
    document.getElementById('detailsTable').querySelector('tbody').innerHTML = '<tr><td colspan="7" class="text-center">加载中...</td></tr>';
    
    // 发起AJAX请求获取数据
    fetch('/api/stats?detailed=true')
        .then(response => response.json())
        .then(data => {
            statsData = data;
            
            // 更新摘要统计
            updateSummaryStats(data);
            
            // 渲染摘要表格
            renderSummaryTable(data.summary);
            
            // 渲染详细表格
            renderDetailsTable(data.details);
            
            // 对比视图已移除
            
            // 更新过滤器选项
            updateFilterOptions(data);
        })
        .catch(error => {
            console.error('获取数据失败:', error);
            document.getElementById('summaryTable').querySelector('tbody').innerHTML = '<tr><td colspan="7" class="text-center text-danger">加载失败，请重试</td></tr>';
            document.getElementById('detailsTable').querySelector('tbody').innerHTML = '<tr><td colspan="7" class="text-center text-danger">加载失败，请重试</td></tr>';
        });
}

// 更新摘要统计
function updateSummaryStats(data) {
    let totalMetadata = 0;
    let totalRaw = 0;
    let totalAnalysis = 0;
    let totalMismatch = 0;
    
    data.summary.forEach(item => {
        totalMetadata += item.metadata_count;
        totalRaw += item.raw_count;
        totalAnalysis += item.analysis_count;
        
        if (!item.metadata_match || !item.analysis_match) {
            totalMismatch += Math.max(
                Math.abs(item.metadata_count - item.raw_count),
                Math.abs(item.raw_count - item.analysis_count)
            );
        }
    });
    
    document.getElementById('total-metadata').textContent = totalMetadata;
    document.getElementById('total-raw').textContent = totalRaw;
    document.getElementById('total-analysis').textContent = totalAnalysis;
    document.getElementById('total-mismatch').textContent = totalMismatch;
    
    // 根据不匹配数量设置颜色
    const mismatchBox = document.getElementById('mismatch-box');
    if (totalMismatch > 0) {
        mismatchBox.classList.add('danger');
        mismatchBox.classList.remove('success');
    } else {
        mismatchBox.classList.add('success');
        mismatchBox.classList.remove('danger');
    }
}

// 渲染摘要表格
function renderSummaryTable(summaryData) {
    const tableBody = document.getElementById('summaryTable').querySelector('tbody');
    tableBody.innerHTML = '';
    
    if (summaryData.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center">没有数据</td></tr>';
        return;
    }
    
    summaryData.forEach(item => {
        // 直接使用API返回的数据
        const metadata_count = item.metadata_count || 0;
        const raw_count = item.raw_count || 0;
        const analysis_count = item.analysis_count || 0;
        const in_crawler_count = item.in_crawler_count || 0;
        const in_analysis_count = item.in_analysis_count || 0;
        const has_file_count = item.has_file_count || 0;
        const tasks_done_count = item.tasks_done_count || 0;
        
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${item.vendor}</td>
            <td>${item.source_type}</td>
            <td>${raw_count}</td>
            <td>${in_crawler_count}</td>
            <td>${in_analysis_count}</td>
            <td>${has_file_count}</td>
            <td>${tasks_done_count}</td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // 初始化DataTable
    if (summaryTable) {
        summaryTable.destroy();
    }
    
    summaryTable = $('#summaryTable').DataTable({
        paging: false,
        searching: false,
        info: false,
        order: [[0, 'asc'], [1, 'asc']]
    });
}

// 渲染详细表格
function renderDetailsTable(detailsData) {
    const tableBody = document.getElementById('detailsTable').querySelector('tbody');
    tableBody.innerHTML = '';
    
    if (!detailsData || Object.keys(detailsData).length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center">没有详细数据</td></tr>';
        return;
    }
    
    // 准备表格数据
    const tableData = [];
    
    for (const vendor in detailsData) {
        for (const sourceType in detailsData[vendor]) {
            const files = detailsData[vendor][sourceType];
            
            files.forEach(file => {
                // 直接使用API返回的数据
                const in_crawler = file.in_crawler_metadata !== undefined ? file.in_crawler_metadata : false;
                const in_analysis = file.in_analysis_metadata !== undefined ? file.in_analysis_metadata : false;
                const has_file = file.has_analysis !== undefined ? file.has_analysis : false;
                const tasks_done = file.tasks_completed !== undefined ? file.tasks_completed : false;
                
                tableData.push([
                    vendor,
                    sourceType,
                    `<span class="filename" title="${file.filename}">${file.filename}</span>`,
                    getStatusIcon(in_crawler),
                    getStatusIcon(in_analysis),
                    getStatusIcon(has_file),
                    getStatusIcon(tasks_done)
                ]);
            });
        }
    }
    
    // 初始化DataTable
    if (detailsTable) {
        detailsTable.destroy();
    }
    
    detailsTable = $('#detailsTable').DataTable({
        data: tableData,
        columns: [
            { title: 'Vendor' },
            { title: 'Type' },
            { title: 'File' },
            { title: 'Meta-C' },
            { title: 'Meta-A' },
            { title: 'AIFileExist' },
            { title: 'AITaskDone' }
        ],
        order: [[0, 'asc'], [1, 'asc'], [2, 'asc']],
        pageLength: 25,
        language: {
            search: "搜索:",
            lengthMenu: "显示 _MENU_ 条记录",
            info: "显示第 _START_ 至 _END_ 条记录，共 _TOTAL_ 条",
            infoEmpty: "没有记录",
            infoFiltered: "(从 _MAX_ 条记录过滤)",
            paginate: {
                first: "首页",
                last: "末页",
                next: "下一页",
                previous: "上一页"
            }
        }
    });
    
    // 更新厂商和类型过滤器选项
    updateVendorAndTypeOptions(detailsData);
}

// 渲染对比表格
function renderComparisonTable(comparisonData) {
    const tableBody = document.getElementById('comparisonTable').querySelector('tbody');
    tableBody.innerHTML = '';
    
    if (!comparisonData || Object.keys(comparisonData).length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center">没有对比数据</td></tr>';
        return;
    }
    
    // 准备表格数据
    const tableData = [];
    
    for (const vendor in comparisonData) {
        for (const sourceType in comparisonData[vendor]) {
            const files = comparisonData[vendor][sourceType];
            
            files.forEach(file => {
                // 确保我们正确处理API返回的数据
                const in_crawler = file.in_crawler_metadata !== undefined ? file.in_crawler_metadata : (file.in_metadata || false);
                const in_analysis = file.in_analysis_metadata !== undefined ? file.in_analysis_metadata : false;
                const has_file = file.analysis_exists !== undefined ? file.analysis_exists : (file.has_analysis || false);
                const tasks_done = file.tasks_completed !== undefined ? file.tasks_completed : false;
                
                tableData.push([
                    vendor,
                    sourceType,
                    `<span class="filename" title="${file.filename}">${file.filename}</span>`,
                    getStatusIcon(in_crawler),
                    getStatusIcon(in_analysis),
                    getStatusIcon(has_file),
                    getStatusIcon(tasks_done)
                ]);
            });
        }
    }
    
    // 初始化DataTable
    if (comparisonTable) {
        comparisonTable.destroy();
    }
    
    comparisonTable = $('#comparisonTable').DataTable({
        data: tableData,
        columns: [
            { title: 'Vendor' },
            { title: 'Type' },
            { title: 'File' },
            { title: 'Meta-C' },
            { title: 'Meta-A' },
            { title: 'AIFileExist' },
            { title: 'AITaskDone' }
        ],
        order: [[0, 'asc'], [1, 'asc'], [2, 'asc']],
        pageLength: 25,
        language: {
            search: "搜索:",
            lengthMenu: "显示 _MENU_ 条记录",
            info: "显示第 _START_ 至 _END_ 条记录，共 _TOTAL_ 条",
            infoEmpty: "没有记录",
            infoFiltered: "(从 _MAX_ 条记录过滤)",
            paginate: {
                first: "首页",
                last: "末页",
                next: "下一页",
                previous: "上一页"
            }
        }
    });
}

// 更新厂商和类型过滤器选项
function updateVendorAndTypeOptions(detailsData) {
    const vendors = new Set();
    const types = new Set();
    
    for (const vendor in detailsData) {
        vendors.add(vendor);
        
        for (const sourceType in detailsData[vendor]) {
            types.add(sourceType);
        }
    }
    
    // 更新厂商过滤器
    const vendorMenu = document.querySelector('#vendorFilter .filter-dropdown-menu');
    const vendorAllItem = vendorMenu.querySelector('.filter-dropdown-item');
    vendorMenu.innerHTML = '';
    vendorMenu.appendChild(vendorAllItem);
    
    vendors.forEach(vendor => {
        const item = document.createElement('div');
        item.className = 'filter-dropdown-item';
        item.innerHTML = `<input type="checkbox" id="vendor-${vendor}" value="${vendor}" checked> ${vendor}`;
        vendorMenu.appendChild(item);
        
        item.querySelector('input').addEventListener('change', function() {
            updateAllCheckbox('vendor');
            if (detailsTable) {
                applyVendorFilter();
            }
        });
    });
    
    // 更新类型过滤器
    const typeMenu = document.querySelector('#typeFilter .filter-dropdown-menu');
    const typeAllItem = typeMenu.querySelector('.filter-dropdown-item');
    typeMenu.innerHTML = '';
    typeMenu.appendChild(typeAllItem);
    
    types.forEach(type => {
        const item = document.createElement('div');
        item.className = 'filter-dropdown-item';
        item.innerHTML = `<input type="checkbox" id="type-${type}" value="${type}" checked> ${type}`;
        typeMenu.appendChild(item);
        
        item.querySelector('input').addEventListener('change', function() {
            updateAllCheckbox('type');
            if (detailsTable) {
                applyTypeFilter();
            }
        });
    });
}

// 更新过滤器选项
function updateFilterOptions(data) {
    // 这里可以根据数据动态更新过滤器选项
}

// 获取状态图标
function getStatusIcon(status) {
    if (status) {
        return '<i class="bi bi-check-circle-fill status-icon status-icon-success"></i>';
    } else {
        return '<i class="bi bi-x-circle-fill status-icon status-icon-danger"></i>';
    }
}

// 获取状态标签
function getStatusBadge(status) {
    switch (status) {
        case 'ok':
            return '<span class="status-badge status-badge-success">正常</span>';
        case 'missing_metadata':
            return '<span class="status-badge status-badge-danger">缺少元数据</span>';
        case 'missing_raw':
            return '<span class="status-badge status-badge-danger">缺少原始文件</span>';
        case 'missing_analysis':
            return '<span class="status-badge status-badge-warning">缺少分析文件</span>';
        default:
            return '<span class="status-badge status-badge-danger">未知</span>';
    }
}
