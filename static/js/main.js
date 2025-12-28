document.addEventListener('DOMContentLoaded', () => {
    initScrollProgress();
    initParticles();
    createDeleteModal();
    createActionsModal();
});

// =============================================================================
// SCROLL PROGRESS BAR
// =============================================================================

function initScrollProgress() {
    window.addEventListener('scroll', () => {
        const scrollProgress = document.getElementById('scrollProgress');
        if (scrollProgress) {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const progress = (scrollTop / scrollHeight) * 100;
            scrollProgress.style.width = progress + '%';
        }
    });
}

// =============================================================================
// FLOATING PARTICLES
// =============================================================================

function initParticles() {
    const particlesContainer = document.getElementById('particles');
    if (particlesContainer) {
        const particleCount = particlesContainer.closest('body').querySelector('.gallery') ? 50 : 30;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = Math.random() * 100 + '%';
            particle.style.setProperty('--tx', (Math.random() - 0.5) * 200 + 'px');
            particle.style.setProperty('--ty', (Math.random() - 0.5) * 200 + 'px');
            particle.style.animationDelay = Math.random() * 20 + 's';
            particle.style.animationDuration = (Math.random() * 10 + 15) + 's';
            particlesContainer.appendChild(particle);
        }
    }
}

// =============================================================================
// МОДАЛЬНОЕ ОКНО ПРОСМОТРА ВИДЕО
// =============================================================================

function openVideoModal(videoUrl, title, description) {
    const modal = document.getElementById('videoModal');
    const player = document.getElementById('videoPlayer');
    const titleEl = document.getElementById('videoModalTitle');
    const descEl = document.getElementById('videoModalDesc');
    
    if (modal && player && titleEl) {
        player.src = videoUrl;
        titleEl.textContent = title || 'Видео';
        
        if (descEl && description) {
            descEl.textContent = description;
            descEl.parentElement.style.display = 'block';
        } else if (descEl) {
            descEl.parentElement.style.display = 'none';
        }
        
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
        
        player.play().catch(() => {
            console.log('Автовоспроизведение заблокировано');
        });
    }
}

function closeVideoModal() {
    const modal = document.getElementById('videoModal');
    const player = document.getElementById('videoPlayer');
    
    if (modal && player) {
        player.pause();
        player.src = '';
        modal.classList.remove('open');
        document.body.style.overflow = '';
    }
}

// Закрытие по ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeVideoModal();
        closeActionsModal();
        closeDeleteModal();
    }
});

// =============================================================================
// МОДАЛЬНОЕ ОКНО ДЕЙСТВИЙ С ВИДЕО
// =============================================================================

function showVideoModal(videoId, videoTitle, videoDescription) {
    const modal = document.getElementById('videoActionsModal');
    const titleEl = modal.querySelector('.video-title-display');
    const galleryBtn = modal.querySelector('.go-to-gallery');
    const stayBtn = modal.querySelector('.stay-here');
    const editTitleBtn = modal.querySelector('.edit-title');
    const editDescBtn = modal.querySelector('.edit-description');
    const deleteBtn = modal.querySelector('.delete-video');
    
    if (titleEl) {
        titleEl.textContent = videoTitle;
    }
    
    if (editTitleBtn) editTitleBtn.style.display = 'inline-flex';
    if (editDescBtn) editDescBtn.style.display = 'inline-flex';
    if (deleteBtn) deleteBtn.style.display = 'inline-flex';
    
    if (galleryBtn) {
        galleryBtn.addEventListener('click', () => {
            closeActionsModal();
            window.location.href = `/videos/${videoId}/`;
        });
    }
    
    if (stayBtn) {
        stayBtn.addEventListener('click', () => {
            closeActionsModal();
        });
    }
    
    if (editTitleBtn) {
        editTitleBtn.addEventListener('click', () => {
            showEditTitleForm(videoId, videoTitle);
        });
    }
    
    if (editDescBtn) {
        editDescBtn.addEventListener('click', () => {
            showEditDescriptionForm(videoId, videoDescription);
        });
    }
    
    if (deleteBtn) {
        deleteBtn.addEventListener('click', () => {
            closeActionsModal();
            deleteVideo(videoId, videoTitle);
        });
    }
    
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
}

function createActionsModal() {
    let modal = document.getElementById('videoActionsModal');
    
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'videoActionsModal';
        modal.className = 'video-actions-modal';
        modal.innerHTML = `
            <div class="video-actions-modal-overlay" onclick="closeActionsModal()"></div>
            <div class="video-actions-modal-content">
                <div class="video-actions-modal-header">
                    <h3>Действия с видео</h3>
                    <div class="video-title-display"></div>
                </div>
                <div class="video-actions-modal-body">
                    <div class="modal-actions">
                        <button type="button" class="modal-btn green go-to-gallery">
                            ▶️ Смотреть видео
                        </button>
                        <button type="button" class="modal-btn secondary stay-here">
                            📋 Остаться в содержании
                        </button>
                        <button type="button" class="modal-btn edit edit-title" style="display: none;">
                            ✏️ Редактировать название
                        </button>
                        <button type="button" class="modal-btn edit edit-description" style="display: none;">
                            📝 Редактировать описание
                        </button>
                        <button type="button" class="modal-btn delete delete-video" style="display: none;">
                            🗑️ Удалить видео
                        </button>
                    </div>
                    
                    <div class="edit-form" id="editTitleForm">
                        <div class="form-group">
                            <label for="newTitle">Новое название:</label>
                            <input type="text" id="newTitle" class="form-input" placeholder="Введите новое название">
                        </div>
                        <div class="form-actions">
                            <button type="button" class="btn" id="saveTitleBtn">💾 Сохранить</button>
                            <button type="button" class="btn secondary" onclick="hideEditForms()">❌ Отмена</button>
                        </div>
                    </div>
                    
                    <div class="edit-form" id="editDescForm">
                        <div class="form-group">
                            <label for="newDescription">Новое описание:</label>
                            <textarea id="newDescription" class="form-textarea" placeholder="Введите новое описание"></textarea>
                        </div>
                        <div class="form-actions">
                            <button type="button" class="btn" id="saveDescBtn">💾 Сохранить</button>
                            <button type="button" class="btn secondary" onclick="hideEditForms()">❌ Отмена</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    return modal;
}

function closeActionsModal() {
    const modal = document.getElementById('videoActionsModal');
    if (modal) {
        modal.classList.remove('open');
        document.body.style.overflow = '';
        hideEditForms();
    }
}

// =============================================================================
// ФОРМЫ РЕДАКТИРОВАНИЯ
// =============================================================================

function showEditTitleForm(videoId, currentTitle) {
    hideEditForms();
    
    const form = document.getElementById('editTitleForm');
    const input = document.getElementById('newTitle');
    const saveBtn = document.getElementById('saveTitleBtn');
    
    if (form && input && saveBtn) {
        input.value = currentTitle || '';
        form.classList.add('active');
        
        const newSaveBtn = saveBtn.cloneNode(true);
        saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);
        
        newSaveBtn.addEventListener('click', () => {
            const newTitle = input.value.trim();
            if (newTitle) {
                updateVideoTitle(videoId, newTitle);
            }
        });
    }
}

function showEditDescriptionForm(videoId, currentDescription) {
    hideEditForms();
    
    const form = document.getElementById('editDescForm');
    const textarea = document.getElementById('newDescription');
    const saveBtn = document.getElementById('saveDescBtn');
    
    if (form && textarea && saveBtn) {
        textarea.value = currentDescription || '';
        form.classList.add('active');
        
        const newSaveBtn = saveBtn.cloneNode(true);
        saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);
        
        newSaveBtn.addEventListener('click', () => {
            const newDescription = textarea.value.trim();
            updateVideoDescription(videoId, newDescription);
        });
    }
}

function hideEditForms() {
    const forms = document.querySelectorAll('.edit-form');
    forms.forEach(form => {
        form.classList.remove('active');
    });
}

// =============================================================================
// ОБНОВЛЕНИЕ ДАННЫХ
// =============================================================================

function updateVideoTitle(videoId, newTitle) {
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/videos/edit/${videoId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            field: 'title',
            value: newTitle
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            hideEditForms();
            showMessage(data.message || 'Название успешно обновлено', 'success');
            
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showMessage(data.error || 'Ошибка при обновлении', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Ошибка при обновлении', 'error');
    });
}

function updateVideoDescription(videoId, newDescription) {
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/videos/edit/${videoId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            field: 'description',
            value: newDescription
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            hideEditForms();
            showMessage(data.message || 'Описание успешно обновлено', 'success');
            
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showMessage(data.error || 'Ошибка при обновлении', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Ошибка при обновлении', 'error');
    });
}

// =============================================================================
// УДАЛЕНИЕ ВИДЕО
// =============================================================================

function deleteVideo(videoId, videoTitle) {
    showDeleteModal(videoId, videoTitle);
}

function createDeleteModal() {
    if (document.getElementById('deleteModal')) return;

    const modal = document.createElement('div');
    modal.id = 'deleteModal';
    modal.className = 'delete-modal';
    modal.innerHTML = `
        <div class="delete-modal-overlay" onclick="closeDeleteModal()"></div>
        <div class="delete-modal-content">
            <div class="delete-modal-header">
                <h3>🗑️ Подтверждение удаления</h3>
            </div>
            <div class="delete-modal-body">
                <p>Вы уверены, что хотите удалить это видео?</p>
                <p class="video-title" id="modalVideoTitle"></p>
            </div>
            <div class="delete-modal-footer">
                <button type="button" class="btn secondary" onclick="closeDeleteModal()">
                    ❌ Отмена
                </button>
                <button type="button" class="btn delete-confirm-btn" id="confirmDeleteBtn">
                    🗑️ Удалить
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
}

function showDeleteModal(videoId, videoTitle) {
    const modal = document.getElementById('deleteModal');
    const titleEl = document.getElementById('modalVideoTitle');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    
    if (modal && titleEl && confirmBtn) {
        titleEl.textContent = `"${videoTitle}"`;
        
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        
        newConfirmBtn.addEventListener('click', () => {
            confirmDeleteVideo(videoId);
        });
        
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
}

function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.classList.remove('open');
        document.body.style.overflow = '';
    }
}

function confirmDeleteVideo(videoId) {
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/videos/delete/${videoId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeDeleteModal();
            showMessage(data.message || 'Видео успешно удалено', 'success');
            
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            closeDeleteModal();
            showMessage(data.error || 'Ошибка при удалении', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        closeDeleteModal();
        showMessage('Ошибка при удалении', 'error');
    });
}

// =============================================================================
// УТИЛИТЫ
// =============================================================================

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function showMessage(text, type) {
    let messagesContainer = document.querySelector('.messages');
    if (!messagesContainer) {
        messagesContainer = document.createElement('div');
        messagesContainer.className = 'messages';
        const card = document.querySelector('.card');
        if (card) {
            card.insertBefore(messagesContainer, card.firstChild.nextSibling);
        }
    }
    
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.textContent = text;
    messagesContainer.appendChild(message);
    
    setTimeout(() => {
        if (message.parentNode) {
            message.remove();
        }
    }, 5000);
}