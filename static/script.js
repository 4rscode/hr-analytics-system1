document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('resume');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const uploadForm = document.getElementById('uploadForm');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');
    const resultsContainer = document.getElementById('resultsContainer');

    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.classList.add('drop-zone-active');
    }

    function unhighlight() {
        dropZone.classList.remove('drop-zone-active');
    }

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    fileInput.addEventListener('change', function(e) {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length) {
            const file = files[0];
            showFileInfo(file);
            fileInput.files = files;
        }
    }

    function showFileInfo(file) {
        fileName.textContent = `Выбран файл: ${file.name}`;
        fileInfo.style.display = 'flex';
    }

    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            showError('Пожалуйста, выберите файл');
            return;
        }

        const formData = new FormData();
        formData.append('resume', file);

        loadingIndicator.style.display = 'block';
        errorMessage.style.display = 'none';
        resultsContainer.style.display = 'none';
        
        fetch('/api/upload', {
                method: 'POST',
                body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка сети');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                displayResults(data);
            } else {
                showError(data.message || 'Произошла ошибка при анализе резюме');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            showError('Произошла ошибка при загрузке файла: ' + error.message);
        })
        .finally(() => {
            loadingIndicator.style.display = 'none';
        });
    });

    function displayResults(analysis) {
        if (!analysis) {
            showError('Ошибка: Нет данных для отображения');
            return;
        }

        resultsContainer.style.display = 'block';
        
        // Отображаем общий счет
        const overallScore = document.getElementById('overallScore');
        overallScore.textContent = analysis.overall_score && typeof analysis.overall_score.value === 'number' 
            ? `${analysis.overall_score.value.toFixed(1)}%` 
            : 'Н/Д';
        
        // Отображаем лучшую подходящую роль
        const bestFitRole = document.getElementById('bestFitRole');
        if (analysis.role_fit && analysis.role_fit.best_fit) {
            bestFitRole.textContent = `${formatRoleName(analysis.role_fit.best_fit.role)} (${analysis.role_fit.best_fit.score.toFixed(1)}%)`;
        } else {
            bestFitRole.textContent = 'Роль не определена';
        }
        
        // Отображаем все роли
        const allRoles = document.getElementById('allRoles');
        if (analysis.role_fit && analysis.role_fit.all_roles) {
            const roles = Object.entries(analysis.role_fit.all_roles)
                .map(([role, score]) => ({
                    role: role,
                    score: typeof score === 'number' ? score : 0
                }))
                .sort((a, b) => b.score - a.score);

            allRoles.innerHTML = roles
                .map(({role, score}) => `<div>${formatRoleName(role)}: ${score.toFixed(1)}%</div>`)
                .join('');
        } else {
            allRoles.innerHTML = '<div>Нет данных по ролям</div>';
        }
        
        // Отображаем детали
        displayDetails(analysis.details || {});
        
        // Отображаем рекомендации
        displayRecommendations(analysis.recommendations || {});
    }

    function formatRoleName(role) {
        const roleNames = {
            'data_scientist': 'Data Scientist',
            'data_engineer': 'Инженер данных',
            'technical_analyst': 'Технический аналитик',
            'ai_manager': 'AI менеджер',
            'ml_engineer': 'ML инженер',
            'data_architect': 'Архитектор данных',
            'business_intelligence_analyst': 'BI аналитик',
            'research_scientist': 'Научный сотрудник'
        };
        return roleNames[role] || role;
    }

    function displayDetails(details) {
        // Образование
        const educationScore = document.getElementById('educationScore');
        educationScore.textContent = details.education && typeof details.education.score === 'number'
            ? `${details.education.score.toFixed(1)}%`
            : 'Н/Д';
        
        // Опыт
        const experienceScore = document.getElementById('experienceScore');
        experienceScore.textContent = details.experience && typeof details.experience.score === 'number'
            ? `${details.experience.score.toFixed(1)}%`
            : 'Н/Д';
        
        // Навыки
        const skillsScore = document.getElementById('skillsScore');
        skillsScore.textContent = details.skills && typeof details.skills.score === 'number'
            ? `${details.skills.score.toFixed(1)}%`
            : 'Н/Д';
        
        // Языки
        const languagesScore = document.getElementById('languagesScore');
        languagesScore.textContent = details.languages && typeof details.languages.score === 'number'
            ? `${details.languages.score.toFixed(1)}%`
            : 'Н/Д';
    }

    function displayRecommendations(recommendations) {
        // Сильные стороны
        const strengthsList = document.getElementById('strengthsList');
        strengthsList.innerHTML = recommendations.strengths && recommendations.strengths.length
            ? recommendations.strengths.map(strength => `<li>${strength}</li>`).join('')
            : '<li>Нет данных</li>';
        
        // Области для улучшения
        const weaknessesList = document.getElementById('weaknessesList');
        let weaknessesHtml = '';
        
        // Группируем рекомендации по категориям
        const categories = {
            'education': 'Образование',
            'experience': 'Опыт работы',
            'skills': 'Навыки',
            'languages': 'Языки'
        };

        Object.entries(categories).forEach(([category, title]) => {
            if (recommendations[category] && recommendations[category].length > 0) {
                weaknessesHtml += `
                    <li class="recommendation-category">
                        <strong>${title}:</strong>
                        <ul>
                            ${recommendations[category].map(item => `<li>${item}</li>`).join('')}
                        </ul>
                    </li>
                `;
            }
        });

        weaknessesList.innerHTML = weaknessesHtml || '<li>Нет данных</li>';
        
        // Рекомендуемые курсы
        const improvementsList = document.getElementById('improvementsList');
        if (recommendations.course_recommendations && recommendations.course_recommendations.length > 0) {
            const coursesHtml = recommendations.course_recommendations.map(course => `
                <li class="course-recommendation">
                    <div class="course-header">
                        <strong>${course.name}</strong>
                    </div>
                    <div class="course-details">
                        <p><span class="detail-label">Платформа:</span> ${course.platform}</p>
                        <p><span class="detail-label">Длительность:</span> ${course.duration}</p>
                        <p><span class="detail-label">Уровень:</span> ${course.level}</p>
                        <a href="${course.url}" target="_blank" rel="noopener noreferrer" class="course-link">
                            Перейти к курсу
                        </a>
                    </div>
                </li>
            `).join('');
            improvementsList.innerHTML = coursesHtml;
        } else {
            improvementsList.innerHTML = '<li>Нет рекомендуемых курсов</li>';
        }
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        loadingIndicator.style.display = 'none';
        resultsContainer.style.display = 'none';
    }
});
