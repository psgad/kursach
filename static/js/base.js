function toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('overlay');
        sidebar.classList.toggle('open');
        overlay.classList.toggle('open');
    }


    function selectElement(id, data) {
        const select = document.getElementById(id);
        if (!select) return; // Проверка на существование элемента
        Array.from(select.options).forEach(option => {
            if (option.text === data) {
                select.value = option.value;
            }
        });
    }

    function filterGroups() {
        const input = document.getElementById('group-search').value.toLowerCase();
        const list = document.getElementById('group-list');
        list.innerHTML = '';

        groups.filter(group => group.toLowerCase().includes(input)).forEach(group => {
            const div = document.createElement('div');
            div.textContent = group;
            div.onclick = () => selectGroup(group);
            list.appendChild(div);
        });
    }

    function selectGroup(group) {
        document.getElementById('group-search').value = group;
        document.getElementById('group-list').innerHTML = '';

        fetch(`/student/lessons?data=${group}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Сеть не в порядке');
                }
                return response.json();
            })
            .then(data => {
                addSchedule(data);
            })
            .catch(error => {
                console.error("Ошибка", error);
            });
    }

    function timeOfIndex(index) {
        switch (index) {
            case '1': return '8:30 - 10:00';
            case '2': return '10:10 - 11:40';
            case '3': return '12:00 - 13:30';
            case '4': return '13:50 - 15:20';
            case '5': return '15:30 - 17:00';
            case '6': return '17:10 - 18:40';
            default: return '';
        }
    }

    function addSchedule(lessons) {
        const tablesContainer = document.getElementById('tables-container');
        tablesContainer.innerHTML = '';

        if (lessons) {
            const columnCount = 4;
            const maxCellWidths = [100, 150, 200, 200];

            for (let day_id in lessons) {
                const day = lessons[day_id];
                const dayTable = document.createElement('div');
                dayTable.classList.add('day-table');

                const title = document.createElement('h2');
                title.textContent = day['weekday'];
                dayTable.appendChild(title);

                const table = document.createElement('table');
                const thead = document.createElement('thead');
                thead.innerHTML = '<tr><th>Номер пары</th><th>Время проведения</th><th>Предмет</th><th>Преподаватель</th></tr>';
                table.appendChild(thead);

                const tbody = document.createElement('tbody');
                for (const key in day) {
                    if (key === "weekday") continue;
                    const value = day[key];
                    const row = document.createElement('tr');
                    row.innerHTML = `<td style="width: 20px">${value['lesson_number']}</td><td style="width: 20px">${timeOfIndex(value['lesson_number'])}</td><td style="width: 300px">${value['lesson_title']}</td><td>${value['lesson_teacher']}</td>`;
                    tbody.appendChild(row);
                }
                table.appendChild(tbody);
                dayTable.appendChild(table);
                tablesContainer.appendChild(dayTable);
            }
            tablesContainer.classList.add('show');
        }
    }

    function previewImage(event) {
        const file = event.target.files[0];
        const reader = new FileReader();
        reader.onload = function (e) {
            const img = document.querySelector('.photo-section img');
            img.src = e.target.result; // Устанавливаем источник изображения в выбранный файл
        }
        reader.readAsDataURL(file);
    }

    function toggleSubmenu(event) {
        const submenu = event.target.querySelector('ul');
        if (submenu) {
            const allSubmenus = document.querySelectorAll('.sidebar ul ul');
            allSubmenus.forEach(sub => {
                if (sub !== submenu) {
                    sub.style.display = 'none';
                }
            });

            submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
        }
    }

    function hideAllSubmenus() {
        const allSubmenus = document.querySelectorAll('.sidebar ul ul');
        allSubmenus.forEach(sub => {
            sub.style.display = 'none';
        });
    }
    try {
        const hamburger = document.getElementById('hamburger');
        hamburger.addEventListener('click', toggleSidebar);
    }
    catch { }

    try {
        const sidebarItems = document.querySelectorAll('.sidebar ul > li');
        sidebarItems.forEach(item => {
            item.addEventListener('click', toggleSubmenu);
        });
    }
    catch { }

    try {
        const overlay = document.getElementById('overlay');
        overlay.addEventListener('click', toggleSidebar);

    }
    catch { }

    try {
        const sidebar = document.getElementById('sidebar');
        sidebar.addEventListener('transitionend', () => {
            if (!sidebar.classList.contains('open')) {
                hideAllSubmenus();
            }
        });
    }
    catch { }

    const profileLink = document.getElementById('profile-link');
    const profileMenu = document.getElementById('profile-menu');

    function toggleProfileMenu() {
        profileMenu.style.display = profileMenu.style.display === 'block' ? 'none' : 'block';
    }
    try {
            profileLink.addEventListener('click', (event) => {
                event.preventDefault();
                toggleProfileMenu();
            });
    }
    catch{ }

    try {
        document.addEventListener('click', (event) => {
            if (!event.target.closest('.profile')) {
                profileMenu.style.display = 'none';
            }
        });
    }
    catch { }

    const newsSlider = document.getElementById('news-slider');
    let currentIndex = 0;

    function showNextNews() {
        currentIndex = (currentIndex + 1) % 4;
        newsSlider.style.transform = `translateX(-${currentIndex * 100}%)`;
    }

    try {
        setInterval(showNextNews, 3000);
    }
    catch { }

    try {
        const groups = [{% for group in groups %}'{{ group }}', {% endfor %}];


        window.addEventListener('load', () => {
            setTimeout(() => {
                document.getElementById('loading').style.display = 'none';
            }, 2000); // Задержка в 2 секунды
        });
    }
    catch { }
    try{
        document.addEventListener('DOMContentLoaded', function() {
                selectElement('group', '{{ user.user_group }}');
            });
    }
    catch{ }
