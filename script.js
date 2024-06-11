document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('date');
    const bidsTodaySection = document.getElementById('bids-today-section');
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
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Fetched data:', data);  // 데이터를 콘솔에 출력
                const bidsToday = data.bidwins.filter(bid => bid.rlOpengDt && bid.rlOpengDt.split(' ')[0] === date);
                const bids = data.bids.filter(bid => bid.bidNtceDt && bid.bidNtceDt.split(' ')[0] === date);
                const prebids = data.prebids.filter(prebid => prebid.rcptDt && prebid.rcptDt.split(' ')[0] === date);

                displayData(bidsToday, bidsTodaySection, 'bidNtceNm', 'rlOpengDt', 'bidwinnrNm');
                displayData(bids, bidsSection, 'bidNtceNm', 'bidNtceDt');
                displayData(prebids, prebidsSection, 'prdctClsfcNoNm', 'rcptDt');
            })
            .catch(error => console.error('Error loading data:', error));
    }

    function displayData(items, container, key, dateKey, extraKey = null) {
        container.innerHTML = '';
        items.forEach(item => {
            const task = document.createElement('div');
            task.className = 'task';
            const date = item[dateKey] ? item[dateKey].split(' ')[0] : ''; // 날짜만 추출, 날짜가 없을 경우 빈 문자열
            let extraInfo = extraKey ? `<br>낙찰자: ${item[extraKey]}` : '';
            task.innerHTML = `<span>${date} ${item[key]}${extraInfo}</span><input type="checkbox">`;
            container.appendChild(task);
        });
    }
});





