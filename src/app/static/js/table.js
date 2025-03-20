// Mapping of table IDs to the columns used for searching
const tables = {
    'container-table':  [0],       // name
    'image-table':      [0],       // name
    'volume-table':     [0],       // name
    'user-table':       [0],       // username
    'roles-table':      [0],       // name
    'network-table':    [0, 2],    // name, subnet
    'process-table':    [0, 1, 7]  // UID, PID, CMD
};

function search(searchValue, currentTable) {
    if (currentTable !== null) {
        const rows = document.querySelectorAll(`#${currentTable} tbody tr`);
        let visibleRowCount = 0;

        rows.forEach(row => {
            const columnsToSearch = tables[currentTable];
            let match = false;

            columnsToSearch.forEach(colIndex => {
                const cellValue = row.cells[colIndex].textContent.toLowerCase();
                if (cellValue.includes(searchValue)) {
                    match = true;
                }
            });

            if (match) {
                row.style.display = '';
                visibleRowCount++;
            } else {
                row.style.display = 'none';
            }
        });

        // Handle the no rows found case
        let noRowsMessage = document.getElementById('no-rows-message');
        if (visibleRowCount === 0) {
            if (!noRowsMessage) {
                noRowsMessage = document.createElement('tr');
                noRowsMessage.id = 'no-rows-message';
                noRowsMessage.innerHTML = `<p>No matching records found</p>`;
                document.querySelector(`.content-box`).appendChild(noRowsMessage);
            }
            noRowsMessage.style.display = '';
        } else if (noRowsMessage) {
            noRowsMessage.style.display = 'none';
        }
    }
}

function sortTable(tableId) {
    const table = document.getElementById(tableId);
    const headers = table.querySelectorAll('th[data-sort]');
    
    headers.forEach(th => {
        th.addEventListener('click', function() {
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const index = Array.from(th.parentNode.children).indexOf(th);
            const isAscending = th.classList.contains('ascending');

            // Remove sorting indicators from all columns
            headers.forEach(otherTh => {
                otherTh.classList.remove('ascending', 'descending');
            });

            // Toggle ascending/descending classes on the clicked column
            if (isAscending) {
                th.classList.remove('ascending');
                th.classList.add('descending');
            } else {
                th.classList.remove('descending');
                th.classList.add('ascending');
            }

            // Determine the new sort direction
            const sortAscending = th.classList.contains('ascending');

            // Sort rows based on the selected column
            rows.sort((a, b) => {
                const cellA = a.children[index].textContent.trim();
                const cellB = b.children[index].textContent.trim();

                if (!isNaN(cellA) && !isNaN(cellB)) {
                    return sortAscending ? cellA - cellB : cellB - cellA;
                }

                return sortAscending ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
            });

            // Re-append rows to the tbody in the new order
            rows.forEach(row => tbody.appendChild(row));
        });
    });
}

const searchField = document.getElementById('search');

if (searchField != null) {
    let currentTable = null;

    for (const tableId in tables) {
        const tableElement = document.getElementById(tableId);
        if (tableElement !== null) {
            currentTable = tableId;
            break;
        }
    }

    if (currentTable !== null) {
        const lastSearchValue = localStorage.getItem(`lastSearchValue_${currentTable}`);
        if (lastSearchValue) {
            searchField.value = lastSearchValue;
            setTimeout(() => {
                search(lastSearchValue, currentTable);
            }, 300);
        }
    }
    
    searchField.addEventListener('input', function() {
        const searchValue = this.value.toLowerCase();
        
        search(searchValue, currentTable);

        localStorage.setItem(`lastSearchValue_${currentTable}`, searchValue);
    });
}

for (const tableId in tables) {
    const tableElement = document.getElementById(tableId);
    if (tableElement !== null) {
        sortTable(tableId);
    }
}

const resresh_btn = document.getElementById('refresh-page-btn');
if (resresh_btn != null) {
    resresh_btn.addEventListener('click', function() {
        location.reload();
    });
}