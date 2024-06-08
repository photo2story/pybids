document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('date');
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
        console.log(`Loading data for date: ${date}`);
        fetch('data.json')
            .then(response => response.json())
            .then(data => {
                console.log('Data loaded:', data);
                const bids = data.bids.filter(bid => bid.bidNtceDt === date);
                const prebids = data.prebids.filter(prebid => prebid.rcptDt === date);
                console.log('Filtered bids:', bids);
                console.log('Filtered prebids:', prebids);

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



