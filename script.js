$(document).ready(() => {
    const dateInput = $('#date');
    const bidwinSection = $('#bidwin-section');
    const bidsSection = $('#bids-section');
    const prebidsSection = $('#prebids-section');

    const today = new Date().toISOString().split('T')[0];
    dateInput.val(today);

    loadAndDisplayData(today);

    dateInput.on('change', () => {
        const selectedDate = dateInput.val();
        loadAndDisplayData(selectedDate);
    });

    function loadAndDisplayData(date) {
        console.log('Loading data for date:', date);

        fetch('filtered_bidwin_data.csv')
            .then(response => response.text())
            .then(csvText => {
                console.log('filtered_bidwin_data.csv loaded:', csvText);
                const data = parseCSV(csvText);
                console.log('Parsed bidwin data:', data);
                const bidwins = data.filter(item => item['opengDt'].split(' ')[0] === date);
                console.log('Filtered bidwin data:', bidwins);
                displayData(bidwins, bidwinSection, 'bidNtceNm', 'opengDt', 'opengCorpInfo', 'link');
            })
            .catch(error => console.error('Error loading bidwin data:', error));

        fetch('filtered_bids_data.csv')
            .then(response => response.text())
            .then(csvText => {
                console.log('filtered_bids_data.csv loaded:', csvText);
                const data = parseCSV(csvText);
                console.log('Parsed bid data:', data);
                const bids = data.filter(item => item['bidNtceDt'].split(' ')[0] === date);
                console.log('Filtered bid data:', bids);
                displayData(bids, bidsSection, 'bidNtceNm', 'bidNtceDt', null, 'link');
            })
            .catch(error => console.error('Error loading bid data:', error));

        fetch('filtered_prebids_data.csv')
            .then(response => response.text())
            .then(csvText => {
                console.log('filtered_prebids_data.csv loaded:', csvText);
                const data = parseCSV(csvText);
                console.log('Parsed prebid data:', data);
                const prebids = data.filter(item => item['rcptDt'].split(' ')[0] === date);
                console.log('Filtered prebid data:', prebids);
                displayData(prebids, prebidsSection, 'prdctClsfcNoNm', 'rcptDt', null, 'link');
            })
            .catch(error => console.error('Error loading prebid data:', error));
    }

    function parseCSV(csvText) {
        const lines = csvText.split('\n');
        const headers = lines[0].split(',');
        const items = lines.slice(1).filter(line => line.trim() !== '').map(line => {
            const values = line.split(',');
            let item = {};
            headers.forEach((header, index) => {
                item[header.trim()] = values[index] ? values[index].trim() : '';
            });
            return item;
        });
        console.log('Parsed CSV:', items);
        return items;
    }

    function displayData(items, container, key, dateKey, extraKey = null, linkKey = null) {
        container.html('');
        items.forEach(item => {
            const task = $('<div>').addClass('task').css('display', 'flex');

            const checkbox = $('<input>').attr('type', 'checkbox').css('marginRight', '10px').css('accentColor', 'yellow');

            checkbox.on('change', () => {
                if (checkbox.prop('checked')) {
                    // sendOK를 4로 설정하는 요청을 보냅니다.
                    $.ajax({
                        url: 'http://localhost:8080/update_sendOK',  // 로컬 서버에서 POST 요청을 처리
                        method: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify({
                            bidNtceNo: item['bidNtceNo'],
                            filePathKey: getFilePathKey(container)
                        }),
                        success: function(response) {
                            if (response.status === 'success') {
                                // 성공적으로 업데이트된 경우, 디스코드 메시지 전송
                                sendDiscordMessage(item['bidNtceNo']);
                                task.remove();
                            } else {
                                alert('Failed to update item');
                                checkbox.prop('checked', false);
                            }
                        },
                        error: function() {
                            alert('Failed to update item');
                            checkbox.prop('checked', false);
                        }
                    });
                }
            });

            const text = $('<span>').css('flex', '1').css('cursor', 'pointer');
            text.on('click', () => {
                if (item[linkKey]) {
                    window.open(item[linkKey], '_blank');
                }
            });

            const date = item[dateKey] ? item[dateKey].split(' ')[0] : '';
            let extraInfo = extraKey ? `<br>낙찰자: ${item[extraKey]}` : '';
            text.html(`${date} ${item[key]}${extraInfo}`);

            task.append(checkbox).append(text);
            container.append(task);
        });
        console.log('Displayed data:', items);
    }

    function sendDiscordMessage(bidNo) {
        $.ajax({
            url: 'http://localhost:8080/send_discord_message',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ bidNtceNo: bidNo }),
            success: function(response) {
                if (response.status !== 'success') {
                    console.error('Failed to send Discord message:', response.message);
                }
            },
            error: function() {
                console.error('Failed to send Discord message');
            }
        });
    }

    function getFilePathKey(container) {
        if (container.attr('id') === 'bids-section') {
            return 'bids';
        } else if (container.attr('id') === 'prebids-section') {
            return 'prebids';
        } else if (container.attr('id') === 'bidwin-section') {
            return 'bidwin';
        }
        return '';
    }
});
