document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('date');
    const bidsSection = document.getElementById('bids-section');
    const prebidsSection = document.getElementById('prebids-section');

    // 현재 날짜를 yyyy-mm-dd 형식으로 포맷
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;

    // 페이지 로드 시 오늘 날짜의 데이터 로드
    loadAndDisplayData(today);

    dateInput.addEventListener('change', () => {
        const selectedDate = dateInput.value;
        loadAndDisplayData(selectedDate);
    });

    function loadAndDisplayData(date) {
        fetch('data.json')
            .then(response => response.json())
            .then(data => {
                const bids = data.bids.filter(bid => bid.bidNtceDt.startsWith(date));
                const prebids = data.prebids.filter(prebid => prebid.rcptDt.startsWith(date));

                displayData(bids, bidsSection, 'bidNtceNm');
                displayData(prebids, prebidsSection, 'prdctClsfcNoNm');
            })
            .catch(error => console.error('Error loading data:', error));
    }

    function displayData(items, container, key) {
        container.innerHTML = '';
        items.forEach(item => {
            const task = document.createElement('div');
            task.className = 'task';
            task.innerHTML = `<span>${item[key]}</span><input type="checkbox">`;
            container.appendChild(task);
        });
    }
});

// python export_json.py



