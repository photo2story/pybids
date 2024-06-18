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
        console.log('Loading data for date:', date);

        fetch('filtered_bidwin_data.json')
            .then(response => response.json())
            .then(data => {
                console.log('filtered_bidwin_data.json loaded:', data);
                const bidwins = data.filter(item => item['opengDt'].split(' ')[0] === date);
                console.log('Filtered bidwin data:', bidwins);
                displayData(bidwins, bidwinSection, 'bidNtceNm', 'opengDt', 'opengCorpInfo', 'link');
            })
            .catch(error => console.error('Error loading bidwin data:', error));

        fetch('filtered_bids_data.json')
            .then(response => response.json())
            .then(data => {
                console.log('filtered_bids_data.json loaded:', data);
                const bids = data.filter(item => item['bidNtceDt'].split(' ')[0] === date);
                console.log('Filtered bid data:', bids);
                displayData(bids, bidsSection, 'bidNtceNm', 'bidNtceDt', null, 'link');
            })
            .catch(error => console.error('Error loading bid data:', error));

        fetch('filtered_prebids_data.json')
            .then(response => response.json())
            .then(data => {
                console.log('filtered_prebids_data.json loaded:', data);
                const prebids = data.filter(item => item['rcptDt'].split(' ')[0] === date);
                console.log('Filtered prebid data:', prebids);
                displayData(prebids, prebidsSection, 'prdctClsfcNoNm', 'rcptDt', null, 'link');
            })
            .catch(error => console.error('Error loading prebid data:', error));
    }

    function displayData(items, container, key, dateKey, extraKey = null, linkKey = null) {
        container.innerHTML = '';
        items.forEach(item => {
            const task = document.createElement('div');
            task.className = 'task';
            task.style.display = 'flex';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.style.marginRight = '10px';
            checkbox.style.accentColor = 'yellow';

            checkbox.addEventListener('change', () => {
                if (checkbox.checked) {
                    task.remove();
                    // GitHub Pages에서는 서버에 POST 요청을 할 수 없으므로, 로컬 스토리지 등을 활용해야 합니다.
                    // fetch('/delete', {
                    //     method: 'POST',
                    //     headers: {
                    //         'Content-Type': 'application/json'
                    //     },
                    //     body: JSON.stringify(item)
                    // }).then(response => {
                    //     if (!response.ok) {
                    //         console.error('Failed to delete item');
                    //     }
                    // }).catch(error => console.error('Error:', error));
                }
            });

            const text = document.createElement('span');
            text.style.flex = '1';
            text.style.cursor = 'pointer';
            text.onclick = () => {
                if (item[linkKey]) {
                    window.open(item[linkKey], '_blank');
                }
            };

            const date = item[dateKey] ? item[dateKey].split(' ')[0] : '';
            let extraInfo = extraKey ? `<br>낙찰자: ${item[extraKey]}` : '';
            text.innerHTML = `${date} ${item[key]}${extraInfo}`;

            task.appendChild(checkbox);
            task.appendChild(text);
            container.appendChild(task);
        });
        console.log('Displayed data:', items);
    }
});
