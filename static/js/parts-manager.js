// Управление запчастями и категориями - Felix Hub
let allParts = [];
let allCategories = [];

// Переключение вкладок
function switchTab(tab, event) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    
    if (tab === 'parts') {
        document.getElementById('partsTab').style.display = 'block';
        document.getElementById('categoriesTab').style.display = 'none';
        loadParts();
    } else {
        document.getElementById('partsTab').style.display = 'none';
        document.getElementById('categoriesTab').style.display = 'block';
        loadCategories();
    }
}

// Загрузка категорий
async function loadCategories() {
    try {
        const lang = getCurrentLanguage ? getCurrentLanguage() : 'ru';
        const response = await fetch(`/api/categories?lang=${lang}`);
        if (!response.ok) throw new Error('Ошибка загрузки категорий');
        
        allCategories = await response.json();
        updateStats();
        renderCategories();
        updateCategoryFilters();
    } catch (error) {
        console.error(error);
        const message = t ? t('error_loading_categories') : 'Ошибка загрузки категорий';
        showAlert(message + ': ' + error.message, 'error');
    }
}

// Отображение категорий
function renderCategories() {
    const container = document.getElementById('categoriesContainer');
    
    if (allCategories.length === 0) {
        const noCategories = t ? t('no_categories') : 'Категорий нет';
        const noCategoriesDesc = t ? t('no_categories_desc') : 'Добавьте первую категорию или импортируйте каталог';
        
        container.innerHTML = `
            <div class="empty-state">
                <div style="font-size: 64px;">📁</div>
                <h3>${noCategories}</h3>
                <p>${noCategoriesDesc}</p>
            </div>
        `;
        return;
    }
    
    let html = `
        <table>
            <thead>
                <tr>
                    <th style="width: 60px;">${t ? t('table_id') : 'ID'}</th>
                    <th>${t ? t('table_name') : 'Название'}</th>
                    <th style="width: 100px;">${t ? t('table_parts_count') : 'Запчастей'}</th>
                    <th style="width: 100px;">${t ? t('table_active_count') : 'Активных'}</th>
                    <th style="width: 100px;">${t ? t('table_sort_order') : 'Порядок'}</th>
                    <th style="width: 120px;">${t ? t('table_status') : 'Статус'}</th>
                    <th style="width: 300px;">${t ? t('table_actions') : 'Действия'}</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    allCategories.forEach(cat => {
        const activeText = t ? t('active') : 'Активна';
        const inactiveText = t ? t('inactive') : 'Неактивна';
        const editText = t ? t('edit') : 'Редактировать';
        
        // Формируем отображение с переводами
        const mainName = cat.name_ru || cat.name || 'N/A';
        const translations = [];
        if (cat.name_en) translations.push(`EN: ${cat.name_en}`);
        if (cat.name_he) translations.push(`HE: ${cat.name_he}`);
        
        html += `
            <tr class="${!cat.is_active ? 'inactive' : ''}">
                <td><strong>#${cat.id}</strong></td>
                <td>
                    <strong>${mainName}</strong>
                    ${translations.length > 0 ? `<br><small style="color: #7f8c8d;">${translations.join(' | ')}</small>` : ''}
                </td>
                <td>${cat.parts_count || 0}</td>
                <td>${cat.active_parts_count || 0}</td>
                <td>${cat.sort_order}</td>
                <td>
                    <span class="status-badge ${cat.is_active ? 'status-active' : 'status-inactive'}">
                        ${cat.is_active ? activeText : inactiveText}
                    </span>
                </td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="editCategory(${cat.id})">
                        ✏️ ${editText}
                    </button>
                    <button class="btn btn-warning btn-sm" onclick="toggleCategoryActive(${cat.id})">
                        ${cat.is_active ? '🔒' : '🔓'}
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteCategory(${cat.id})">
                        🗑️
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

// Загрузка запчастей
async function loadParts() {
    try {
        const statusFilter = document.getElementById('statusFilter').value;
        const activeOnly = statusFilter === 'active' ? 'true' : 'false';
        const lang = getCurrentLanguage ? getCurrentLanguage() : 'ru';
        
        const response = await fetch(`/api/parts?active_only=${activeOnly}&lang=${lang}`);
        if (!response.ok) throw new Error('Ошибка загрузки запчастей');
        
        allParts = await response.json();
        
        if (statusFilter === 'inactive') {
            const allResponse = await fetch(`/api/parts?active_only=false&lang=${lang}`);
            const allData = await allResponse.json();
            allParts = allData.filter(p => !p.is_active);
        }
        
        updateStats();
        renderParts();
    } catch (error) {
        console.error(error);
        const message = t ? t('error_loading_parts') : 'Ошибка загрузки запчастей';
        showAlert(message + ': ' + error.message, 'error');
    }
}

// Отображение запчастей
function renderParts() {
    const container = document.getElementById('partsContainer');
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const categoryFilter = document.getElementById('categoryFilter').value;
    
    let filteredParts = allParts;
    
    if (categoryFilter !== 'all') {
        filteredParts = filteredParts.filter(p => p.category === categoryFilter);
    }
    
    if (searchTerm) {
        filteredParts = filteredParts.filter(p => 
            p.name.toLowerCase().includes(searchTerm) ||
            p.category.toLowerCase().includes(searchTerm)
        );
    }
    
    if (filteredParts.length === 0) {
        const noParts = t ? t('no_parts') : 'Запчасти не найдены';
        const noPartsDesc = t ? t('no_parts_desc') : 'Попробуйте изменить фильтры';
        
        container.innerHTML = `
            <div class="empty-state">
                <div style="font-size: 64px;">📦</div>
                <h3>${noParts}</h3>
                <p>${noPartsDesc}</p>
            </div>
        `;
        return;
    }
    
    let html = `
        <table>
            <thead>
                <tr>
                    <th style="width: 60px;">${t ? t('table_id') : 'ID'}</th>
                    <th>${t ? t('table_name') : 'Название'}</th>
                    <th style="width: 200px;">${t ? t('table_category') : 'Категория'}</th>
                    <th style="width: 100px;">${t ? t('table_sort_order') : 'Порядок'}</th>
                    <th style="width: 120px;">${t ? t('table_status') : 'Статус'}</th>
                    <th style="width: 300px;">${t ? t('table_actions') : 'Действия'}</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    filteredParts.forEach(part => {
        // Отображаем названия на всех языках
        const displayName = part.name_ru || part.name || 'N/A';
        const translations = [];
        if (part.name_en) translations.push(`EN: ${part.name_en}`);
        if (part.name_he) translations.push(`HE: ${part.name_he}`);
        
        const activeText = t ? t('active') : 'Активна';
        const inactiveText = t ? t('inactive') : 'Неактивна';
        const editText = t ? t('edit') : 'Редактировать';
        
        html += `
            <tr class="${!part.is_active ? 'inactive' : ''}">
                <td><strong>#${part.id}</strong></td>
                <td>
                    <strong>${displayName}</strong>
                    ${translations.length > 0 ? `<br><small style="color: #7f8c8d;">${translations.join(' | ')}</small>` : ''}
                </td>
                <td>📁 ${part.category}</td>
                <td>${part.sort_order}</td>
                <td>
                    <span class="status-badge ${part.is_active ? 'status-active' : 'status-inactive'}">
                        ${part.is_active ? activeText : inactiveText}
                    </span>
                </td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="editPart(${part.id})">
                        ✏️ ${editText}
                    </button>
                    <button class="btn btn-warning btn-sm" onclick="togglePartActive(${part.id})">
                        ${part.is_active ? '🔒' : '🔓'}
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deletePart(${part.id})">
                        🗑️
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

// Обновление фильтров категорий
function updateCategoryFilters() {
    const categoryFilter = document.getElementById('categoryFilter');
    const partCategory = document.getElementById('partCategory');
    
    // Сохраняем текущие значения
    const currentFilterValue = categoryFilter.value;
    const currentPartCategoryValue = partCategory.value;
    
    // Обновляем фильтр категорий
    const allCategoriesText = t ? t('all_categories') : 'Все категории';
    categoryFilter.innerHTML = `<option value="all">${allCategoriesText}</option>`;
    
    allCategories
        .filter(c => c.is_active)
        .forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.name;
            option.textContent = cat.name;
            if (cat.name === currentFilterValue) option.selected = true;
            categoryFilter.appendChild(option);
        });
    
    // Обновляем селект категорий в модальном окне, сохраняя выбранное значение
    const chooseCategoryText = t ? t('choose_category') : 'Выберите категорию';
    partCategory.innerHTML = `<option value="">${chooseCategoryText}</option>`;
    allCategories
        .filter(c => c.is_active)
        .forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.name;
            option.textContent = cat.name;
            if (cat.name === currentPartCategoryValue) option.selected = true;
            partCategory.appendChild(option);
        });
}

// Обновление статистики
function updateStats() {
    document.getElementById('totalCategories').textContent = allCategories.length;
    document.getElementById('totalParts').textContent = allParts.length;
    document.getElementById('activeParts').textContent = allParts.filter(p => p.is_active).length;
}

// === КАТЕГОРИИ ===
function openAddCategoryModal() {
    const title = t ? t('add_category_title') : 'Добавить категорию';
    document.getElementById('categoryModalTitle').textContent = title;
    document.getElementById('categoryForm').reset();
    document.getElementById('categoryId').value = '';
    document.getElementById('categoryIsActive').checked = true;
    document.getElementById('categoryModal').classList.add('active');
}

async function editCategory(id) {
    try {
        const response = await fetch(`/api/admin/categories/${id}`);
        const category = await response.json();
        
        const title = t ? t('edit_category_title') : 'Редактировать категорию';
        document.getElementById('categoryModalTitle').textContent = title;
        document.getElementById('categoryId').value = category.id;
        document.getElementById('categoryName').value = category.name_ru || category.name || '';
        document.getElementById('categoryNameEn').value = category.name_en || '';
        document.getElementById('categoryNameHe').value = category.name_he || '';
        document.getElementById('categorySortOrder').value = category.sort_order;
        document.getElementById('categoryIsActive').checked = category.is_active;
        
        document.getElementById('categoryModal').classList.add('active');
    } catch (error) {
        const message = t ? t('error_loading_category') : 'Ошибка загрузки категории';
        showAlert(message, 'error');
    }
}

async function saveCategory(event) {
    event.preventDefault();
    
    const id = document.getElementById('categoryId').value;
    const data = {
        name: document.getElementById('categoryName').value,
        name_ru: document.getElementById('categoryName').value,
        name_en: document.getElementById('categoryNameEn').value,
        name_he: document.getElementById('categoryNameHe').value,
        sort_order: parseInt(document.getElementById('categorySortOrder').value) || 0,
        is_active: document.getElementById('categoryIsActive').checked
    };
    
    try {
        const url = id ? `/api/admin/categories/${id}` : '/api/admin/categories';
        const method = id ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || 'Ошибка сохранения');
        
        const successMessage = id 
            ? (t ? t('category_updated') : 'Категория обновлена')
            : (t ? t('category_added') : 'Категория добавлена');
        showAlert(successMessage, 'success');
        closeCategoryModal();
        loadCategories();
        loadParts();
    } catch (error) {
        const errorMessage = t ? t('error') : 'Ошибка';
        showAlert(errorMessage + ': ' + error.message, 'error');
    }
}

async function toggleCategoryActive(id) {
    try {
        const response = await fetch(`/api/admin/categories/${id}/toggle-active`, {
            method: 'PUT'
        });
        if (!response.ok) throw new Error('Ошибка');
        
        const message = t ? t('category_status_changed') : 'Статус категории изменен';
        showAlert(message, 'success');
        loadCategories();
    } catch (error) {
        const errorMessage = t ? t('error') : 'Ошибка';
        showAlert(errorMessage + ': ' + error.message, 'error');
    }
}

async function deleteCategory(id) {
    const confirmMessage = t ? t('confirm_delete_category') : 'Удалить категорию? Это возможно только если в ней нет запчастей.';
    if (!confirm(confirmMessage)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/categories/${id}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || 'Ошибка удаления');
        
        const successMessage = t ? t('category_deleted') : 'Категория удалена';
        showAlert(successMessage, 'success');
        loadCategories();
    } catch (error) {
        const errorMessage = t ? t('error') : 'Ошибка';
        showAlert(errorMessage + ': ' + error.message, 'error');
    }
}

function closeCategoryModal() {
    document.getElementById('categoryModal').classList.remove('active');
}

// === ЗАПЧАСТИ ===
function openAddPartModal() {
    const title = t ? t('add_part_title') : 'Добавить запчасть';
    document.getElementById('partModalTitle').textContent = title;
    document.getElementById('partForm').reset();
    document.getElementById('partId').value = '';
    document.getElementById('partIsActive').checked = true;
    document.getElementById('partModal').classList.add('active');
}

async function editPart(id) {
    try {
        const response = await fetch(`/api/admin/parts/${id}`);
        const part = await response.json();
        
        const title = t ? t('edit_part_title') : 'Редактировать запчасть';
        document.getElementById('partModalTitle').textContent = title;
        document.getElementById('partId').value = part.id;
        
        // Заполняем поля для всех языков
        document.getElementById('partNameRu').value = part.name_ru || part.name || '';
        document.getElementById('partNameEn').value = part.name_en || '';
        document.getElementById('partNameHe').value = part.name_he || '';
        
        document.getElementById('partDescRu').value = part.description_ru || '';
        document.getElementById('partDescEn').value = part.description_en || '';
        document.getElementById('partDescHe').value = part.description_he || '';
        
        document.getElementById('partCategory').value = part.category;
        document.getElementById('partSortOrder').value = part.sort_order;
        document.getElementById('partIsActive').checked = part.is_active;
        
        document.getElementById('partModal').classList.add('active');
    } catch (error) {
        const message = t ? t('error_loading_part') : 'Ошибка загрузки запчасти';
        showAlert(message, 'error');
    }
}

async function savePart(event) {
    event.preventDefault();
    
    const id = document.getElementById('partId').value;
    const data = {
        name_ru: document.getElementById('partNameRu').value,
        name_en: document.getElementById('partNameEn').value,
        name_he: document.getElementById('partNameHe').value,
        description_ru: document.getElementById('partDescRu').value,
        description_en: document.getElementById('partDescEn').value,
        description_he: document.getElementById('partDescHe').value,
        category: document.getElementById('partCategory').value,
        sort_order: parseInt(document.getElementById('partSortOrder').value) || 0,
        is_active: document.getElementById('partIsActive').checked
    };
    
    try {
        const url = id ? `/api/admin/parts/${id}` : '/api/admin/parts';
        const method = id ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || 'Ошибка сохранения');
        
        const successMessage = id 
            ? (t ? t('part_updated') : 'Запчасть обновлена')
            : (t ? t('part_added') : 'Запчасть добавлена');
        showAlert(successMessage, 'success');
        closePartModal();
        loadParts();
    } catch (error) {
        const errorMessage = t ? t('error') : 'Ошибка';
        showAlert(errorMessage + ': ' + error.message, 'error');
    }
}

async function togglePartActive(id) {
    try {
        const response = await fetch(`/api/admin/parts/${id}/toggle-active`, {
            method: 'PUT'
        });
        if (!response.ok) throw new Error('Ошибка');
        
        const message = t ? t('part_status_changed') : 'Статус запчасти изменен';
        showAlert(message, 'success');
        loadParts();
    } catch (error) {
        const errorMessage = t ? t('error') : 'Ошибка';
        showAlert(errorMessage + ': ' + error.message, 'error');
    }
}

async function deletePart(id) {
    const confirmMessage = t ? t('confirm_delete_part') : 'Удалить запчасть?';
    if (!confirm(confirmMessage)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/parts/${id}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Ошибка удаления');
        
        const successMessage = t ? t('part_deleted') : 'Запчасть удалена';
        showAlert(successMessage, 'success');
        loadParts();
    } catch (error) {
        const errorMessage = t ? t('error') : 'Ошибка';
        showAlert(errorMessage + ': ' + error.message, 'error');
    }
}

function closePartModal() {
    document.getElementById('partModal').classList.remove('active');
}

// === ИМПОРТ ===
async function importDefaultCatalog() {
    const confirmMessage = t ? t('confirm_import_catalog') : 'Импортировать дефолтный каталог? Существующие записи не будут затронуты.';
    if (!confirm(confirmMessage)) {
        return;
    }
    
    try {
        const response = await fetch('/api/admin/parts/import-default', {
            method: 'POST'
        });
        
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || 'Ошибка импорта');
        
        showAlert(result.message, 'success');
        loadCategories();
        loadParts();
    } catch (error) {
        const errorMessage = t ? t('error') : 'Ошибка';
        showAlert(errorMessage + ': ' + error.message, 'error');
    }
}

// === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
function showAlert(message, type) {
    const container = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    container.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Поиск по мере ввода
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', renderParts);
    }
    
    // Закрытие модальных окон по клику вне их
    document.getElementById('categoryModal').addEventListener('click', function(e) {
        if (e.target === this) closeCategoryModal();
    });
    
    document.getElementById('partModal').addEventListener('click', function(e) {
        if (e.target === this) closePartModal();
    });
    
    // Загрузка при старте
    loadCategories();
    loadParts();
});
