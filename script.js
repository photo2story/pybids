// Script.js_ jQuery를 이용한 기능 구현

$(function() {
    const dateInput = $('#date');
    const bidwinSection = $('#bidwin-section');
    const bidsSection = $('#bids-section');
    const prebidsSection = $('#prebids-section');

    const today = new Date().toISOString().split('T')[0];
    dateInput.val(today);

    loadAndDisplayData(today);

    dateInput.on('change', function() {
        const selectedDate = $(this).val();
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
        container.empty();
        items.forEach(item => {
            const task = $('<div>').addClass('task').css('display', 'flex');

            const checkbox = $('<input>').attr('type', 'checkbox').css('marginRight', '10px').css('accentColor', 'yellow');

            checkbox.on('change', function() {
                if (checkbox.prop('checked')) {
                    // sendOK를 4로 설정하는 요청을 보냅니다.
                    $.ajax({
                        url: '/update_sendOK',
                        type: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify({
                            bidNtceNo: item['bidNtceNo'],
                            filePath: getFilePath(container)
                        }),
                        success: function(result) {
                            if (result.status === 'success') {
                                task.remove();
                            } else {
                                alert('Failed to update item');
                                checkbox.prop('checked', false);
                            }
                        },
                        error: function(error) {
                            console.error('Error updating item:', error);
                            alert('Failed to update item');
                            checkbox.prop('checked', false);
                        }
                    });
                }
            });

            const text = $('<span>').css('flex', '1').css('cursor', 'pointer').on('click', function() {
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

    function getFilePath(container) {
        if (container.is('#bids-section')) {
            return 'filtered_bids_data.csv';
        } else if (container.is('#prebids-section')) {
            return 'filtered_prebids_data.csv';
        } else if (container.is('#bidwin-section')) {
            return 'filtered_bidwin_data.csv';
        }
        return '';
    }
});
