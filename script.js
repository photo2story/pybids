document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('date');
    const bidsSection = document.getElementById('bids-section');
    const prebidsSection = document.getElementById('prebids-section');

    // 현재 날짜를 yyyy-mm-dd 형식으로 포맷
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;

    // 페이지 로드 시 오늘 날짜의 데이터 로드
    loadAndDisplayData(today);

    // 날짜 변경 시 선택한 날짜의 데이터 로드
    dateInput.addEventListener('change', () => {
        const selectedDate = dateInput.value;
        loadAndDisplayData(selectedDate);
    });

    function loadAndDisplayData(date) {
        console.log(`Loading data for date: ${date}`); // 디버깅 로그
        fetch('data.json')
            .then(response => response.json())
            .then(data => {
                console.log('Data loaded:', data); // 디버깅 로그
                const bids = data.bids.filter(bid => bid.bidNtceDt === date);
                const prebids = data.prebids.filter(prebid => prebid.rcptDt === date);
                console.log('Filtered bids:', bids); // 디버깅 로그
                console.log('Filtered prebids:', prebids); // 디버깅 로그

                displayData(bids, bidsSection, 'bidNtceNm');
                displayData(prebids, prebidsSection, 'prdctClsfcNoNm');
            })
            .catch(error => console.error('Error loading data:', error));
    }

    function displayData(items, container, key) {
        container.innerHTML = '';
        if (items.length === 0) {
            container.innerHTML = '<p>해당 날짜에 공고가 없습니다.</p>';
        } else {
            items.forEach(item => {
                const task = document.createElement('div');
                task.className = 'task';
                task.innerHTML = `<span>${item[key]}</span><input type="checkbox">`;
                container.appendChild(task);
            });
        }
    }
});



