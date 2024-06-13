document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('date');
    const bidsTodaySection = document.getElementById('bids-today-section');
    const bidsSection = document.getElementById('bids-section');
    const prebidsSection = document.getElementById('prebids-section');

    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;

    loadAndDisplayData(today);

    dateInput.addEventListener('change', () => {
        const selectedDate = dateInput.value;
        loadAndDisplayData(selectedDate);
    });

    function loadAndDisplayData(date) {
        fetch('data.json')
            .then(response => response.json())
            .then(data => {
                console.log('Fetched data:', data); // 데이터 로드 확인 로그
                const bidsToday = data.bidwins.filter(bid => bid.opengDt && bid.opengDt.split(' ')[0] === date);
                const bids = data.bids.filter(bid => bid.bidNtceDt && bid.bidNtceDt.split(' ')[0] === date);
                const prebids = data.prebids.filter(prebid => prebid.rcptDt && prebid.rcptDt.split(' ')[0] === date);

                console.log('Bids Today:', bidsToday); // 필터링된 데이터 로그
                console.log('Bids:', bids); // 필터링된 데이터 로그
                console.log('Prebids:', prebids); // 필터링된 데이터 로그

                displayData(bidsToday, bidsTodaySection, 'bidNtceNm', 'opengDt', 'opengCorpInfo');
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






