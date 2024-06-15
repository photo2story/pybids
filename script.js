document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('date');
    const bidwinSection = document.getElementById('bidwin-section');
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
                const bidwins = data.bidwins.filter(bid => bid.opengDt && bid.opengDt.split(' ')[0] === date);
                const bids = data.bids.filter(bid => bid.bidNtceDt && bid.bidNtceDt.split(' ')[0] === date);
                const prebids = data.prebids.filter(prebid => prebid.rcptDt && prebid.rcptDt.split(' ')[0] === date);

                displayData(bidwins, bidwinSection, 'bidNtceNm', 'opengDt', 'opengCorpInfo');
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
            const date = item[dateKey] ? item[dateKey].split(' ')[0] : ''; // Extract date only
            let extraInfo = extraKey ? `<br>낙찰자: ${item[extraKey]}` : '';
            task.innerHTML = `<span>${date} ${item[key]}${extraInfo}</span><input type="checkbox">`;
            container.appendChild(task);
        });
    }
});





